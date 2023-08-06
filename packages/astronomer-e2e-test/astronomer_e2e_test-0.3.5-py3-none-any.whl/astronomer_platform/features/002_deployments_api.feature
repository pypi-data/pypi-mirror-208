@withAPI
Feature: Deployment Basics

  Scenario: Create workspaces via API
    Given we are authenticated
      When (API) we create a workspace "deploymentTests" for "testing various deployments"
      Then a new workspace is returned

  Scenario: List deployments via API
    Given we are authenticated
    And   we have a workspace
      When (API) we list workspace deployments
      Then a deployment list is returned
      And  deployment length is equal to "0"

  Scenario: Create LocalExecutor deployment
    Given we are authenticated
    And   we have a workspace
      When (API) we create a "LocalExecutor" deployment "default" for "testing default deployment"
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
      When (API) we delete a deployment "default"
      Then the deployment was deleted

  Scenario: Create CeleryExecutor deployment
    Given we are authenticated
    And   we have a workspace
      When (API) we create a "CeleryExecutor" deployment "default" for "testing default deployment"
      Then a new deployment is returned

  Scenario: Delete CeleryExecutor deployment
    Given we are authenticated
    And   we have a workspace
    And   we have a deployment
      When (API) we delete a deployment "default"
      Then the deployment was deleted

  Scenario: Create KubernetesExecutor deployment
    Given we are authenticated
    And   we have a workspace
      When (API) we create a "KubernetesExecutor" deployment "default" for "testing default deployment"
      Then a new deployment is returned

  Scenario: Delete KubernetesExecutor deployment
    Given we are authenticated
    And   we have a workspace
    And   we have a deployment
      When (API) we delete a deployment "default"
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
