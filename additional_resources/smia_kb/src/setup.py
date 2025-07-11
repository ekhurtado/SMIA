# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="SMIA Knowledge Base (KB) | HTTP/REST | API Collection",
    author_email="apiteam@swagger.io",
    url="",
    keywords=["Swagger", "SMIA Knowledge Base (KB) | HTTP/REST | API Collection"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    This is a sample SMIA Knowledge Base (KB) based on the OpenAPI 3.0 specification.  You can find out more about at [GitHub](https://github.com/ekhurtado/SMIA). TODO Remove -&gt; In the third iteration of the pet store, we&#x27;ve switched to the design first approach! You can now help us improve the API whether it&#x27;s by making changes to the definition itself or to the code. That way, with time, we can improve the API in general, and expose some of the new features in OAS3.  Some useful links: - [The Pet Store repository](https://github.com/swagger-api/swagger-petstore) - [The source API definition for the Pet Store](https://github.com/swagger-api/swagger-petstore/blob/master/src/main/resources/openapi.yaml) - [SMIA GitHub repository](https://github.com/ekhurtado/SMIA) - [SMIA ReadTheDocs documentation project](https://smia.readthedocs.io/en/latest/) - [SMIA DockerHub repository](hub.docker.com/r/ekhurtado/smia/)
    """
)
