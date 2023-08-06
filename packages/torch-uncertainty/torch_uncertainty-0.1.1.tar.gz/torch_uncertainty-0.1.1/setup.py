# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torch_uncertainty',
 'torch_uncertainty.baselines',
 'torch_uncertainty.baselines.batched',
 'torch_uncertainty.baselines.masked',
 'torch_uncertainty.baselines.mimo',
 'torch_uncertainty.baselines.packed',
 'torch_uncertainty.baselines.standard',
 'torch_uncertainty.datamodules',
 'torch_uncertainty.datasets',
 'torch_uncertainty.layers',
 'torch_uncertainty.metrics',
 'torch_uncertainty.models',
 'torch_uncertainty.models.resnet',
 'torch_uncertainty.models.wideresnet',
 'torch_uncertainty.routines',
 'torch_uncertainty.transforms',
 'torch_uncertainty.utils']

package_data = \
{'': ['*']}

install_requires = \
['einops>=0.6.0,<0.7.0',
 'huggingface-hub>=0.14.1,<0.15.0',
 'pytorch-lightning>=1.9.0,<2.0.0',
 'scipy>=1.10.0,<2.0.0',
 'tensorboard>=2.11.2,<3.0.0',
 'timm>=0.6.12,<0.7.0',
 'torchinfo>=1.7.1,<2.0.0',
 'torchvision>=0.14.1,<0.15.0']

setup_kwargs = {
    'name': 'torch-uncertainty',
    'version': '0.1.1',
    'description': 'A PyTorch Library for benchmarking and leveraging efficient predictive uncertainty quantification techniques.',
    'long_description': '<div align="center">\n\n![Torch Uncertainty Logo](https://github.com/ENSTA-U2IS/torch-uncertainty/blob/main/docs/source/_static/images/torch_uncertainty.png)\n\n[![pypi](https://img.shields.io/pypi/v/torch_uncertainty.svg)](https://pypi.python.org/pypi/torch_uncertainty) [![tests](https://github.com/ENSTA-U2IS/torch-uncertainty/actions/workflows/run-tests.yml/badge.svg?branch=main&event=push)](https://github.com/ENSTA-U2IS/torch-uncertainty/actions/workflows/run-tests.yml) [![Docs](https://github.com/ENSTA-U2IS/torch-uncertainty/actions/workflows/build-docs.yml/badge.svg)](https://torch-uncertainty.github.io/) [![Code Coverage](https://img.shields.io/codecov/c/github/ENSTA-U2IS/torch-uncertainty.svg)](https://codecov.io/gh/ENSTA-U2IS/torch-uncertainty) [![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n</div>\n\n_TorchUncertainty_ is a package designed to help you leverage uncertainty quantification techniques and make your neural networks more reliable. It is based on PyTorch Lightning to handle multi-GPU training and inference and automatic logging through tensorboard.\n\n---\n\nThis package provides a multi-level API, including:\n- ready-to-train baselines on research datasets, such as ImageNet and CIFAR\n- baselines available for training on your datasets\n- [pretrained weights](https://huggingface.co/torch-uncertainty) for these baselines on ImageNet and CIFAR.\n- layers available for use in your networks\n\n## Installation\n\nThe package can be installed from PyPI:\n\n```sh\npip install torch-uncertainty\n```\n\nTo contribute, install the package from source following the instructions of the [dedicated page](https://torch-uncertainty.github.io/installation.html) in the documentation and activate the pre-commit hooks with `pre-commit install`.\n\n## Getting Started and Documentation\n\nPlease find the documentation at [torch-uncertainty.github.io](https://torch-uncertainty.github.io).\n\nA quickstart is available at [torch-uncertainty.github.io/quickstart](https://torch-uncertainty.github.io/quickstart.html).\n\n## Implemented baselines\n\nTo date, the following baselines are implemented:\n\n- Deep Ensembles\n- Masksembles\n- Packed-Ensembles\n\n## Tutorials\n\n\n## Awesome Uncertainty repositories\n\nYou may find a lot of information about modern uncertainty estimation techniques on the [Awesome Uncertainty in Deep Learning](https://github.com/ENSTA-U2IS/awesome-uncertainty-deeplearning).\n\n## Other References\n\nThis package also contains the official implementation of Packed-Ensembles.\n\nIf you find the corresponding models interesting, please consider citing our [paper](https://arxiv.org/abs/2210.09184):\n\t\n    @inproceedings{laurent2023packed,\n        title={Packed-Ensembles for Efficient Uncertainty Estimation},\n        author={Laurent, Olivier and Lafage, Adrien and Tartaglione, Enzo and Daniel, Geoffrey and Martinez, Jean-Marc and Bursuc, Andrei and Franchi, Gianni},\n        booktitle={ICLR},\n        year={2023}\n    }\n',
    'author': 'ENSTA U2IS',
    'author_email': 'olivier.laurent@ensta-paris.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
