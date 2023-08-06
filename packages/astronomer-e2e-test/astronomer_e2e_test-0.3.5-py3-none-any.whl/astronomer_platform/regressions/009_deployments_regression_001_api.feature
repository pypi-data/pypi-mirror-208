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
      When (API) we create a "LocalExecutor" deployment "default" with null workspaceUuid
      Then No deployment is returned

  Scenario: List deployments via API
    Given we are authenticated
    And   we have a workspace
      When (API) we list workspace deployments
      Then a deployment list is returned
      And  deployment length is equal to "0"
