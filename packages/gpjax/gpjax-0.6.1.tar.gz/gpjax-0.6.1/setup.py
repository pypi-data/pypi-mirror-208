# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gpjax',
 'gpjax.base',
 'gpjax.kernels',
 'gpjax.kernels.approximations',
 'gpjax.kernels.computations',
 'gpjax.kernels.non_euclidean',
 'gpjax.kernels.nonstationary',
 'gpjax.kernels.stationary',
 'gpjax.linops']

package_data = \
{'': ['*']}

install_requires = \
['beartype>=0.13.1,<0.14.0',
 'jax>=0.4.1',
 'jaxlib==0.4.7',
 'jaxtyping>=0.2.15,<0.3.0',
 'optax>=0.1.4,<0.2.0',
 'orbax-checkpoint>=0.2.0,<0.3.0',
 'simple-pytree>=0.1.7,<0.2.0',
 'tensorflow-probability>=0.19.0,<0.20.0',
 'tqdm>=4.65.0,<5.0.0']

setup_kwargs = {
    'name': 'gpjax',
    'version': '0.6.1',
    'description': 'Gaussian processes in JAX.',
    'long_description': '<!-- <h1 align=\'center\'>GPJax</h1>\n<h2 align=\'center\'>Gaussian processes in Jax.</h2> -->\n<p align="center">\n<img width="700" height="300" src="https://raw.githubusercontent.com/JaxGaussianProcesses/GPJax/main/docs/_static/gpjax_logo.svg" alt="GPJax\'s logo">\n</p>\n\n[![codecov](https://codecov.io/gh/JaxGaussianProcesses/GPJax/branch/master/graph/badge.svg?token=DM1DRDASU2)](https://codecov.io/gh/JaxGaussianProcesses/GPJax)\n[![CodeFactor](https://www.codefactor.io/repository/github/jaxgaussianprocesses/gpjax/badge)](https://www.codefactor.io/repository/github/jaxgaussianprocesses/gpjax)\n[![Documentation Status](https://readthedocs.org/projects/gpjax/badge/?version=latest)](https://gpjax.readthedocs.io/en/latest/?badge=latest)\n[![PyPI version](https://badge.fury.io/py/GPJax.svg)](https://badge.fury.io/py/GPJax)\n[![DOI](https://joss.theoj.org/papers/10.21105/joss.04455/status.svg)](https://doi.org/10.21105/joss.04455)\n[![Downloads](https://pepy.tech/badge/gpjax)](https://pepy.tech/project/gpjax)\n[![Slack Invite](https://img.shields.io/badge/Slack_Invite--blue?style=social&logo=slack)](https://join.slack.com/t/gpjax/shared_invite/zt-1da57pmjn-rdBCVg9kApirEEn2E5Q2Zw)\n\n[**Quickstart**](#simple-example)\n| [**Install guide**](#installation)\n| [**Documentation**](https://gpjax.readthedocs.io/en/latest/)\n| [**Slack Community**](https://join.slack.com/t/gpjax/shared_invite/zt-1da57pmjn-rdBCVg9kApirEEn2E5Q2Zw)\n\nGPJax aims to provide a low-level interface to Gaussian process (GP) models in\n[Jax](https://github.com/google/jax), structured to give researchers maximum\nflexibility in extending the code to suit their own needs. The idea is that the\ncode should be as close as possible to the maths we write on paper when working\nwith GP models.\n\n# Package support\n\nGPJax was founded by [Thomas Pinder](https://github.com/thomaspinder). Today,\nthe maintenance of GPJax is undertaken by [Thomas\nPinder](https://github.com/thomaspinder) and [Daniel\nDodd](https://github.com/Daniel-Dodd).\n\nWe would be delighted to receive contributions from interested individuals and\ngroups. To learn how you can get involved, please read our [guide for\ncontributing](https://github.com/JaxGaussianProcesses/GPJax/blob/master/CONTRIBUTING.md).\nIf you have any questions, we encourage you to [open an\nissue](https://github.com/JaxGaussianProcesses/GPJax/issues/new/choose). For\nbroader conversations, such as best GP fitting practices or questions about the\nmathematics of GPs, we invite you to [open a\ndiscussion](https://github.com/JaxGaussianProcesses/GPJax/discussions).\n\nFeel free to join our [Slack\nChannel](https://join.slack.com/t/gpjax/shared_invite/zt-1da57pmjn-rdBCVg9kApirEEn2E5Q2Zw),\nwhere we can discuss the development of GPJax and broader support for Gaussian\nprocess modelling.\n\n# Supported methods and interfaces\n\n## Notebook examples\n\n> - [**Conjugate Inference**](https://gpjax.readthedocs.io/en/latest/examples/regression.html)\n> - [**Classification with MCMC**](https://gpjax.readthedocs.io/en/latest/examples/classification.html)\n> - [**Sparse Variational Inference**](https://gpjax.readthedocs.io/en/latest/examples/uncollapsed_vi.html)\n> - [**BlackJax Integration**](https://gpjax.readthedocs.io/en/latest/examples/classification.html)\n> - [**Laplace Approximation**](https://gpjax.readthedocs.io/en/latest/examples/classification.html#Laplace-approximation)\n> - [**Inference on Non-Euclidean Spaces**](https://gpjax.readthedocs.io/en/latest/examples/kernels.html#Custom-Kernel)\n> - [**Inference on Graphs**](https://gpjax.readthedocs.io/en/latest/examples/graph_kernels.html)\n> - [**Learning Gaussian Process Barycentres**](https://gpjax.readthedocs.io/en/latest/examples/barycentres.html)\n> - [**Deep Kernel Regression**](https://gpjax.readthedocs.io/en/latest/examples/haiku.html)\n\n## Guides for customisation\n>\n> - [**Custom kernels**](https://gpjax.readthedocs.io/en/latest/examples/kernels.html#Custom-Kernel)\n> - [**UCI regression**](https://gpjax.readthedocs.io/en/latest/examples/yacht.html)\n\n## Conversion between `.ipynb` and `.py`\nAbove examples are stored in [examples](examples) directory in the double\npercent (`py:percent`) format. Checkout [jupytext\nusing-cli](https://jupytext.readthedocs.io/en/latest/using-cli.html) for more\ninfo.\n\n* To convert `example.py` to `example.ipynb`, run:\n\n```bash\njupytext --to notebook example.py\n```\n\n* To convert `example.ipynb` to `example.py`, run:\n\n```bash\njupytext --to py:percent example.ipynb\n```\n\n# Simple example\n\nLet us import some dependencies and simulate a toy dataset $\\mathcal{D}$.\n\n```python\nimport gpjax as gpx\nfrom jax import grad, jit\nimport jax.numpy as jnp\nimport jax.random as jr\nimport optax as ox\n\nkey = jr.PRNGKey(123)\n\nf = lambda x: 10 * jnp.sin(x)\n\nn = 50\nx = jr.uniform(key=key, minval=-3.0, maxval=3.0, shape=(n,1)).sort()\ny = f(x) + jr.normal(key, shape=(n,1))\nD = gpx.Dataset(X=x, y=y)\n\n# Construct the prior\nmeanf = gpx.mean_functions.Zero()\nkernel = gpx.kernels.RBF()\nprior = gpx.Prior(mean_function=meanf, kernel = kernel)\n\n# Define a likelihood\nlikelihood = gpx.Gaussian(num_datapoints = n)\n\n# Construct the posterior\nposterior = prior * likelihood\n\n# Define an optimiser\noptimiser = ox.adam(learning_rate=1e-2)\n\n# Define the marginal log-likelihood\nnegative_mll = jit(gpx.objectives.ConjugateMLL(negative=True))\n\n# Obtain Type 2 MLEs of the hyperparameters\nopt_posterior, history = gpx.fit(\n    model=posterior,\n    objective=negative_mll,\n    train_data=D,\n    optim=optimiser,\n    num_iters=500,\n    safe=True,\n    key=key,\n)\n\n# Infer the predictive posterior distribution\nxtest = jnp.linspace(-3., 3., 100).reshape(-1, 1)\nlatent_dist = opt_posterior(xtest, D)\npredictive_dist = opt_posterior.likelihood(latent_dist)\n\n# Obtain the predictive mean and standard deviation\npred_mean = predictive_dist.mean()\npred_std = predictive_dist.stddev()\n```\n\n# Installation\n\n## Stable version\n\nThe latest stable version of GPJax can be installed via\npip:\n\n```bash\npip install gpjax\n```\n\n> **Note**\n>\n> We recommend you check your installation version:\n> ```python\n> python -c \'import gpjax; print(gpjax.__version__)\'\n> ```\n\n\n\n## Development version\n> **Warning**\n>\n> This version is possibly unstable and may contain bugs.\n\nClone a copy of the repository to your local machine and run the setup\nconfiguration in development mode.\n```bash\ngit clone https://github.com/JaxGaussianProcesses/GPJax.git\ncd GPJax\npoetry install\n```\n\n> **Note**\n>\n> We advise you create virtual environment before installing:\n> ```\n> conda create -n gpjax_experimental python=3.10.0\n> conda activate gpjax_experimental\n>  ```\n>\n> and recommend you check your installation passes the supplied unit tests:\n>\n> ```python\n> poetry run pytest\n> ```\n\n# Citing GPJax\n\nIf you use GPJax in your research, please cite our [JOSS paper](https://joss.theoj.org/papers/10.21105/joss.04455#).\n\n```\n@article{Pinder2022,\n  doi = {10.21105/joss.04455},\n  url = {https://doi.org/10.21105/joss.04455},\n  year = {2022},\n  publisher = {The Open Journal},\n  volume = {7},\n  number = {75},\n  pages = {4455},\n  author = {Thomas Pinder and Daniel Dodd},\n  title = {GPJax: A Gaussian Process Framework in JAX},\n  journal = {Journal of Open Source Software}\n}\n```\n',
    'author': 'Thomas Pinder',
    'author_email': 'tompinder@live.co.uk',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/JaxGaussianProcesses/GPJax',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
