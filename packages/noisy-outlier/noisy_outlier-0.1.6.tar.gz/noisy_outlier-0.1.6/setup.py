# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['noisy_outlier', 'noisy_outlier.hyperopt', 'noisy_outlier.model']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.24.3,<2.0.0', 'scikit-learn>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'noisy-outlier',
    'version': '0.1.6',
    'description': 'Self-Supervised Learning for Outlier Detection',
    'long_description': '# Self-Supervised Learning for Outlier Detection\n\nThe detection of outliers can be very challenging, especially if the data has features that do not carry \ninformation about the outlyingness of a point.For supervised problems, there are many methods for selecting \nappropriate features. For unsupervised problems it can be challenging to select features that are meaningful \nfor outlier detection. We propose a method to transform the unsupervised problem of outlier detection into a \nsupervised problem to mitigate the problem of irrelevant features and the hiding of outliers in these features. \nWe benchmark our model against common outlier detection models and have clear advantages in outlier detection \nwhen many irrelevant features are present.\n\nThis repository contains the code used for the experiments, as well as instructions to reproduce our results. \nFor reproduction of our results, please switch to the "publication" branch \nor click [here](https://github.com/JanDiers/self-supervised-outlier/tree/publication).\n\nIf you use this code in your publication, we ask you to cite our paper. Find the details below.\n\n## Installation\n\nThe software can be installed by using pip. We recommend to use a virtual environment for installation, for example \nvenv. [See the official guide](https://docs.python.org/3/library/venv.html).\n\nTo install our software, run\n\n``pip install noisy_outlier``\n\n\n## Usage\n\nFor outlier detection, you can use the `NoisyOutlierDetector` as follows. The methods follow the scikit-learn syntax:\n\n```python\nimport numpy as np\nfrom noisy_outlier import NoisyOutlierDetector\nX = np.random.randn(50, 2)  # some sample data\nmodel = NoisyOutlierDetector()\nmodel.fit(X)\nmodel.predict(X)  # returns binary decisions, 1 for outlier, 0 for inlier\nmodel.predict_outlier_probability(X)  # predicts probability for being an outlier, this is the recommended way   \n```\n\nThe `NoisyOutlierDetector` has several hyperpararameters such as the number of estimators for the classification \nproblem or the pruning parameter. To our experience, the default values for the `NoisyOutlierDetector` provide stable \nresults. However, you also have the choice to run routines for optimizing hyperparameters based on a RandomSearch. Details\ncan be found in the paper. Use the `HyperparameterOptimizer` as follows:\n\n````python\nimport numpy as np\nfrom scipy.stats.distributions import uniform, randint\nfrom sklearn import metrics\n\nfrom noisy_outlier import HyperparameterOptimizer, PercentileScoring\nfrom noisy_outlier import NoisyOutlierDetector\n\nX = np.random.randn(50, 5)\ngrid = dict(n_estimators=randint(50, 150), ccp_alpha=uniform(0.01, 0.3), min_samples_leaf=randint(5, 10))\noptimizer = HyperparameterOptimizer(\n                estimator=NoisyOutlierDetector(),\n                param_distributions=grid,\n                scoring=metrics.make_scorer(PercentileScoring(0.05), needs_proba=True),\n                n_jobs=None,\n                n_iter=5,\n                cv=3,\n            )\noptimizer.fit(X)\n# The optimizer is itself a `NoisyOutlierDetector`, so you can use it in the same way:\noutlier_probability = optimizer.predict_outlier_probability(X)\n````\nDetails about the algorithms may be found in our publication. \nIf you use this work for your publication, please cite as follows. To reproduce our results, \nplease switch to the "publication" branch or click [here](https://github.com/JanDiers/self-supervised-outlier/tree/publication).\n\n````\nDiers, J, Pigorsch, C. Self‐supervised learning for outlier detection. Stat. 2021; 10e322. https://doi.org/10.1002/sta4.322 \n````\n\nBibTeX:\n\n````\n@article{\n    https://doi.org/10.1002/sta4.322,\n    author = {Diers, Jan and Pigorsch, Christian},\n    title = {Self-supervised learning for outlier detection},\n    journal = {Stat},\n    volume = {10},\n    number = {1},\n    pages = {e322},\n    keywords = {hyperparameter, machine learning, noisy signal, outlier detection, self-supervised learning},\n    doi = {https://doi.org/10.1002/sta4.322},\n    url = {https://onlinelibrary.wiley.com/doi/abs/10.1002/sta4.322},\n    eprint = {https://onlinelibrary.wiley.com/doi/pdf/10.1002/sta4.322},\n    note = {e322 sta4.322},\n    year = {2021}\n}\n````\n',
    'author': 'JanDiers',
    'author_email': 'jan.diers@uni-jena.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jandiers/self-supervised-outlier',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
