# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['romeways_memory_queue',
 'romeways_memory_queue.config',
 'romeways_memory_queue.config.connector',
 'romeways_memory_queue.config.queue',
 'romeways_memory_queue.infrastructure',
 'romeways_memory_queue.infrastructure.connector']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'romeways-memory-queue',
    'version': '0.2.0',
    'description': '',
    'long_description': '# Romeways memory queue\n\nThis is an extra package for romeways for more details access the [romeways](https://github.com/CenturyBoys/romeways) Github page.\n\n## Configs\n\n### Queue\n\nThe only difference between the `romeways.GenericQueueConfig` and `romeways_memory_queue.MemoryQueueConfig` is the `multiprocessing.Queue` instance.\n\n```python\nfrom dataclasses import dataclass\nfrom multiprocessing import Queue\n\nfrom romeways import GenericQueueConfig\n\n\n@dataclass(slots=True, frozen=True)\nclass MemoryQueueConfig(GenericQueueConfig):\n    connector_name: str\n    frequency: float\n    max_chunk_size: int\n    sequential: bool\n    queue: Queue\n```\n### Connector\n\n\n```python\nfrom dataclasses import dataclass\n\nfrom romeways import GenericConnectorConfig\n\n@dataclass(slots=True, frozen=True)\nclass MemoryConnectorConfig(GenericConnectorConfig):\n    connector_name: str\n```\n\n## Use case\n\n```python\nfrom multiprocessing import Queue\nimport asyncio\n\nimport romeways\n\n# Config the connector\nqueue = Queue()\n\n# Create a queue config\nconfig_q = romeways.MemoryQueueConfig(\n    connector_name="memory-dev1",\n    frequency=1,\n    max_chunk_size=10,\n    sequential=False,\n    queue=queue\n)\n\n# Register a controller/consumer for the queue name\n@romeways.queue_consumer(queue_name="queue.payment.done", config=config_q)\nasync def controller(message: romeways.Message):\n    print(message)\n\n\n\nconfig_p = romeways.MemoryConnectorConfig(connector_name="memory-dev1")\n\n# Register a connector\nromeways.connector_register(\n    connector=romeways.MemoryQueueConnector, config=config_p, spawn_process=True\n)\n\nasyncio.run(romeways.start())\n\n```\n',
    'author': 'Marco Sievers de Almeida Ximit Gaia',
    'author_email': 'im.ximit@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
