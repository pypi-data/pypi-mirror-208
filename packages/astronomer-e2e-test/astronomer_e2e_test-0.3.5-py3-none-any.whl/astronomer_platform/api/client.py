import json

from graphqlclient import GraphQLClient

createTokenGraphql = """
mutation createToken ($email: String!, $password: String!, $duration: Int!) {
    createToken(identity: $email, password: $password, duration: $duration) {
        token {
            value
        }
    }
}
"""


def getClient(houstonURL, email, password, duration):
    # Create GraphQL client
    client = GraphQLClient(houstonURL)

    # Generate a token for auth, via graphql call
    variables = {"email": email, "password": password, "duration": duration}
    resp = client.execute(createTokenGraphql, variables=variables)
    data = json.loads(resp)

    # print("DATA", data)
    token = data["data"]["createToken"]["token"]["value"]

    # Inject the token into the client
    client.inject_token(token)
    client.token = token

    # cliAuth(client)
    return client
