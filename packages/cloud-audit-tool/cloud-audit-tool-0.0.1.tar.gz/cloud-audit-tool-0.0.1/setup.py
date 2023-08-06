from setuptools import find_packages
import setuptools
import os

with open("README_PIP.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt","r") as req:
    required_packages = req.read().splitlines()

__version__ = '0.0.1'
__author__='Vishal, Koushik, Sudharshan, Vikneshwar, Bhanuja, Ajay'
__maintainer_email__ = 'vishalrv1904@gmail.com , bhanuja497@gmail.com'

setuptools.setup(
    name="cloud-audit-tool",                
    version=__version__,                        
    author=__author__,  
    maintainer_email=__maintainer_email__,
    license= 'MIT',              
    description="AWS Cloud Audit Tool",
    long_description=long_description,     
    long_description_content_type="text/markdown",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        'common': ['templates/*.html'],
    },
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'cloud-audit-tool=main:Main.generate_aws_audit_report'
        ]
    },
    include_package_data=True,
    python_requires='>=3.6',                
    install_requires=required_packages                   
)