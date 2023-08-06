# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['quantuloop_simulator']

package_data = \
{'': ['*']}

install_requires = \
['quantuloop-dense>=0.2.1,<0.3.0',
 'quantuloop-quest>=0.2.2,<0.3.0',
 'quantuloop-sparse>=0.2.1,<0.3.0']

setup_kwargs = {
    'name': 'quantuloop-simulator',
    'version': '2023.5',
    'description': 'Quantuloop Quantum Simulator Suite for HPC',
    'long_description': '# Quantuloop Quantum Simulator Suite for HPC\n\nThe **Quantuloop Quantum Simulator Suite for HPC** is a collection of high-performance quantum computer simulators for the **Ket language**. Since quantum algorithms explore distinct aspects of quantum computation to extract advantages, there is no silver bullet for the simulation of a quantum computer. The Quantuloop Quantum Simulator Suite for HPC offers three quantum simulators today, with new ones coming in the future. The simulators available today are:\n\n* **Quantuloop Sparse**, which brings the Bitwise Representation (implemented in the KBW Sparse) for HPC. This is the only simulator that implements this simulation algorithm and it provides many benefits:\n  * Ready for multi-GPU systems, allowing you to scale up simulations as needed.\n  * Efficient execution time with the amount of superposition, providing faster simulations.\n  * Exact simulation of more than 100 qubits [depending on the algorithm](https://repositorio.ufsc.br/handle/123456789/231060), making it ideal for larger simulations.\n* **Quantuloop Dense** is a state vector simulator built with the NVIDIA cuQuantum SDK cuStateVec. It provides several advantages:\n  * Great scalability in multi-GPU systems, enabling large simulations to be run with ease.\n  * The perfect fit for most quantum algorithms, allowing you to simulate many different types of quantum circuits.\n* **Quantuloop QuEST**, which is an interface for the open-source simulator QuEST. It provides many benefits, including:\n  * Excellent performance for single GPU systems, allowing you to run simulations even if you don\'t have access to multiple GPUs.\n\nBy using the Quantuloop Quantum Simulator Suite for HPC, you can enjoy the following benefits:\n\n* Faster simulation times, as the simulators are optimized for GPU-based computing.\n* Higher scalability, as multi-GPU systems, can be used to run large simulations.\n* Access to unique simulation algorithms, such as the Parallel Bitwise implemented in the Quantuloop Sparse simulator.\n* Ability to simulate a wide range of quantum algorithms and circuits, allowing you to explore the potential of quantum computing.\n\nThe use of this simulator is exclusively for Quantuloop\'s customers and partners. Contact your institution to get your access token or visit <https://quantuloop.com>.\n\n## Installation  \n\nInstalling using pip:\n\n```shell\npip install --index-url https://gitlab.com/api/v4/projects/43029789/packages/pypi/simple quantuloop-simulator\n```\n\nAdd in poetry:\n\n```shell\npoetry source add quantuloop https://gitlab.com/api/v4/projects/43029789/packages/pypi/simple --secondary\npoetry add quantuloop-simulator\n```\n\n## Usage\n\n```py\nimport quantuloop_simulator as ql\n\nql.set_simulator(\n    "Sparse", # or "Dense" or "QuEST"\n    token="YOR.ACCESS.TOKEN", # Quantuloop Access Token is required to use the simulators \n    precision=2, # optional, default 1\n    gpu_count=4, # optional, default use all GPUs\n)\n```\n\n## Compatibility\n\nThe following system requirements are necessary to run the Quantuloop Dense simulator:\n\n* CUDA 11.2 or newer with compatible NVIDIA driver\n* Linux x86_64 with glibc 2.17 or newer\n  * Ubuntu 18.04 or newer.\n  * Red Hat Enterprise Linux 7 or newer.\n* Python 3.8 or newer\n* Ket 0.6.1 or newer\n\nQuantuloop Dense is compatible only with CUDA architecture 70, 75, 80, and 86.\n\n----\n\nBy installing or using this package, you agree to the Quantuloop Quantum Simulator Suite EULA.\n\nAll rights reserved (C) 2023 Quantuloop\n',
    'author': 'Quantuloop',
    'author_email': 'dev@quantuloop.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
