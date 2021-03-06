"""
The setup module.

Responsible for CDK imports and versioning.
"""

import setuptools


with open('README.md') as fp:
    long_description = fp.read()


CDK_VERSION = None
with open('.env.aws', 'r') as env_file:
    env_vars = env_file.read().split('\n')
    for env_var in env_vars:
        if env_var.startswith('CDK_VERSION'):
            CDK_VERSION = env_var.split('=')[1].replace('"', '')

if not CDK_VERSION:
    raise ValueError('The ENV VAR CDK_VERSION is required.')

setuptools.setup(
    name='graphql_playground',
    version='0.0.1',

    description='An example implementation of an AppSync API in CDK.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Luc van Donkersgoed',

    package_dir={'': 'graphql_playground'},
    packages=setuptools.find_packages(where='graphql_playground'),

    install_requires=[
        f'aws-cdk.core=={CDK_VERSION}',
        f'aws_cdk.aws_appsync=={CDK_VERSION}',
        f'aws_cdk.aws_cognito=={CDK_VERSION}',
        f'aws_cdk.aws_dynamodb=={CDK_VERSION}',
        'python-dotenv==0.10.3',
    ],

    python_requires='>=3.7',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',

        'Topic :: Software Development :: Code Generators',
        'Topic :: GraphQL',
        'Topic :: Utilities',

        'Typing :: Typed',
    ],
)
