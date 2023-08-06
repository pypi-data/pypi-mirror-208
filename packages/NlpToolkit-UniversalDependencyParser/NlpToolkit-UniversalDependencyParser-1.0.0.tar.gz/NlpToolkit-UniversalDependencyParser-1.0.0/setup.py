from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='NlpToolkit-UniversalDependencyParser',
    version='1.0.0',
    packages=['Parser', 'Parser.TransitionBasedParser'],
    url='https://github.com/StarlangSoftware/UniversalDependencyParser-Py',
    license='',
    author='olcaytaner',
    author_email='olcay.yildiz@ozyegin.edu.tr',
    description='Universal Dependency Parsing',
    install_requires=['NlpToolkit-Classification', 'NlpToolkit-DependencyParser'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
