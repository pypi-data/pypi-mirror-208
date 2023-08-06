# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asociita',
 'asociita.components.evaluator',
 'asociita.components.nodes',
 'asociita.components.orchestrator',
 'asociita.datasets',
 'asociita.models.pytorch',
 'asociita.utils']

package_data = \
{'': ['*']}

install_requires = \
['datasets>=1.0.1,<2.0.0',
 'matplotlib>=3.7.1,<4.0.0',
 'numpy>=1.24.1,<2.0.0',
 'scikit-learn>=1.2.0,<2.0.0',
 'torch>=1.13.1,<2.0.0',
 'torchvision>=0.14.1,<0.15.0']

setup_kwargs = {
    'name': 'asociita',
    'version': '0.1.4',
    'description': "An intuitive and modular simulator for assessing the marginal value of a client's contribution in a decentralized setting.",
    'long_description': '### Setting Configuration\n\nIn order to run the simulation, the `Orchestrator` instance must receive a `settings` object that contains all the necessary parameters. It is possible to store those parameters in a `JSON` format and load them as the Python dictionary by using `asociita.utils.helper.load_from_json` function. Below is an exemplary settings object embedded as a `json` file. All the elements are necessary unless stated otherwise.\n\n```\n{\n    "orchestrator":{\n        "iterations": int,\n        "number_of_nodes": int,\n        "local_warm_start": bool,\n        "sample_size": int,\n        "evaluation": "none" | "full"\n        "save_metrics": bool,\n\t"save_models": bool,\n\t"save_path": str\n\t"nodes": [0,\n\t1,\n\t2]\n    },\n    "nodes":{\n    "local_epochs": int,\n    "model_settings": {\n        "optimizer": "RMS",\n        "batch_size": int,\n        "learning_rate": float}\n        }\n}\n```\n\nThe `settings` contains two dictionaries: `orchestrator` and `nodes`.\n\n`orchestrator` contains all the settings necessary details of the training:\n\n* `iterations` is the number of rounds to be performed. Example: `iterations:12`\n* `number_of_nodes` is the number of nodes that will be included in the training. Example: `number_of_nodes: 10`\n* `local_warm_start` allows to distribute various pre-trained weights to different local clients. Not implemeneted yet. Example: `local_warm_start: false`.\n* `sample_size` is the size of the sample that will be taken each round. Example: `sample_size : 4.`\n* `evaluation` allows to control the evaluation procedure across the clients.  Currently, only `none` or `full` are supported. Setting the evaluation to full will perform a full evaluation of every client included in the training. Example: `evaluation: full`\n* `save_metrics` allows to control whether the metrics should be saved in a csv file. Example: `save_metrics: true.`\n* `save_models` allows to control whether the models should be saved. Not implemeneted yet. Example: `save_metrics: false`.\n* `save_path` is the system path that will be used when saving the model. It is possible to define a saving_path in a method call.\n* `nodes` is the list containing the ids of all the nodes participating in the training. Length of `nodes` must be equal `number_of_nodes`.\n\n`nodes` contains all the necessary configuration for nodes.\n\n* `"local_epochs":` the number of local epochs to be performed on the local nodes.\n* `"model_settings"` is a dictionary containing all the parameters for training the model.\n  * `optimizer` is an optimizer that will be used during the training. Example: `optimizer: "RMS"`\n  * `batch_size` is the batch size that will be used during the training. Example: `batch_size: 32`\n  * `learning_rate` is the learning rate that will be used during the training. Example: `learning_rate: 0.001`\n',
    'author': 'Maciej Zuziak',
    'author_email': 'maciejkrzysztof.zuziak@isti.cnr.it',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Scolpe/Asociita',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
