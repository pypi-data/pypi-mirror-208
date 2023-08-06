import json


def listing(client):
    resp = client.execute(listWorkspacesGraphql)
    return json.loads(resp)


listWorkspacesGraphql = """
query listWorkspaces {
    workspaces {
        id
        uuid
        active
        description
        properties
        label
    }
}
"""


def create(client, label, description):
    variables = {"label": label, "description": description}
    resp = client.execute(createWorkspaceGraphql, variables=variables)
    return json.loads(resp)


createWorkspaceGraphql = """
mutation createWorkspace($label: String!, $description: String!) {
    createWorkspace(
        label: $label,
        description: $description
    ) {
        id
        uuid
        active
        description
        properties
        label
    }
}
"""


def delete(client, uuid):
    variables = {"uuid": uuid}
    resp = client.execute(deleteWorkspaceGraphql, variables=variables)
    return json.loads(resp)


deleteWorkspaceGraphql = """
mutation deleteWorkspace($uuid: Uuid!) {
    deleteWorkspace(
        workspaceUuid: $uuid
    ) {
        id
        uuid
        active
        description
        properties
        label
    }
}
"""
