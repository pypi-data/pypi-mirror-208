import os
from pygqlc import GraphQLClient


def setup_gql(env_name=None):
    env = env_name or os.environ.get('ENV')
    gql = GraphQLClient()
    gql.addEnvironment(
        env,
        url=os.environ.get('API'),
        wss=os.environ.get('WSS'),
        headers={'Authorization': os.environ.get('TOKEN')})
    # ! Sets the environment selected in the .env file
    gql.setEnvironment(env)
    return gql
