# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['coredb_pgmq_python']

package_data = \
{'': ['*']}

install_requires = \
['orjson>=3.8.10,<4.0.0',
 'psycopg[binary,pool]>=3.1.8,<4.0.0',
 'pydantic>=1.10.7,<2.0.0']

setup_kwargs = {
    'name': 'coredb-pgmq-python',
    'version': '0.2.2',
    'description': 'Python client for the PGMQ Postgres extension.',
    'long_description': '# Coredb\'s Python Client for PGMQ\n\n## Installation\n\nInstall with `pip` from pypi.org\n\n```bash\npip install coredb-pgmq-python\n```\n\nDependencies:\n\nPostgres running the [CoreDB PGMQ extension](https://github.com/CoreDB-io/coredb/tree/main/extensions/pgmq).\n\n## Usage\n\n## Start a Postgres Instance with the CoreDB extension installed\n\n```bash\ndocker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 quay.io/coredb/pgmq-pg:latest\n```\n\nInitialize a connection to Postgres\n\n```python\n\nfrom coredb_pgmq_python import PGMQueue, Message\n\nqueue = PGMQueue(host="0.0.0.0")\n```\n\nCreate a queue (or a partitioned queue)\n\n```python\nqueue.create_queue("my_queue")\n# queue.create_partitioned_queue("my_partitioned_queue", partition_size=10000)\n```\n\n\nSend a message\n\n```python\nmsg_id: int = queue.send("my_queue", {"hello": "world"})\n```\n\nRead a message, set it invisible for 30 seconds.\n\n```python\nread_message: Message = queue.read("my_queue", vt=10)\nprint(read_message)\n```\n\nArchive the message after we\'re done with it. Archived messages are moved to an archive table.\n\n```python\narchived: bool = queue.archive("my_queue", read_message.msg_id)\n```\n\nDelete a message completely.\n\n```python\nmsg_id: int = queue.send("my_queue", {"hello": "world"})\nread_message: Message = queue.read("my_queue")\ndeleted: bool = queue.delete("my_queue", read_message.msg_id)\n```\n\nPop a message, deleting it and reading it in one transaction.\n\n```python\npopped_message: Message = queue.pop("my_queue")\nprint(popped_message)\n```\n',
    'author': 'Adam Hendel',
    'author_email': 'adam@coredb.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
