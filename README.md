# Azure DevOps Sync

These scripts allow you to sync the test cases under a test suite.

## Usage

Open the `ado_config.json` file and replace the fields with the desired configurations.

Example:

```JSON
{
  "paths": {
    "features": "features",
    "tests": "tests"
  },
  "credentials": {
    "personal_access_token": "",
    "organization_name": "<your organization name>",
    "project_name": "<your project name>"
  },
  "constants": {
    "TestPlanId": "<your test plan id>",
    "System.TeamProject": "<your team project ~~name~~>"
  }
}
```

After that, you can save your feature files under the folder `features`. Save your files using Gherkin and with the extension `.feature`.

After that, you can navigate to the ado_sync folder and run the following command line

`python scripts/sync_folder.py`

If you provided a Personal Access Token (PAT) on the ado_config.json file, you do not need any further parameter to run. If you didn't provided any value for the PAT, you can pass it through the command line like this

`python scripts/sync_folder.py YOUR_PAT`

After that, the script will synchronize all your test cases.

## Reading test cases

If you want to gather all the test cases under a test plan you can use the command bellow

`python scripts/get_tests_on_suite.py`

It will gather all the test suites and the test cases within each test suite, and save them on `.feature` files under the tests folder in your local machine. You can do this to initialize your repository.

## Pipelines

You can use the `azure-pipelines.yml` file as an example to start your own pipeline.
