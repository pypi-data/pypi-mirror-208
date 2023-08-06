import json


def listing(client, workspace):
    variables = {"workspace": workspace}
    resp = client.execute(listDeploymentsGraphql, variables=variables)
    return json.loads(resp)


listDeploymentsGraphql = """
query listDeployments($workspace: Uuid!) {
    workspaceDeployments(workspaceUuid: $workspace) {
        id
        uuid
        label
        releaseName
        type
        version
        airflowVersion
        status
        config
    }
}
"""


def create(client, workspace, executor, label, description):
    variables = {
        "workspace": workspace,
        "label": label,
        "description": description,
        "config": {"executor": executor},
    }
    resp = client.execute(createDeploymentGraphql, variables=variables)
    return json.loads(resp)


createDeploymentGraphql = """
mutation createDeployment($workspace: Uuid!, $label: String!, $description: String!, $config: JSON!) {
    createDeployment(
        workspaceUuid: $workspace,
        type: "airflow",
        config: $config,
        label: $label,
        description: $description
    ) {
        id
        uuid
        label
        releaseName
        type
        version
        airflowVersion
        status
        config
    }
}
"""


def delete(client, uuid):
    variables = {"uuid": uuid}
    resp = client.execute(deleteDeploymentGraphql, variables=variables)
    return json.loads(resp)


deleteDeploymentGraphql = """
mutation deleteDeployment($uuid: Uuid!) {
    deleteDeployment(
        deploymentUuid: $uuid
    ) {
        id
        uuid
        label
        releaseName
        type
        version
        airflowVersion
        status
        config
    }
}
"""
