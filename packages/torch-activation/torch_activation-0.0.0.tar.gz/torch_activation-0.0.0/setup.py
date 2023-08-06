# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torch_activation']

package_data = \
{'': ['*']}

install_requires = \
['torch>=1.0.0']

setup_kwargs = {
    'name': 'torch-activation',
    'version': '0.0.0',
    'description': 'A library of new activation function implement in PyTorch to save time in experiment and have fun',
    'long_description': '# PyTorch Activation Collection\n\nA collection of new, un-implemented activation functions for the PyTorch library. This project is designed for ease of use during experimentation with different activation functions (or simply for fun!). \n\n\n## Installation\n\n```bash\n$ pip install torch-activation\n```\n\n## Usage\n\nTo use the activation functions, simply import from `torch_activation`:\n\n```python\nfrom torch_activation import ShiLU\n\nm = ShiLU(inplace=True)\nx = torch.rand(1, 2, 2, 3)\nm(x)\n```\n\n\n## Available Functions\n\n- ShiLU [[1]](#1)\n\n  ![ShiLU Activation](https://github.com/alan191006/torch_activation/blob/63d8db5d4a2ef19e382fc8175bf47b0a5173df3e/images/activation_images/ShiLU.png "ShiLU")\n\n- DELU [[1]](#1)\n\n  ![DELU Activation](https://github.com/alan191006/torch_activation/blob/63d8db5d4a2ef19e382fc8175bf47b0a5173df3e/images/activation_images/DELU.png "DELU")\n\n- CReLU [[2]](#2)\n\n- GCU [[3]](#3)\n\n  ![GCU Activation](https://github.com/alan191006/torch_activation/blob/63d8db5d4a2ef19e382fc8175bf47b0a5173df3e/images/activation_images/GCU.png "GCU")\n\n- CosLU [[1]](#1)\n\n  ![CosLU Activation](https://github.com/alan191006/torch_activation/blob/63d8db5d4a2ef19e382fc8175bf47b0a5173df3e/images/activation_images/CosLU.png "CosLU")\n\n- CoLU [[4]](#4)\n\n  ![CoLU Activation](https://github.com/alan191006/torch_activation/blob/63d8db5d4a2ef19e382fc8175bf47b0a5173df3e/images/activation_images/CoLU.png "CoLU")\n\n- ReLUN [[1]](#1)\n\n  ![ReLUN Activation](https://github.com/alan191006/torch_activation/blob/63d8db5d4a2ef19e382fc8175bf47b0a5173df3e/images/activation_images/ReLUN.png "ReLUN")\n\n\n- SquaredReLU [[5]](#5)\n\n  ![SquaredReLU Activation](https://github.com/alan191006/torch_activation/blob/63d8db5d4a2ef19e382fc8175bf47b0a5173df3e/images/activation_images/SquaredReLU.png "SquaredReLU")\n\n- ScaledSoftSign [[1]](#1)\n\n  ![ScaledSoftSign Activation](https://github.com/alan191006/torch_activation/blob/63d8db5d4a2ef19e382fc8175bf47b0a5173df3e/images/activation_images/ScaledSoftSign.png "ScaledSoftSign")\n\n  \n## Future features\n* Activations:\n  * LinComb\n  * NormLinComb\n  * ReGLU\n  * GeGLU\n  * SwiGLU\n  * SinLU\n  * DReLUs\n  * ...\n* Layers:\n  * Depth-wise Convolution\n  * ...\n\n## References\n<a id="1">[1]</a>\nPishchik, E. (2023). Trainable Activations for Image Classification. Preprints.org, 2023010463. DOI: 10.20944/preprints202301.0463.v1.\n\n<a id="2">[2]</a>\nShang, W., Sohn, K., Almeida, D., Lee, H. (2016). Understanding and Improving Convolutional Neural Networks via Concatenated Rectified Linear Units. arXiv:1603.05201v2 (cs).\n\n<a id="3">[3]</a>\nNoel, M. M., Arunkumar, L., Trivedi, A., Dutta, P. (2023). Growing Cosine Unit: A Novel Oscillatory Activation Function That Can Speedup Training and Reduce Parameters in Convolutional Neural Networks. arXiv:2108.12943v3 (cs).\n\n<a id="4">[4]</a>\nVagerwal, A. (2021). Deeper Learning with CoLU Activation. arXiv:2112.12078v1 (cs).\n\n<a id="5">[5]</a>\nSo, D. R., Mańke, W., Liu, H., Dai, Z., Shazeer, N., Le, Q. V. (2022). Primer: Searching for Efficient Transformers for Language Modeling. arXiv:2109.08668v2 (cs)',
    'author': 'Alan Huynh',
    'author_email': 'hdmquan@outlook.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
