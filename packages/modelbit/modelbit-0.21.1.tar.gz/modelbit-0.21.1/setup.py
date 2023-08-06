from setuptools import find_packages, setup  # type: ignore

with open("README.md", "r") as fh:
  long_description = fh.read()

with open("requirements.txt", "r") as fh:
  required_packages = fh.read().strip().split("\n")

setup(
    name='modelbit',
    description='Python package to connect Python notebooks to Modelbit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.modelbit.com',
    author='Modelbit',
    author_email='tom@modelbit.com',
    license='MIT',
    data_files=[('', ['requirements.txt'])],
    packages=find_packages(),
    package_data={"modelbit": ["*.pyi", "*.png", "templates/*.j2"]},
    entry_points={'console_scripts': ['modelbit=modelbit.cli:main']},
    # Note: Keep these deps in sync with snowpark config
    install_requires=required_packages,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft',
        'Programming Language :: Python :: 3',
    ])
