@withCLI
Feature: Workspace Basics

  # Using the API here for some scenarios
  # because the color output adds special chars
  # which disrupt output parsing and checks


  Scenario: List workspaces via API
    Given we are authenticated
      When (API) we list workspaces
      Then a workspace list is returned
      And workspace length is equal to "0"

  Scenario: Create workspaces via CLI
    Given we are authenticated
      When (CLI) we create a workspace "workspaceTests" for "basic workspace tests"
      Then a new workspace is returned

  Scenario: List workspaces after create
    Given we are authenticated
      When (API) we list workspaces
      Then a workspace list is returned
      And workspace length is equal to "1"

  Scenario: Delete workspaces via API
    Given we are authenticated
    And we have a workspace
      When (CLI) we delete a workspace
      Then the workspace was deleted

  Scenario: List workspaces after delete
    Given we are authenticated
      When (API) we list workspaces
      Then a workspace list is returned
      And workspace length is equal to "0"
