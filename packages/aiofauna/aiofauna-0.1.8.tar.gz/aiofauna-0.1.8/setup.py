# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiofauna']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'Markdown>=3.4.3,<4.0.0',
 'Pygments>=2.15.1,<3.0.0',
 'aiohttp-devtools>=1.0.post0,<2.0',
 'aiohttp-sse>=2.1.0,<3.0.0',
 'aiohttp>=3.8.4,<4.0.0',
 'aiohttp_cors>=0.7.0,<0.8.0',
 'iso8601>=1.1.0,<2.0.0',
 'pydantic[dotenv]>=1.10.7,<2.0.0']

setup_kwargs = {
    'name': 'aiofauna',
    'version': '0.1.8',
    'description': '',
    'long_description': '---\ntitle: AioFauna\n---\n# AioFauna\n\n🚀 Introducing aiofauna: A full-stack framework built on top of Aiohttp, Pydantic and FaunaDB.\n\n🔥 Inspired by FastAPI focuses on Developer Experience, Productivity and Versatility.\n\n🌟 Features:\n\n✅ Supports Python 3.7+, comes with an opinionated ODM (Object Document Mapper) out of the box for FaunaDB that abstracts out complex FQL expressions into pythonic, fully typed asynchronous methods for all CRUD operations.\n\n✅ Performant and scalable: Built on top of Aiohttp a powerful http server and client and FaunaDB an scalable serverless database for modern applications.\n\n✅ Async/await coroutines: Leverage the power of async programming for enhanced performance and responsiveness, being ASGI compliant is compatible with most async python frameworks.\n\n✅ Automatic Swagger UI generation: Automatic generation of interactive Swagger UI documentation for instant testing of your API.\n\n✅ SSE (Server Sent Events): Built-in support for SSE (Server Sent Events) for real-time streaming of data from FaunaDB to your application.\n\n✅ Robust data validation: Built-in support for Pydantic models for robust data validation and serialization.\n\n✅ Auto-provisioning: Automatic management of indexes, unique indexes, and collections with FaunaModel ODM.\n\n✅ Full JSON communication: Custom encoder to ensure seamless data exchange between your application and FaunaDB backend.\n\n✅ Markdown and Jinja support with live reload: experiment an smooth frontend devserver experience without leaving your backend code.\n\n✅ Inspired by fastapi, you will work with almost the same syntax and features like path operations, path parameters, query parameters, request body, status codes and more.\n\n💡 With aiofauna, you can build fast, scalable, and reliable modern applications, while building seamless integrations thanks to the fastest http client aiohttp and the most versatile database FaunaDB, you will enjoy integrating with third party services such as APIs, Data Sources and Cloud Services.\n\n📚 Check out the aiofauna library, and start building your next-gen applications today! 🚀\n\n#Python #FaunaDB #Async #Pydantic #aiofauna\n\n⚙️ If you are using a synchronous framework check out [Faudantic](https://github.com/obahamonde/faudantic) for a similar experience with FaunaDB and Pydantic.\n\n📚 [Documentation](https://obahamonde-aiofauna-docs.smartpro.solutions) (Built with aiofauna)\n\n📦 [PyPi](https://pypi.org/project/aiofauna/)\n\n📦 [GitHub](https://github.com/obahamonde/aiofauna)\n\n📦 [Demo](https://aiofaunastreams-fwuw7gz7oq-uc.a.run.app/) (Real time Latency Monitoring between FaunaDB and Google Cloud Run)\n',
    'author': 'Oscar Bahamonde',
    'author_email': 'oscar.bahamonde.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/obahamonde/aiofauna',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
