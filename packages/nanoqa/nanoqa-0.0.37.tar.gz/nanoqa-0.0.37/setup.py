# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nanoqa',
 'nanoqa.components',
 'nanoqa.components.document_store',
 'nanoqa.components.file_processing',
 'nanoqa.components.file_processing.convertors',
 'nanoqa.components.file_processing.text_processor',
 'nanoqa.components.question_answering',
 'nanoqa.components.question_answering.handlers',
 'nanoqa.components.question_answering.pipeline',
 'nanoqa.components.question_answering.ranker',
 'nanoqa.components.question_answering.reader',
 'nanoqa.components.question_answering.retriever',
 'nanoqa.schemas',
 'nanoqa.schemas.pipeline',
 'nanoqa.schemas.reader',
 'nanoqa.schemas.retriever']

package_data = \
{'': ['*'], 'nanoqa': ['static/*']}

install_requires = \
['PyMuPDF==1.21.1',
 'adapter-transformers==3.1.0',
 'datasets==2.9.0',
 'docx2python==2.6.0',
 'elasticsearch==7.17.4',
 'fpdf2==2.6.1',
 'mmh3==3.0.0',
 'more_itertools==9.0.0',
 'nltk==3.8.1',
 'rich==13.3.1',
 'wheel==0.38.4']

entry_points = \
{'console_scripts': ['cli_command_name = package_name:function']}

setup_kwargs = {
    'name': 'nanoqa',
    'version': '0.0.37',
    'description': '',
    'long_description': '<div align="center"> \n    <h1>\n        Question Answering kit\n    </h1>\n</div>\n\n## Requirements\n\n    - python >= 3.8\n\n```bash\n# python environment\nwhich python3\npython3 -m venv nanoEnv\nsource ./nanoEnv/bin/activate\n\n# m1 chip, problem shooting pyserini installation\n# CFLAGS="-mavx -DWARN(a)=(a)" pip install nmslib \n\n# pip3 upgrade\npip3 install --upgrade pip\npip3 install -r requirements.txt\n\n# we also need to install tessaract library, well google it for your os\n## For Linux\nsudo apt install tesseract-ocr -y\nsudo apt install tesseract-ocr-heb\nsudo apt install tesseract-ocr-all -y\n```\n\n    - Elasticsearch\n\n```bash\n# run elasticsearch in a docker container\ndocker run -d -p 127.0.0.1:9200:9200 -p 127.0.0.1:9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.9.2\n# after creation of the container, run the following command to start the container\ndocker start <container_id>\n```\n\n## Todos\n\n- [X] Migrate/Re-Implement full QA functions\n- [X] Implementation of pdf conversion.\n- [X] Implementation of file extraction.\n- [X] Implementation of Retriever via ElasticSearch\n- [X] Implementation of fine-tuning the reader with adapter\n- [X] Put tests\n\n# Download WikiDump\n\n```bash\npython download_wikidump.py --lang en --latest --delete-dump \n```\n\n\n## ChangeLog\n\n- 2023-03-02: replace xpdf by PyMuPDF\n',
    'author': 'Kunpeng GUO',
    'author_email': 'gabin.guo@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/gabinguo/nanoQA',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
