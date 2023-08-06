#!/usr/bin/env python3

import json
import re
from urllib.parse import urlparse

import requests
import stripe


def delete_deployment(client, workspace_id, deployment_id):
    query = """
    mutation deleteDeployment($id: Uuid!) {
      deleteDeployment(deploymentUuid: $id) {
        id: uuid
        __typename
      }
    }
    """
    variables = {"id": deployment_id, "queryVars": {"workspaceId": workspace_id}}
    client.execute(query, variables=variables)


def delete_workspace(client, workspace_id):
    query = """
    mutation deleteWorkspace($id: Uuid!) {
        deleteWorkspace(workspaceUuid: $id) {
            id: uuid
            __typename
        }
    }
    """
    variables = {"id": workspace_id}
    client.execute(query, variables=variables)


def create_deployment(
    client, deployment_name, workspace_id, executor="KubernetesExecutor"
):
    print(f"Creating deployment {deployment_name}, {executor}")
    query = """
    mutation createDeployment($type: String!,
                              $label: String!,
                              $workspaceId: Uuid!,
                              $version: String,
                              $description: String,
                              $config: JSON,
                              $env: JSON,
                              $properties: JSON) {
      createDeployment(workspaceUuid: $workspaceId,
                       type: $type,
                       label: $label,
                       version: $version,
                       description: $description,
                       config: $config,
                       env: $env,
                       properties: $properties) {
                         ...deployment
                         __typename
                       }
    }
    fragment deployment on Deployment {
      id: uuid
      label
      description
      type
      releaseName
      version
      airflowVersion
      workspace {
        id: uuid
        stripeCustomerId
        billingEnabled
        __typename
      }
      urls {
        type
        url
        __typename
      }
      createdAt
      updatedAt
      config
      env
      properties
      __typename
    }
    """
    variables = {
        "type": "airflow",
        "workspaceId": workspace_id,
        "config": {"executor": executor},
        "label": deployment_name,
    }
    return json.loads(client.execute(query, variables=variables))


def create_workspace(client, workspace_name):
    print(f"Creating workspace {workspace_name}")
    query = """
    mutation createWorkspace($label: String!, $description: String) {
      createWorkspace(label: $label, description: $description) {
        ...workspace
        __typename
      }
    }
    fragment workspace on Workspace {
      id: uuid
      label
      description
      createdAt
      updatedAt
      deploymentCount
      stripeCustomerId
      workspaceCapabilities {
        canUpdateBilling
        canUpdateIAM
        __typename
      }
      trialEndsAt
      billingEnabled
      paywallEnabled
      __typename
    }
    """
    variables = {"label": workspace_name}
    return json.loads(client.execute(query, variables=variables))


def _get_stripe_pk(client):
    headers = {"Authorization": client.token}
    endpoint_parsed = urlparse(client.endpoint)
    hostname = endpoint_parsed.hostname
    endpoint = f"https://{hostname}/billing".replace("houston", "app")
    response = requests.get(endpoint, headers=headers)
    pk_regex = re.compile(r'window\\.STRIPE_PUBLISHABLE_KEY\\s*=\\s*["]([^"]*)"')
    return pk_regex.findall(response.text)[0].strip()


def add_card(client, workspace_id):
    stripe.api_key = _get_stripe_pk(client)
    print("Adding card to Stripe")
    response = stripe.Token.create(
        card={
            "name": "Astronomer Team",
            "number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2020,
            "cvc": "123",
        }
    )
    token_id = response["id"]
    print("Adding card to Astronomer")
    query = """
    mutation addCard($id: Uuid!,
                     $billingEmail: String!,
                     $company: String,
                     $token: String!) {
      addCard(workspaceUuid: $id,
              billingEmail: $billingEmail,
              company: $company,
              token: $token) {
        ...card
        __typename
      }
    }
    fragment card on Card {
      name
      expMonth
      expYear
      last4
      brand
      billingEmail
      company
      __typename
    }
    """
    variables = {
        "id": workspace_id,
        "billingEmail": "humans@astronomer.io",
        "company": "Astronomer",
        "token": token_id,
    }
    return json.loads(client.execute(query, variables=variables))
