# Welcome to the GraphQL Playground!

This project provides an example implementation of a GraphQL API, hosted in AWS AppSync and backed by Lambda and DynamoDB. The goal of the project is to provide a tech demo. It explores features like filtering, paging, OAuth scopes and CDK constructs.

The GraphQL Playground is extensively described in a three-part blog series:
- [AppSync Insights Part 1: Restricting Access with OAuth Scopes and VTL](https://www.sentiatechblog.com/appsync-insights-part-1-restricting-access-with-oauth-scopes-and-vtl)
- [AppSync Insights Part 2: Implementing a Generic String Filter in Python](https://www.sentiatechblog.com/appsync-insights-part-2-implementing-a-generic-string-filter-in-python)
- [AppSync Insights Part 3: Minimizing Data Transfer on all Layers ](https://www.sentiatechblog.com/appsync-insights-part-3-minimizing-data-transfer-on-all-layers)

## Installing GraphQL Playground
Check out this repository to you local machine and run `export USER_POOL_DOMAIN_PREFIX=my-graphql-playground && cdk synth && cdk deploy`, where `my-graphql-playground` needs to be replaced with a unique domain prefix. This prefix will be used in a Cognito User Pool Domain, for example `https://my-graphql-playground.auth.eu-west-1.amazoncognito.com/`, and can therefore not be in use by anyone else.
