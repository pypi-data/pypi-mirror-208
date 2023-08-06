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
    'version': '0.1.0',
    'description': '',
    'long_description': '# Romeways memory queue\n\nThis is an extra package for romeways for more details access the [romeways](https://github.com/CenturyBoys/romeways) Github page.\n\n## Configs\n\n### Queue\n\nThe only difference between the `romeways.GenericQueueConfig` and `romeways_memory_queue.MemoryQueueConfig` are some default parameters.\n\n```python\nfrom dataclasses import dataclass, field\n\nfrom romeways import GenericQueueConfig\n\n\n@dataclass(slots=True, frozen=True)\nclass MemoryQueueConfig(GenericQueueConfig):\n    connector_name: str\n    frequency: float = field(default=0.25)\n    max_chunk_size: int = field(default=10)\n    sequential: bool = field(default=False)\n```\n### Connector\n\nObs: Because the package use the multiprocessing.Queue is allowed to register only one queue consumer.\n\n```python\nfrom dataclasses import dataclass\nfrom multiprocessing import Queue\n\nfrom romeways import GenericConnectorConfig\n\n@dataclass(slots=True, frozen=True)\nclass MemoryConnectorConfig(GenericConnectorConfig):\n    connector_name: str\n    queue: Queue\n```\n\n## Use case\n\n```python\nfrom multiprocessing import Queue\n\nimport romeways\n\n# Create a queue config\nconfig_q = romeways.MemoryQueueConfig(\n    connector_name="memory-dev1"\n)\n\n# Register a controller/consumer for the queue name\n@romeways.queue_consumer(queue_name="queue.payment.done", config=config_q)\nasync def controller(message: romeways.Message):\n    print(message)\n\n# Config the connector\nqueue = Queue()\n\nconfig_p = romeways.MemoryConnectorConfig(connector_name="memory-dev1", queue=queue)\n\n# Register a connector\nromeways.connector_register(\n    connector=romeways.MemoryQueueConnector, config=config_p, spawn_process=True\n)\n\n```\n',
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
