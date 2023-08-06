from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["Parser/TransitionBasedParser/*.pyx"],
                          compiler_directives={'language_level': "3"}),
    name='NlpToolkit-UniversalDependencyParser-Cy',
    version='1.0.0',
    packages=['Parser', 'Parser.TransitionBasedParser'],
    package_data={'Parser.TransitionBasedParser': ['*.pxd', '*.pyx', '*.c', '*.py']},
    url='https://github.com/StarlangSoftware/UniversalDependencyParser-Cy',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Dependency Parsing library',
    install_requires=['NlpToolkit-Classification-Cy', 'NlpToolkit-DependencyParser-Cy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
