from typing import Callable, Any, List, Dict, Optional, cast
from .helpers import NamespaceCollection, RuntimePythonProps, JobProps, InstancePickleWrapper
import inspect, re, sys, types
from .jobs import ModelbitJobResult, stripJobDecorators
from .utils import unindent, convertLambdaToDef
from .source_generation import makeSourceFile


def getRuntimePythonProps(func: Optional[Callable[..., Any]], sourceOverride: Optional[str] = None):
  props: RuntimePythonProps = RuntimePythonProps()
  if not inspect.isfunction(func):
    raise Exception('The deploy function parameter does not appear to be a function.')
  else:
    props.name = func.__name__
    props.source = sourceOverride if sourceOverride is not None else getFuncSource(func)
    props.argNames = getFuncArgNames(func)
    props.argTypes = annotationsToTypeStr(func.__annotations__)
    nsCollection = NamespaceCollection()
    collectNamespaceDeps(func, nsCollection)
    props.namespaceFunctions = nsCollection.functions
    props.namespaceVars = nsCollection.vars
    props.namespaceVarsDesc = _strValues(nsCollection.vars)
    props.namespaceImports = nsCollection.imports
    props.namespaceFroms = nsCollection.froms
    props.namespaceModules = list(set(nsCollection.allModules))
    props.customInitCode = nsCollection.customInitCode
    props.extraDataFiles = nsCollection.extraDataFiles
    props.extraSourceFiles = nsCollection.extraSourceFiles
    props.jobs = nsCollection.jobs
    props.userClasses = list(nsCollection.userClasses.values())

    # Add modules from jobs to inference code so warnings fire if job includes extra packages
    for j in props.jobs:
      if j.rtProps.namespaceModules is not None:
        for nMod in j.rtProps.namespaceModules:
          if nMod not in props.namespaceModules:
            props.namespaceModules.append(nMod)
  return props


def getFuncSource(func: Callable[..., Any]):
  if not inspect.isfunction(func):
    return None
  return stripJobDecorators(unindent(inspect.getsource(func)))


def getClassSource(cls: type):
  try:
    from IPython.core.magics.code import extract_symbols  # type: ignore
  except:
    return inspect.getsource(cls)

  originalGetfile = inspect.getfile

  # from https://stackoverflow.com/questions/51566497/getting-the-source-of-an-object-defined-in-a-jupyter-notebook
  def getfile(obj: Any):
    if not inspect.isclass(obj):
      return originalGetfile(obj)

    # Lookup by parent module (as in current inspect)
    if hasattr(obj, '__module__'):
      obj_ = sys.modules.get(obj.__module__)
      if obj_ is not None and hasattr(obj_, '__file__'):
        return obj_.__file__

    # If parent module is __main__, lookup by methods (NEW)
    for _, member in inspect.getmembers(obj):
      if inspect.isfunction(member) and obj.__qualname__ + '.' + member.__name__ == member.__qualname__:
        return inspect.getfile(member)
    else:
      raise TypeError('Source for {!r} not found'.format(obj))

  inspect.getfile = getfile  # type: ignore
  cellCode = "".join(inspect.linecache.getlines(getfile(cls)))  # type: ignore
  classCode = cast(str, extract_symbols(cellCode, cls.__name__)[0][0])
  inspect.getfile = originalGetfile
  return classCode


def getFuncArgNames(func: Optional[Callable[..., Any]]):
  noArgs: List[str] = []
  if func is None:
    return noArgs
  argSpec = inspect.getfullargspec(func)
  if argSpec.varargs:
    return ['...']
  if argSpec.args:
    return argSpec.args
  return noArgs


def annotationsToTypeStr(annotations: Dict[str, Any]):
  annoStrs: Dict[str, str] = {}
  for name, tClass in annotations.items():
    try:
      if tClass == Any:
        annoStrs[name] = "Any"
      else:
        annoStrs[name] = tClass.__name__
    except:
      pass
  return annoStrs


def _strValues(args: Dict[str, Any]):
  newDict: Dict[str, str] = {}
  for k, v in args.items():
    strVal = re.sub(r'\s+', " ", str(v))
    if type(v) is bytes:
      strVal = "Binary data"
    elif _isMainModule(v) and hasattr(v, "__class__"):
      strVal = f"Instance of {v.__class__.__name__}"
    elif len(strVal) > 200:
      strVal = strVal[0:200] + "..."
    newDict[k] = strVal
  return newDict


def collectNamespaceDeps(func: Callable[..., Any], collection: NamespaceCollection):
  if not inspect.isfunction(func):
    return collection
  _collectArgTypes(func, collection)
  globalsDict = func.__globals__
  allNames = _extractAllNames(func)
  for maybeFuncVarName in allNames:
    if maybeFuncVarName in globalsDict:
      maybeFuncVar = globalsDict[maybeFuncVarName]
      if inspect.isfunction(maybeFuncVar) and maybeFuncVar == func:
        continue
      if type(maybeFuncVar) is ModelbitJobResult:
        jr = maybeFuncVar
        collection.jobs.append(
            JobProps(name=jr.mb_func.__name__,
                     outVar=maybeFuncVarName,
                     rtProps=getRuntimePythonProps(jr.mb_func),
                     schedule=jr.mb_schedule,
                     redeployOnSuccess=jr.mb_redeployOnSuccess,
                     emailOnFailure=jr.mb_emailOnFailure,
                     refreshDatasets=jr.mb_refreshDatasets,
                     timeoutMinutes=jr.mb_timeoutMinutes,
                     size=jr.mb_size))
        maybeFuncVar = jr.mb_obj
      if "__module__" in dir(maybeFuncVar):
        if _isMainModuleFunction(maybeFuncVar):  # the user's functions
          _collectFunction(maybeFuncVar, collection)
        elif _isMainModuleClassDef(maybeFuncVar):
          maybeFuncVar = cast(type, maybeFuncVar)
          _collectClassDefDeps(maybeFuncVar, globalsDict, collection)
        else:  # functions imported by the user from elsewhere
          if collectedSpecialObj(maybeFuncVar, maybeFuncVarName, collection):
            pass
          elif inspect.isclass(maybeFuncVar):
            collection.froms[maybeFuncVarName] = maybeFuncVar.__module__  #
            collection.allModules.append(maybeFuncVar.__module__)
          elif _isMainModuleClassInstance(maybeFuncVar):
            _collectClassDefDeps(maybeFuncVar.__class__, globalsDict, collection)
            collection.vars[maybeFuncVarName] = InstancePickleWrapper(maybeFuncVar)
          elif isinstance(maybeFuncVar, object) and "sklearn.pipeline" in f"{type(maybeFuncVar)}":
            collectPipelineModules(maybeFuncVar, maybeFuncVarName, collection)
          elif isinstance(maybeFuncVar, object) and type(maybeFuncVar) != types.FunctionType:
            collection.froms[maybeFuncVar.__class__.__name__] = maybeFuncVar.__module__
            collection.allModules.append(maybeFuncVar.__module__)
            collection.vars[maybeFuncVarName] = maybeFuncVar
          elif inspect.isfunction(maybeFuncVar):
            collection.froms[maybeFuncVarName] = maybeFuncVar.__module__  #
            collection.allModules.append(maybeFuncVar.__module__)
          else:
            raise Exception(f"Unknown object type: {maybeFuncVar}")
      elif str(maybeFuncVar).startswith('<module'):
        collection.imports[maybeFuncVarName] = maybeFuncVar.__name__
        collection.allModules.append(maybeFuncVar.__name__)
      elif inspect.isclass(maybeFuncVar):
        collection.froms[maybeFuncVarName] = maybeFuncVar.__module__  #
        collection.allModules.append(maybeFuncVar.__module__)
      else:
        collection.vars[maybeFuncVarName] = maybeFuncVar


def _collectArgTypes(func: Callable[..., Any], collection: NamespaceCollection):
  try:
    import ast

    def parseAstNameToId(astName: Any):
      if hasattr(astName, "attr"):
        return astName.value.id
      else:
        return astName.id

    def collectModName(modName: str):
      if modName in func.__globals__:
        gMod = func.__globals__[modName]
        if hasattr(gMod, "__module__"):
          collection.froms[modName] = gMod.__module__
        else:
          collection.imports[modName] = gMod.__name__
        if hasattr(func.__globals__[modName], "__name__"):
          collection.allModules.append(func.__globals__[modName].__name__)

    sigAst = ast.parse(unindent(inspect.getsource(func))).body[0]  # type: ignore

    for a in sigAst.args.args:  # type: ignore
      if a.annotation is None:  # type: ignore
        continue
      collectModName(parseAstNameToId(a.annotation))  # type: ignore
    if sigAst.returns is not None:  # type: ignore
      collectModName(parseAstNameToId(sigAst.returns))  # type: ignore
  except Exception as err:
    strErr = f"{err}"
    if (strErr != "could not get source code" and func.__name__ != "<lambda>"):
      print(f"Warning: failed parsing type annotations: {func} {err}")


def _collectSuperclassType(clsName: str, clsSource: str, funcGlobals: Dict[str, Any],
                           collection: NamespaceCollection):
  try:
    import ast

    def parseAstNameToId(astName: Any):
      if hasattr(astName, "attr"):
        return astName.value.id
      else:
        return astName.id

    def collectModName(modName: str):
      if modName in funcGlobals:
        gMod = funcGlobals[modName]
        if hasattr(gMod, "__module__"):
          if gMod.__module__ != "__main__":
            collection.froms[modName] = gMod.__module__
        else:
          collection.imports[modName] = gMod.__name__
        collection.allModules.append(funcGlobals[modName].__name__)

    clsDef = cast(Any, ast.parse((clsSource)).body[0])  # type: ignore
    bases = cast(List[Any], clsDef.bases)
    if len(bases) == 0:
      return
    collectModName(parseAstNameToId(bases[0]))
  except Exception as err:
    print(f"Warning: failed superclasses for {clsName}: {err}")


def _extractAllNames(func: Callable[..., Any]):
  code = func.__code__
  return list(code.co_names) + list(code.co_freevars) + _extractListCompNames(func)


def _extractListCompNames(func: Callable[..., Any]):
  names: List[str] = []
  for const in func.__code__.co_consts:
    if hasattr(const, "co_names"):
      for name in list(const.co_names):
        names.append(name)
  return names


def _collectFunction(func: Callable[..., Any], collection: NamespaceCollection):
  argNames = list(func.__code__.co_varnames or [])
  funcSig = f"{func.__name__}({', '.join(argNames)})"
  if funcSig not in collection.functions:
    collection.functions[funcSig] = inspect.getsource(func)
    collectNamespaceDeps(func, collection)


def _isMainModule(obj: Any) -> bool:
  return hasattr(obj, "__module__") and obj.__module__ == "__main__"


def _isMainModuleFunction(func: Any) -> bool:
  return inspect.isfunction(func) and _isMainModule(func)


def _isMainModuleClassDef(cls: Any) -> bool:
  return inspect.isclass(cls) and _isMainModule(cls)


def _isMainModuleClassInstance(inst: Any) -> bool:
  return isinstance(inst, object) and hasattr(inst, "__class__") and _isMainModuleClassDef(inst.__class__)


def _collectClassDefDeps(cls: type, funcGlobals: Dict[str, Any], collection: NamespaceCollection):
  firstAncestor = [c for c in cls.__mro__ if not _isMainModule(c)][0]
  for superCls in cls.__mro__:
    if _isMainModule(superCls) and superCls != cls:
      _collectClassDefDeps(superCls, funcGlobals, collection)
  classSrc = getClassSource(cls)
  collection.userClasses[cls.__name__] = classSrc
  _collectSuperclassType(cls.__name__, classSrc, funcGlobals, collection)
  ancestorAttrs = [a for a in dir(firstAncestor) if a != "__init__"]
  for name in dir(cls):
    if name in ancestorAttrs or (name.startswith("__") and name != "__init__"):
      continue
    obj = getattr(cls, name)
    if hasattr(obj, "__module__") and cls.__module__ != obj.__module__:
      continue  # from parent, ignore
    if inspect.isfunction(obj):
      collectNamespaceDeps(obj, collection)


def collectedSpecialObj(obj: Any, name: str, collection: NamespaceCollection) -> bool:
  if _inTypeStr("_FastText", obj):
    _collectFastText(obj, name, collection)
    return True
  return False


def savedSpecialObj(obj: Any, filepath: str):
  if _inTypeStr("_FastText", obj):
    obj.save_model(filepath)
    return True
  else:
    return False


def collectPipelineModules(obj: Any, name: str, collection: NamespaceCollection):
  import copy
  pipeline = copy.deepcopy(obj)
  collection.froms[pipeline.__class__.__name__] = pipeline.__module__
  collection.allModules.append(pipeline.__module__)
  collection.vars[name] = pipeline
  for step in pipeline.steps:
    pipelineObj = step[1]
    if not hasattr(pipelineObj, "__class__") or not hasattr(pipelineObj, "__module__"):
      continue
    collection.froms[pipelineObj.__class__.__name__] = pipelineObj.__module__
    collection.allModules.append(pipelineObj.__module__)
    if pipelineObj.__class__.__name__ == "FunctionTransformer" and hasattr(pipelineObj, "func"):
      libDir = "lib"
      sourceOverride = None
      if pipelineObj.func.__name__ == "<lambda>":  # FYI: modifying pipeline
        pipelineObj.func, sourceOverride = convertLambdaToDef(pipelineObj.func, "lambda_func")
      helperProps = getRuntimePythonProps(pipelineObj.func, sourceOverride=sourceOverride)
      helperName = pipelineObj.func.__name__
      helperFile = makeSourceFile(helperProps, f"{libDir}/{helperName}", isHelper=True)
      helperModule = _makeModule(f"{libDir}.{helperName}", helperFile.contents)
      _makeModule(libDir, "")
      pipelineObj.func = helperModule.__dict__[pipelineObj.func.__name__]  # FYI: modifying pipeline
      collection.extraSourceFiles[helperFile.name] = helperFile.contents


def _makeModule(name: str, source: str):
  mod = types.ModuleType(name)
  exec(source, mod.__dict__)
  sys.modules[mod.__name__] = mod
  return mod


def _inTypeStr(name: str, obj: Any) -> bool:
  return name in f"{type(obj)}"


def _collectFastText(obj: Any, name: str, collection: NamespaceCollection):
  import tempfile, os
  tmpFilePath = os.path.join(tempfile.gettempdir(), "tmp.pkl")
  assert savedSpecialObj(obj, tmpFilePath)
  with open(tmpFilePath, "rb") as f:
    collection.extraDataFiles[name] = (obj, f.read())
  collection.customInitCode.append(f"""
with open('data/{name}.pkl') as f:
  pass # ensure hydration
{name} = fasttext.load_model('data/{name}.pkl')
  """.strip())
  collection.imports["fasttext"] = "fasttext"
  collection.allModules.append("fasttext")
