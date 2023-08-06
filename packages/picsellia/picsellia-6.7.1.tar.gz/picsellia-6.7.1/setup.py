# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['picsellia', 'picsellia.sdk', 'picsellia.services', 'picsellia.types']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'beartype>=0.11.0,<0.12.0',
 'deprecation>=2.1.0,<3.0.0',
 'orjson>=3.7.11,<4.0.0',
 'picsellia-annotations>=0.6.0,<0.7.0',
 'picsellia-connexion-services>=0.2.0,<0.3.0',
 'pydantic>=1.9.1,<2.0.0',
 'pyyaml>=6.0,<7.0',
 'requests>=2.28.1,<3.0.0',
 'tdqm>=0.0.1,<0.0.2']

setup_kwargs = {
    'name': 'picsellia',
    'version': '6.7.1',
    'description': 'Python SDK package for Picsellia MLOps platform',
    'long_description': '# Picsellia SDK\n\nPicsellia Python SDK is a python library that allows connecting to Picsellia platform.\n\n## Documentation\n\nReference of the SDK can be found at [reference](https://documentation.picsellia.com/reference/client)\n\n## Getting started\nDocumentation can be found at [docs](https://documentation.picsellia.com/docs/getting-started).\nStart by installing the Picsellia python package in your environment.\n```\npip install picsellia\n```\n\nThen, initialize a client\n```python\nfrom picsellia import Client\nclient = Client(api_token=<your api token>)\n```\n\nNow, use it to upload data and create a dataset !\n```python\nlake = client.get_datalake()\nuploaded_data = lake.upload_data(filepaths=["pics/twingo.png", "pics/ferrari.png"], tags=["tag_car"])\n\ndataset = client.create_dataset("cars").create_version("first")\ndataset.add_data(uploaded_data)\n```\n\n## What is Picsellia ?\n\nOur mission is to give you all the necessary tools to relieve the burden of AI projects off of your shoulders. As a data scientist / ML engineer / Researcher, you shouldn\'t have to worry about the following topics :\n\n- [💾 Data Management](https://documentation.picsellia.com/docs/data-management)\n- [📈 Experiment Tracking](https://documentation.picsellia.com/docs/experiment-tracking)\n- [📘 Model Management](https://documentation.picsellia.com/docs/export-an-experiment)\n- [🚀 Model Deployment](https://documentation.picsellia.com/docs/serverless)\n- [👀 Model Monitoring](https://documentation.picsellia.com/docs/monitor-model)\n\nPicsellia is the one-stop place for all the life-cycle of your Computer Vision projects, from ideation to production in a single platform 🚀.\n',
    'author': 'Pierre-Nicolas Tiffreau',
    'author_email': 'pierre-nicolas@picsellia.com',
    'maintainer': 'Pierre-Nicolas Tiffreau',
    'maintainer_email': 'pierre-nicolas@picsellia.com',
    'url': 'https://www.picsellia.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0.0',
}


setup(**setup_kwargs)
