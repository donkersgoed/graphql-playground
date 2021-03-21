#!/usr/bin/env python3

from aws_cdk import core

from graphql_playground.graphql_playground_stack import GraphqlPlaygroundStack


app = core.App()
GraphqlPlaygroundStack(app, "graphql-playground")

app.synth()
