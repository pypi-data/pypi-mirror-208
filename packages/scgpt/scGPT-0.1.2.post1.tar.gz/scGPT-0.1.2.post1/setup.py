# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scgpt', 'scgpt.model', 'scgpt.scbank', 'scgpt.tokenizer', 'scgpt.utils']

package_data = \
{'': ['*']}

install_requires = \
['datasets>=2.3.0,<3.0.0',
 'flash-attn>=1.0.1,<2.0.0',
 'leidenalg>=0.8.10,<0.9.0',
 'llvmlite>=0.38.0,<0.39.0',
 'numba>=0.55.1,<0.56.0',
 'pandas==1.3.5',
 'scanpy>=1.9.1,<1.10.0',
 'scib>=1.0.3,<2.0.0',
 'scikit-misc>=0.1.4,<0.2.0',
 'scvi-tools>=0.16.0,<0.17.0',
 'torch==1.13.0',
 'torchtext==0.14.0',
 'transformers>=4.18.0,<5.0.0',
 'typing-extensions>=4.2.0,<5.0.0',
 'umap-learn>=0.5.3,<0.6.0']

setup_kwargs = {
    'name': 'scgpt',
    'version': '0.1.2.post1',
    'description': 'Large-scale generative pretrain of single cell using transformer.',
    'long_description': '# scGPT\n\nThis is the official codebase for **scGPT: Towards Building a Foundation Model for Single-Cell Multi-omics Using Generative AI**.\n\n## Installation\n\nscGPT is available on PyPI. To install scGPT, run the following command:\n\n```bash\n$ pip install scgpt\n```\n\n[Optional] We recommend using [wandb](https://wandb.ai/) for logging and visualization.\n\n```bash\n$ pip install wandb\n```\n\nFor developing, we are using the [Poetry](https://python-poetry.org/) package manager. To install Poetry, follow the instructions [here](https://python-poetry.org/docs/#installation).\n\n```bash\n$ git clone this-repo-url\n$ cd scGPT\n$ poetry install\n```\n\n**Note**: The `flash-attn` dependency usually requires specific GPU and CUDA version. If you encounter any issues, please refer to the [flash-attn](https://github.com/HazyResearch/flash-attention/tree/main) repository for installation instructions.\n\n## Pretrained scGPT checkpoints\n\nPlease download the pretrained scGPT checkpoints from [here](https://drive.google.com/drive/folders/1kkug5C7NjvXIwQGGaGoqXTk_Lb_pDrBU?usp=sharing).\n\n## Fine-tune scGPT for scRNA-seq integration\n\nPlease see our example code in [examples/finetune_integration.py](examples/finetune_integration.py). By default, the script assumes the scGPT checkpoint folder stored in the `examples/save` directory.\n\n## To-do-list\n\n- [x] Upload the pretrained model checkpoint\n- [x] Publish to pypi\n- [ ] Provide the pretraining code with generative attention masking\n- [ ] Finetuning examples for multi-omics integration, cell tyep annotation, perturbation prediction, cell generation\n- [ ] Example code for Gene Regulatory Network analysis\n- [ ] Documentation website with readthedocs\n- [ ] Bump up to pytorch 2.0\n- [ ] New pretraining on larger datasets\n- [ ] Reference mapping example\n- [ ] Finetuning with LORA\n- [ ] Publish to huggingface model hub\n\n## Contributing\n\nWe greatly welcome contributions to scGPT. Please submit a pull request if you have any ideas or bug fixes. We also welcome any issues you encounter while using scGPT.\n\n## Acknowledgements\n\nWe sincerely thank the authors of following open-source projects:\n\n- [flash-attention](https://github.com/HazyResearch/flash-attention)\n- [scanpy](https://github.com/scverse/scanpy)\n- [scvi-tools](https://github.com/scverse/scvi-tools)\n- [scib](https://github.com/theislab/scib)\n- [datasets](https://github.com/huggingface/datasets)\n- [transformers](https://github.com/huggingface/transformers)\n\n## Citing scGPT\n\n```bibtex\n@article{cui2023scGPT,\ntitle={scGPT: Towards Building a Foundation Model for Single-Cell Multi-omics Using Generative AI},\nauthor={Cui, Haotian and Wang, Chloe and Maan, Hassaan and Wang, Bo},\njournal={bioRxiv},\nyear={2023},\npublisher={Cold Spring Harbor Laboratory}\n}\n```\n',
    'author': 'Haotian',
    'author_email': 'subercui@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/bowang-lab/scGPT',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.13,<3.11',
}


setup(**setup_kwargs)
