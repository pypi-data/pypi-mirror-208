# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aws_lambda_stream',
 'aws_lambda_stream.connectors',
 'aws_lambda_stream.events',
 'aws_lambda_stream.filters',
 'aws_lambda_stream.flavors',
 'aws_lambda_stream.pipelines',
 'aws_lambda_stream.repositories',
 'aws_lambda_stream.utils']

package_data = \
{'': ['*']}

install_requires = \
['aws-lambda-powertools>=1.29.1,<2.0.0',
 'boto3>=1.24.66,<2.0.0',
 'pydash>=5.1.1,<6.0.0',
 'reactivex>=4.0.4,<5.0.0',
 'requests-aws4auth>=1.1.2,<2.0.0']

setup_kwargs = {
    'name': 'aws-lambda-stream',
    'version': '1.0.28',
    'description': 'Create stream processors with AWS Lambda functions',
    'long_description': '# aws-lambda-stream\n\nThis a python version of [aws-lambda-stream](https://github.com/jgilbert01/aws-lambda-stream) using [ReactiveX](https://github.com/ReactiveX/RxPY)\n\n\n## Installation\nWith `pip` installed, run:\n\n````\npip install aws-lambda-stream\n````\n\nWith `poetry`, run:\n````\npoetry add aws-lambda-stream\n````\n\n## Credits\n- [aws-lambda-stream](https://github.com/jgilbert01/aws-lambda-stream)\n\n## License\nThis library is licensed under the MIT License. See the LICENSE file.',
    'author': 'Alejandro Hernández',
    'author_email': 'clandro89@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/clandro89/aws-lambda-stream',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
