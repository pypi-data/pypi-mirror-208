# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['therapi']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.2,<3.0.0']

setup_kwargs = {
    'name': 'therapi',
    'version': '0.0.4',
    'description': 'Therapy to ease the pain of writing boilerplate JSON API consumers.',
    'long_description': '# python-therapi\nTherapy to ease the pain of writing boilerplate JSON API consumers.\n\n---\n\nTired of writing the same code to consume JSON APIs, over and over? Let\'s solve that!\n\n## Query a basic, public JSON API\n\nTo query any basic, public JSON API, we create our consumer class and inherit from `BaseAPIConsumer`, as follows:\n\n```python\nfrom therapi import BaseAPIConsumer\n\nclass MyAPIConsumer(BaseAPIConsumer):\n    base_url = "https://www.an-awesome-service.com/api"\n```\n\nNow we can use this class to make API calls to different endpoints, as follows:\n\n```python\nconsumer = MyAPIConsumer()\nresult = consumer.json_request(method="get", path="items", params={"id": 123})\nprint(result)\n```\n\nWe would see, for example, this response:\n\n```json\n{\n  "data": [\n    {"name": "Laptop", "price": 239},\n    {"name": "Printer", "price": 99}\n  ]\n}\n```\n',
    'author': 'Helmut Irle',
    'author_email': 'me@helmut.dev',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
