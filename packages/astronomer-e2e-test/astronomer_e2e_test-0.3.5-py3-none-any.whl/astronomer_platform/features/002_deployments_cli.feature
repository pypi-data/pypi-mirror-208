@withCLI
Feature: Deployment Basics

  Scenario: Login with CLI (basic auth)
    Given we have credentials
      When we login with the CLI
      Then we get a valid token

  Scenario: Create workspaces via API
    Given we are authenticated
      When (API) we create a workspace "deploymentTests" for "testing various deployments"
      Then a new workspace is returned

  Scenario: Switch to workspace via CLI
    Given we are authenticated
    And   we have a workspace
      When (CLI) we can switch to workspace "deploymentTests"
      Then a new workspace is returned

  Scenario: FIX ME, RE-Authenticate with CLI after workspace switch
    Given we have credentials
      When we login with the CLI
      Then we get a valid token

  Scenario: List deployments via API
    Given we are authenticated
    And   we have a workspace
      When (API) we list workspace deployments
      Then a deployment list is returned
      And  deployment length is equal to "0"

  Scenario: Create LocalExecutor deployment
    Given we are authenticated
    And   we have a workspace
      When (CLI) we create a "local" deployment "default" for "testing default deployment"
      Then a new deployment is returned

  Scenario: List deployments via API
    Given we are authenticated
    And   we have a workspace
      When (API) we list workspace deployments
      Then a deployment list is returned
      And  deployment length is equal to "1"

  Scenario: Delete LocalExecutor deployment
    Given we are authenticated
    And   we have a workspace
    And   we have a deployment
      When (CLI) we delete a deployment "default"
      Then the deployment was deleted

  Scenario: Create CeleryExecutor deployment
    Given we are authenticated
    And   we have a workspace
      When (CLI) we create a "celery" deployment "default" for "testing default deployment"
      Then a new deployment is returned

  Scenario: Delete CeleryExecutor deployment
    Given we are authenticated
    And   we have a workspace
    And   we have a deployment
      When (CLI) we delete a deployment "default"
      Then the deployment was deleted

  Scenario: Create KubernetesExecutor deployment
    Given we are authenticated
    And   we have a workspace
      When (CLI) we create a "kubernetes" deployment "default" for "testing default deployment"
      Then a new deployment is returned

  Scenario: Delete KubernetesExecutor deployment
    Given we are authenticated
    And   we have a workspace
    And   we have a deployment
      When (CLI) we delete a deployment "default"
      Then the deployment was deleted

  Scenario: List deployments via API
    Given we are authenticated
    And   we have a workspace
      When (API) we list workspace deployments
      Then a deployment list is returned
      And  deployment length is equal to "0"

  Scenario: Delete workspaces via API
    Given we are authenticated
    And   we have a workspace
      When (API) we delete a workspace
      Then the workspace was deleted
