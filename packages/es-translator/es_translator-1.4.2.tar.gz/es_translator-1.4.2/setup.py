# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['es_translator',
 'es_translator.interpreters',
 'es_translator.interpreters.apertium',
 'es_translator.interpreters.argos']

package_data = \
{'': ['*']}

install_requires = \
['argostranslate>=1.7,<2.0',
 'click>=8,<9',
 'coloredlogs',
 'deb-pkg-tools>=8.4,<9.0',
 'elasticsearch-dsl>=7.4.0,<8.0.0',
 'elasticsearch>=7.10,<7.11',
 'pycountry>=22.3,<23.0',
 'rich>=12,<13',
 'sh>=1,<2',
 'torch>=1.13,<2.0',
 'urllib3>=1.26,<2.0']

entry_points = \
{'console_scripts': ['es-translator = es_translator.cli:translate',
                     'es-translator-pairs = es_translator.cli:pairs']}

setup_kwargs = {
    'name': 'es-translator',
    'version': '1.4.2',
    'description': 'A lazy yet bulletproof machine translation tool for Elastichsearch.',
    'long_description': '# ES Translator\n\n[![CircleCI](https://circleci.com/gh/ICIJ/es-translator.svg?style=svg)](https://circleci.com/gh/ICIJ/es-translator)\n\nA lazy yet bulletproof machine translation tool for Elastichsearch.\n\n```\nUsage: es-translator [OPTIONS]\n\nOptions:\n  --url TEXT                    Elastichsearch URL  [required]\n  --index TEXT                  Elastichsearch Index  [required]\n  --interpreter TEXT            Interpreter to use to perform the translation\n  --source-language TEXT        Source language to translate from  [required]\n  --target-language TEXT        Target language to translate to  [required]\n  --intermediary-language TEXT  An intermediary language to use when no\n                                translation is available between the source\n                                and the target. If none is provided this will\n                                be calculated automatically.\n  --source-field TEXT           Document field to translate\n  --target-field TEXT           Document field where the translations are\n                                stored\n  --query-string TEXT           Search query string to filter result\n  --data-dir PATH               Path to the directory where to language model\n                                will be downloaded\n  --scan-scroll TEXT            Scroll duration (set to higher value if you\'re\n                                processing a lot of documents)\n  --dry-run                     Don\'t save anything in Elasticsearch\n  --pool-size INTEGER           Number of parallel processes to start\n  --pool-timeout INTEGER        Timeout to add a translation\n  --syslog-address TEXT         Syslog address\n  --syslog-port INTEGER         Syslog port\n  --syslog-facility TEXT        Syslog facility\n  --stdout-loglevel TEXT        Change the default log level for stdout error\n                                handler\n  --help                        Show this message and exit.\n```\n\n## Installation (Ubuntu)\n\nInstall Apertium:\n\n```\nwget https://apertium.projectjj.com/apt/install-nightly.sh -O - | sudo bash\nsudo apt install apertium-all-dev\n```\n\nCreate a Virtualenv and install Pip packages with Poetry:\n\n```\nmake install\n```\n\nOn Ubuntu 22.04 some additional packages might be needed if you use the version from Ubuntu\'s repository:\n\n```\nsudo apt install cg3 apertium-get apertium-lex-tools\n```\n\n\n## Installation (Docker)\n\nNothing to do as long as you have Docker on your system:\n\n```\ndocker run -it icij/es-translator poetry run es-translator --help\n```\n\n## Examples\n\nTranslates documents from French to Spanish on a local Elasticsearch. The translated field is `content` (the default).\n\n```bash\npoetry run es-translator --url "http://localhost:9200" --index my-index --source-language fr --target-language es\n```\n\nTranslates documents from French to English on a local Elasticsearch using Apertium:\n\n```bash\npoetry run es-translator --url "http://localhost:9200" --index my-index --source-language fr --target-language en --interpreter apertium\n```\n\nTo translate the `title` field we could do:\n\n```bash\npoetry run es-translator --url "http://localhost:9200" --index my-index --source-language fr --target-language es --source-field title\n```\n\nTranslates documents from English to Spanish on a local Elasticsearch using 4 threads:\n\n```bash\npoetry run es-translator --url "http://localhost:9200" --index my-index --source-language en --target-language es --pool-size 4\n```\n\nTranslates documents from Portuguese to English, using an intermediary language (Apertium doesn\'t offer this translation pair):\n\n```bash\npoetry run es-translator --url "http://localhost:9200" --index my-index --source-language pt --intermediary-language es --target-language en\n```\n',
    'author': 'ICIJ',
    'author_email': 'engineering@icij.org',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
