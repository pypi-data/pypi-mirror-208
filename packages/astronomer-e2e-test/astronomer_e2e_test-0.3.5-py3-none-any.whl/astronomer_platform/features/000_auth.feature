Feature: Authentication

  Scenario: Authenticate with API
    Given we have credentials
      When we create an API client
      Then we get a valid token

  Scenario: Authenticate with CLI
    Given we have credentials
      When we create a CLI client
      Then we get a valid token

  Scenario: Login with CLI (basic auth)
    Given we have credentials
      When we login with the CLI
      Then we get a valid token
