import setuptools

from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    
    long_description = fh.read()


setuptools.setup(
    name="qsolve",
    version="0.3.1",
    url = "https://github.com/jfmennemann/qsolve",
    author="Jan-Frederik Mennemann",
    author_email="jfmennemann@gmx.de",
    description="Numerical framework for the simulation and optimization of ultracold atom experiments",
    # long_description=read('README.md'),
    long_description=long_description,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[]
    # classifiers=[
    #     'Programming Language :: Python',
    #     'Programming Language :: Python :: 3',
    #     'Programming Language :: Python :: 3.10',
    # ],
    # package_data={'': ['/qsolve/qsolve/core/*.pyc']},
    # license="MIT",
    # keywords="ultracold atoms, classical fields simulations, Gross-Pitaevskii equation, thermal state sampling, time of flight"
)

