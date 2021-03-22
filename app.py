#!/usr/bin/env python3
"""The main app, used to synthesize the CDK project."""


# Standard library imports
# -

# Related third party imports
from aws_cdk import core
from dotenv import load_dotenv

# Local application/library specific imports
from graphql_playground.graphql_playground_stack import GraphqlPlaygroundStack

load_dotenv('.env.aws')
app = core.App()
GraphqlPlaygroundStack(app, 'graphql-playground')

app.synth()
