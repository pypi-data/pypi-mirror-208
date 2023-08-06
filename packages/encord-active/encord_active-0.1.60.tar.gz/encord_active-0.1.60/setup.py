# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['encord_active',
 'encord_active.app',
 'encord_active.app.actions_page',
 'encord_active.app.auth',
 'encord_active.app.common',
 'encord_active.app.common.components',
 'encord_active.app.common.components.help',
 'encord_active.app.common.components.sticky',
 'encord_active.app.common.components.tags',
 'encord_active.app.conf',
 'encord_active.app.data_quality',
 'encord_active.app.data_quality.sub_pages',
 'encord_active.app.label_onboarding',
 'encord_active.app.model_quality',
 'encord_active.app.model_quality.prediction_types',
 'encord_active.app.project_comparison',
 'encord_active.app.views',
 'encord_active.cli',
 'encord_active.cli.utils',
 'encord_active.lib',
 'encord_active.lib.charts',
 'encord_active.lib.coco',
 'encord_active.lib.common',
 'encord_active.lib.dataset',
 'encord_active.lib.db',
 'encord_active.lib.db.helpers',
 'encord_active.lib.embeddings',
 'encord_active.lib.embeddings.models',
 'encord_active.lib.encord',
 'encord_active.lib.file_structure',
 'encord_active.lib.labels',
 'encord_active.lib.metrics',
 'encord_active.lib.metrics.geometric',
 'encord_active.lib.metrics.heuristic',
 'encord_active.lib.metrics.semantic',
 'encord_active.lib.model_predictions',
 'encord_active.lib.premium',
 'encord_active.lib.project',
 'encord_active.lib.project.sandbox_projects',
 'encord_active.lib.versioning',
 'encord_active.server']

package_data = \
{'': ['*'],
 'encord_active.app': ['assets/*'],
 'encord_active.lib.db': ['migrations/*', 'migrations/20230502111812_init/*'],
 'encord_active.lib.project.sandbox_projects': ['images/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'av>=9.2.0,<10.0.0',
 'clip-ea>=1.0,<2.0',
 'encord-active-components>=0.0.12,<0.0.13',
 'encord>=0.1.75,<0.2.0',
 'faiss-cpu>=1.7.2,<2.0.0',
 'fastapi>=0.95.0,<0.96.0',
 'ftfy>=6.1.1,<7.0.0',
 'gitpython>=3.1.31,<4.0.0',
 'inquirerpy>=0.3.4,<0.4.0',
 'llvmlite>=0.39.1,<0.40.0',
 'loguru>=0.6.0,<0.7.0',
 'matplotlib>=3.5.3,<4.0.0',
 'natsort>=8.1.0,<9.0.0',
 'nodejs-bin>=16.15.1a4,<17.0.0',
 'numpy>=1.23.5,<1.24.0',
 'opencv-python==4.5.5.64',
 'pandas>=1.4.3,<2.0.0',
 'pandera>=0.13.4,<0.14.0',
 'plotly>=5.10.0,<6.0.0',
 'prisma>=0.8.2,<0.9.0',
 'psutil>=5.9.4,<6.0.0',
 'pydantic>=1.10.2,<2.0.0',
 'pyjwt>=2.7.0,<3.0.0',
 'python-dotenv>=0.21.0,<0.22.0',
 'pytz>=2022.2.1,<2023.0.0',
 'regex>=2023.5.5,<2024.0.0',
 'rich>=12.6.0,<13.0.0',
 'scikit-learn>=1.0.1,<2.0.0',
 'scipy==1.8.1',
 'shapely>=1.7.0,<2.0.0',
 'statsmodels>=0.13.5,<0.14.0',
 'streamlit-nested-layout>=0.1.1,<0.2.0',
 'streamlit-plotly-events>=0.0.6,<0.0.7',
 'streamlit>=1.19.0,<2.0.0',
 'termcolor>=2.0.1,<3.0.0',
 'toml>=0.10.2,<0.11.0',
 'torch>=2.0.0,<3.0.0',
 'torchvision>=0.15.2,<0.16.0',
 'typer>=0.6.1,<0.7.0',
 'types-pytz>=2022.2.1,<2023.0.0',
 'umap-learn>=0.5.3,<0.6.0',
 'uvicorn[standard]>=0.21.1,<0.22.0',
 'watchdog>=2.1.9,<3.0.0']

extras_require = \
{'coco': ['pycocotools>=2.0.6,<3.0.0'],
 'notebooks': ['jupyterlab>=3.5.2,<4.0.0', 'ipywidgets>=8.0.4,<9.0.0']}

entry_points = \
{'console_scripts': ['encord-active = encord_active.cli.main:cli']}

setup_kwargs = {
    'name': 'encord-active',
    'version': '0.1.60',
    'description': 'Enable users to improve machine learning models in an active learning fashion via data, label, and model quality.',
    'long_description': '<p align="center">\n<a href="https://docs.encord.com/active/docs" target="_blank">Documentation</a> |\n<a href="https://colab.research.google.com/drive/11iZE1CCFIGlkWdTmhf5XACDojtGeIRGS?usp=sharing" target="_blank">Try it Now</a> |\n<a href="https://encord.com/encord_active/" target="_blank">Website</a> |\n<a href="https://encord.com/blog/" target="_blank">Blog</a> |\n<a href="https://discord.gg/TU6yT7Uvx3" target="_blank">Discord Channel</a>\n</p>\n\n<h1 align="center">\n  <a href="https://encord.com"><img src="https://raw.githubusercontent.com/encord-team/encord-active/main/docs/static/img/icons/encord_active_logo.png" alt="Encord logo"/></a>\n</h1>\n\n<div align="center">\n\n[![PRs-Welcome][contribute-image]][contribute-url]\n![Licence][license-image]\n[![PyPi project][pypi-package-image]][pypi-package]\n![PyPi version][pypi-version-image]\n[![Open In Colab][colab-image]][colab-notebook]\n![downloads-badge][downloads-badge]\n\n[![docs][docs-image]][encord-active-docs]\n[!["Join us on Discord"][discord-image]][join-discord]\n[![Twitter Follow][twitter-image]][twitter-url]\n\n</div>\n\n## ❓ What is Encord Active?\n\n[Encord Active][encord-active-landing] is an open-source toolkit to test, validate, and evaluate your models and surface, curate, and prioritize the most valuable data for labeling to supercharge model performance.\n\nUse Encord Active to:\n\n- Test, validate, and evaluate your models with advanced error analysis\n- Generate model explainability reports\n- Surface, curate, and prioritize the most valuable data for labeling\n- Search through your data using natural language (beta feature)\n- Find and fix dataset errors and biases (duplicates, outliers, label errors)\n\n![homepage-visual]\n\n## Installation\n\nThe simplest way to install the CLI is using `pip` in a suitable virtual environment:\n\n```shell\npip install encord-active\n```\n\nWe recommend using a virtual environment, such as `venv`:\n\n```shell\npython3.9 -m venv ea-venv\nsource ea-venv/bin/activate\npip install encord-active\n```\n\n> `encord-active` requires [python3.9][python-39].\n> If you have trouble installing `encord-active`, you find more detailed instructions on\n> installing it [here](https://docs.encord.com/active/docs/installation). If just want to see it in action try out [this Colab notebook][colab-notebook].\n\n## 👋 Quickstart\n\nGet started immediately by sourcing your environment and running the code below.\nThis downloads a small dataset and launches the Encord Active App for you to explore:\n\n```shell\nencord-active quickstart\n```\n\nor you can use <a href="https://hub.docker.com/r/encord/encord-active"><img src="https://www.docker.com/wp-content/uploads/2022/03/horizontal-logo-monochromatic-white.png" height="20"/></a>:\n\n```shell\ndocker run -it --rm -p 8501:8501 -p 8000:8000 -v ${PWD}:/data encord/encord-active quickstart\n```\n\nAfter opening the UI, we recommend you to head to the [workflow documentation][encord-active-docs-workflow] to see some common workflows.\n\n![projects page](https://raw.githubusercontent.com/encord-team/encord-active/main/docs/static/img/projects-page.jpg)\n\n## 💡 When to use Encord Active?\n\nEncord Active helps you understand and improve your data, labels, and models at all stages of your computer vision journey.\n\nWhether you\'ve just started collecting data, labeled your first batch of samples, or have multiple models in production, Encord Active can help you.\n\n![encord active diagram](https://raw.githubusercontent.com/encord-team/encord-active/main/docs/static/img/process-chart-ea.webp)\n\n## 🔖 Documentation\n\nOur full documentation is available [here](https://docs.encord.com/active/docs). In particular, we recommend checking out:\n\n- [Getting Started](https://docs.encord.com/active/docs/getting-started)\n- [Imports](https://docs.encord.com/active/docs/import/)\n- [Workflows][encord-active-docs-workflow]\n- [User Guides](https://docs.encord.com/active/docs/category/user-guide)\n- [CLI Documentation](https://docs.encord.com/active/docs/cli)\n\n## ⬇️\xa0 Download a sandbox dataset\n\nAnother way to quickly get familiar with Encord Active is to download a dataset from its sandbox.\nThe download command will ask which pre-built dataset to use and will download it into a new directory in the current working directory.\n\n```shell\nencord-active download\ncd /path/of/downloaded/project\nencord-active visualize\n```\n\nThe app should then open in the browser.\nIf not, navigate to [`localhost:8501`](http://localhost:8501).\nOur [docs][encord-active-docs] contains more information about what you can see in the page.\n\n## <img width="24" height="24" src="https://raw.githubusercontent.com/encord-team/encord-active/main/docs/static/img/icons/encord_icon.png"/> Import your dataset\n\n### Quick import Dataset\n\nTo import your data (without labels) save your data in a directory and run the command:\n\n```shell\n# within venv\nencord-active init /path/to/data/directory\n```\n\nA project will be created using the data in the directory.\n\nTo visualize the project run:\n\n```shell\ncd /path/to/project\nencord-active visualize\n```\n\nYou can find more details on the `init` command in the [documentation][encord-active-docs-init].\n\n### Import from COCO\n\nTo import your data, labels, and predictions from COCO, save your data in a directory and run the command:\n\n```shell\n# install COCO extras\n(ea-venv)$ python -m pip install encord-active[coco]\n\n# import samples with COCO annotations\nencord-active import project --coco -i ./images -a ./annotations.json\n\n# import COCO model predictions\nencord-active import predictions --coco results.json\n```\n\n### Import from Encord Platform\n\nThis section requires [setting up an ssh key][encord-docs-ssh] with Encord, so slightly more technical.\n\nTo import an Encord project, use this command:\n\n```shell\nencord-active import project\n```\n\nThe command will allow you to search through your Encord projects and choose which one to import.\n\n## ⭐ Concepts and features\n\n### Quality metrics:\n\nQuality metrics are applied to your data, labels, and predictions to assign them quality metric scores.\nPlug in your own or rely on Encord Active\'s prebuilt quality metrics.\nThe quality metrics automatically decompose your data, label, and model quality to show you how to improve your model performance from a data-centric perspective.\nEncord Active ships with 25+ metrics and more are coming; [contributions][contribute-url] are also very welcome.\n\n### Core features:\n\n- [Data Exploration](https://docs.encord.com/active/docs/workflows/understand-data-distribution)\n- [Data Outlier detection](https://docs.encord.com/active/docs/workflows/identify-outliers-edge-cases)\n- [Label Outlier detection](https://docs.encord.com/active/docs/workflows/identify-outliers-edge-cases#label-outliers)\n- [Object Detection/segmentation Model Decomposition](https://docs.encord.com/active/docs/workflows/evaluate-detection-model)\n- [Classification Model Decomposition](https://docs.encord.com/active/docs/workflows/evaluate-classification-model)\n- [Similarity Search](https://docs.encord.com/active/docs/workflows/image-similarity)\n- [Data Tagging](https://docs.encord.com/active/docs/user-guide/tags)\n- [Visualize TP/FP/FN](https://docs.encord.com/active/docs/workflows/evaluate-detection-model#exploring-the-individual-samples)\n- [COCO Exports](https://docs.encord.com/active/docs/user-guide/filter_export#export-to-coco-file)\n- And much more!\n\nVisit our [documentation][encord-active-docs] to learn more.\n\n### Supported data:\n\n| Data   |     | Labels          |     | Project sizes |               |\n| ------ | --- | --------------- | --- | ------------- | ------------- |\n| `jpg`  | ✅  | Bounding Boxes  | ✅  | Images        | 50.000        |\n| `png`  | ✅  | Polygons        | ✅  | Videos        | 50.000 frames |\n| `tiff` | ✅  | Segmentation    | ✅  |               |               |\n| `mp4`  | ✅  | Classifications | ✅  |               |               |\n|        |     | Polylines       | 🟡  |               |               |\n\n## 🧑🏽\u200d💻Development\n\n### 🛠 Build your own quality metrics\n\nEncord Active is built with customizability in mind. Therefore, you can easily build your own custom metrics\xa0🔧\xa0See the\xa0[Writing Your Own Metric][encord-active-docs-write-metric]\xa0page in the docs for details on this topic. If you need help or guidance feel free to ping us in the **[Discord channel](https://discord.gg/TU6yT7Uvx3)**!\n\n## 👪 Community and support\n\nJoin our channel on\xa0[Discord][join-discord]\xa0to connect with the team behind Encord Active.\n\nAlso, feel free to [suggest improvements or report problems][report-issue] via GitHub issues.\n\n## 🎇 Contributions\n\nIf you\'re using Encord Active in your organization, please try to add your company name to the\xa0[ADOPTERS.md][adopters]. It really helps the project to gain momentum and credibility. It\'s a small contribution back to the project with a big impact.\n\nIf you want to share your custom metrics or improve the tool, please see our\xa0[contributing docs][contribute-url].\n\n### 🦸 Contributors\n\n<a href="https://github.com/encord-team/encord-active/graphs/contributors">\n  <img src="https://contrib.rocks/image?repo=encord-team/encord-active" alt="Contributors graph"/>\n</a>\n\n[@Javi Leguina](https://github.com/jleguina)\n\n## Licence\n\nThis repository is published under the Apache 2.0 licence.\n\n[adopters]: https://github.com/encord-team/encord-active/blob/main/ADOPTERS.md\n[colab-image]: https://colab.research.google.com/assets/colab-badge.svg\n[colab-notebook]: https://colab.research.google.com/drive/11iZE1CCFIGlkWdTmhf5XACDojtGeIRGS?usp=sharing\n[contribute-image]: https://img.shields.io/badge/PRs-welcome-blue.svg\n[contribute-url]: https://docs.encord.com/active/docs/contributing\n[docs-image]: https://img.shields.io/badge/docs-online-blue\n[downloads-badge]: https://static.pepy.tech/badge/encord-active\n[encord-active-docs-init]: https://docs.encord.com/active/docs/import/quick-import-data\n[encord-active-docs-workflow]: https://docs.encord.com/active/docs/category/workflows\n[encord-active-docs-write-metric]: https://docs.encord.com/active/docs/metrics/write-your-own\n[encord-active-docs]: https://docs.encord.com/active/docs\n[encord-active-landing]: https://encord.com/encord-active/\n[encord-docs-ssh]: https://docs.encord.com/admins/settings/public-keys/#set-up-public-key-authentication\n[homepage-visual]: https://raw.githubusercontent.com/encord-team/encord-active/main/homepage_visual.png\n[join-discord]: https://discord.gg/TU6yT7Uvx3\n[license-image]: https://img.shields.io/github/license/encord-team/encord-active\n[new-issue]: https://github.com/encord-team/encord-active/issues/new\n[pypi-package-image]: https://img.shields.io/pypi/v/encord-active\n[pypi-package]: https://www.piwheels.org/project/encord-active/\n[pypi-version-image]: https://img.shields.io/pypi/pyversions/encord-active\n[python-39]: https://www.python.org/downloads/release/python-3915/\n[report-issue]: https://github.com/encord-team/data-quality-pocs/issues/new\n[discord-image]: https://shields.io/badge/Discord-chat-blue?logo=discord&logoColor=white\n[twitter-image]: https://img.shields.io/twitter/follow/encord_team?label=%40encord_team&style=social\n[twitter-url]: https://twitter.com/encord_team\n',
    'author': 'Cord Technologies Limited',
    'author_email': 'hello@encord.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://encord.com/encord-active/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9, !=2.7.*, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*, !=3.7.*, !=3.8.*, !=3.11.*',
}


setup(**setup_kwargs)
