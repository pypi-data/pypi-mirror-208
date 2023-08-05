# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['seven_api_sdk']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.26.24,<2.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'seven-api-sdk',
    'version': '0.1.7',
    'description': 'A package for end users to use the API endpoints of SEVEN with ease.',
    'long_description': '# SEVEN API endpoint package\n\nThis package was meant to help the end users to utilise the API endpoints of Seven. \nIn the current verison you can use the following endpoints:\n\n- Store Fields\n- Store Data\n- Process Fields\n- Process Data\n- Costs\n- Reports\n\nEach of these categories are represented by a class. You can initiate a class instance and use the .call_api() method to get a response.\n\n## Installation\n\nYou can use your package manager to install from PyPI.\n\nIf you are using pip:\n```\npython3 -m pip install seven-api-sdk\n```\n\n## Examples\n\n```\nimport seven_api_sdk\nimport json\n\npassword = "YOUR_SECRET_PASSWORD"\nusername = "YOUR_USERNAME"\nclient_id = "YOUR_CLIENT_ID"\nclient_name = "YOUR_TENANT_NAME"\n\n\nhandler = seven_api_sdk.StoreFields(username=username,password=password,client_id=client_id,client_name=client_name)\ndata = handler.call_api()\n\nprint (json.dumps(data,indent=4))\n\n#You can specify parameters for certain endpoints\nhandler = seven_api_sdk.ProcessData(username=username,password=password,client_id=client_id,client_name=client_name,parameter="proc_by_storeID")\ndata = handler.call_api()\nprint (json.dumps(data,indent=4))\n```',
    'author': 'Daniel Molnar',
    'author_email': 'daniel@prjct8.ch',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
