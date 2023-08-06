# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['romeways',
 'romeways.src',
 'romeways.src.core',
 'romeways.src.core.abstract',
 'romeways.src.core.abstract.infrastructure',
 'romeways.src.core.abstract.infrastructure.queue_connector',
 'romeways.src.core.interfaces',
 'romeways.src.core.interfaces.infrastructure',
 'romeways.src.core.interfaces.infrastructure.queue_connector',
 'romeways.src.core.interfaces.infrastructure.spawner',
 'romeways.src.core.interfaces.service',
 'romeways.src.core.interfaces.service.chauffeur',
 'romeways.src.core.interfaces.service.guide',
 'romeways.src.domain',
 'romeways.src.domain.exceptions',
 'romeways.src.domain.models',
 'romeways.src.domain.models.config',
 'romeways.src.domain.models.config.connector',
 'romeways.src.domain.models.config.itinerary',
 'romeways.src.domain.models.config.map',
 'romeways.src.domain.models.config.queue',
 'romeways.src.domain.models.message',
 'romeways.src.infrastructure',
 'romeways.src.infrastructure.spawner',
 'romeways.src.service',
 'romeways.src.service.chauffeur',
 'romeways.src.service.guide']

package_data = \
{'': ['*']}

install_requires = \
['meeseeks-singleton>=0.4.2,<0.5.0']

extras_require = \
{'memory': ['romeways_memory_queue>=0.2.0,<0.3.0']}

setup_kwargs = {
    'name': 'rome-ways',
    'version': '0.1.2',
    'description': 'A queue framework',
    'long_description': '# Romeways\n\n<img src="./docs/images/banner.png" width="200"/>\nby: CenturyBoys\n\nThis project has as goal help developers to not reimplemented default queue consumer behaviour.\n\n# Basics\n\nRomeways works with two basic concepts queue handler and queue connector. The queue connector is a queue consumer and can be spawned in a separate process or in async worker. The queue handler is the callback function that will be called for each retrieved message.\n\nHere you can see all implemented consumer:\n\n| Queue Type            | Install using extra | description                                    |\n|-----------------------|---------------------|------------------------------------------------|\n| multiprocessing.Queue | memory              | [here](romeways_extras/memory_queue/README.md) |\n\nHow to install extra packages?\n\n```shell\npoetry add romeways -E memory\nOR\npip install \'romeways[memory]\'\n```\n\n# Configuration\n\n## Queue connector config\n\nThe queue connector config is all configurations that you need to be able to retrieve messages from the queue.\n\nBellow are the `romeways.GenericConnectorConfig` implementation. This class can be inheritance to allow extra configurations.\n\n#### Params:\n\n- `connector_name: str` For what connector this queue must be delivered\n\n```python\nfrom dataclasses import dataclass\n\n\n@dataclass(slots=True, frozen=True)\nclass GenericConnectorConfig:\n    """\n    connector_name: str Connector name\n    """\n    connector_name: str\n\n```\n\n## Queue handler config\n\nWhen you register a queue consumer you are setting configs and a callback handler for each message that this queue receives.\n\nBellow are the `romeways.GenericQueueConfig` implementation. This class can be inheritance to allow extra configurations.\n\n#### Params:\n\n- `connector_name: str` For what connector this queue must be delivered\n- `frequency: float` Time in seconds for retrieve messages from queue\n- `max_chunk_size: int` Max quantity for messages that one retrieve will get\n- `sequential: bool` If the handler call must be sequential or in asyncio.gather\n\n```python\nfrom dataclasses import dataclass\n\n\n@dataclass(slots=True, frozen=True)\nclass GenericQueueConfig:\n    """\n    connector_name: str For what connector this queue must be delivered\n    frequency: float Time in seconds for retrieve messages from queue\n    max_chunk_size: int Max quantity for messages that one retrieve will get\n    sequential: bool If the handler call must be sequential or in asyncio.gather\n    """\n    connector_name: str\n    frequency: float\n    max_chunk_size: int\n    sequential: bool\n\n```\n\n## Resend on error\n\nRomeways allow you to resend the message to the queue if something in your handler do not perform correctly. For that your code need tho raise the `romeways.ResendException` exception, the message will be resent to the same queue and the `romeways.Message.rw_resend_times` parameter will be raized\n\n\n## Spawn a process\n\nRomeways can run each connector in a separate process or in async workers for that use the parameter `spawn_process` to configure that.\n\n# Example\n\nFor this example we are using the extra package `memory`\n\n```python\nfrom multiprocessing import Queue\n\nimport romeways\n\n# Config the connector\nqueue = Queue()\n\n# Create a queue config\nconfig_q = romeways.MemoryQueueConfig(\n    connector_name="memory-dev1", \n    queue=queue\n)\n\n# Register a controller/consumer for the queue name\n@romeways.queue_consumer(queue_name="queue.payment.done", config=config_q)\nasync def controller(message: romeways.Message):\n    print(message)\n\nconfig_p = romeways.MemoryConnectorConfig(connector_name="memory-dev1")\n\n# Register a connector\nromeways.connector_register(\n    connector=romeways.MemoryQueueConnector, config=config_p, spawn_process=True\n)\n\n```',
    'author': 'Marco Sievers de Almeida Ximit Gaia',
    'author_email': 'im.ximit@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
