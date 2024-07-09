# CONNECT data services Security Management Python Sample

**Version:** 1.1.4

[![Build Status](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_apis/build/status%2Fproduct-readiness%2FADH%2FAVEVA.sample-adh-security_management-python?repoName=AVEVA%2Fsample-adh-security_management-python&branchName=main)](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_build/latest?definitionId=16185&repoName=AVEVA%2Fsample-adh-security_management-python&branchName=main)

Developed against Python 3.9.1.

## Requirements

- Python 3.7+
- Register a [Client-Credentials Client](https://datahub.connect.aveva.com/clients) in your CONNECT data services tenant and create a client secret to use in the configuration of this sample. ([Video Walkthrough](https://www.youtube.com/watch?v=JPWy0ZX9niU)). Please note that a client is a different authentication method from using your user account to login.
- The client that is registered must have "Manage Permissions" access on all collections and collection items that you intend to set security for. Generally, the Tenant Administrator role will have manage access unless a custom configuration has been set.
- Install required modules: `pip install -r requirements.txt`

## About this sample

This sample uses the sample python library, which makes REST API calls to Cds, to manage the security of an Cds Namespace and Tenant. The steps are as follows

1. Create a custom role
1. Create a user and invite them to the Tenant
1. Create a Type
1. Create a Stream
1. Add the custom role to the example type, example stream, and streams collection access control lists using PUT
1. Add the 'Tenant Member' role to the created stream's access control list (ACL) using a PATCH REST call
1. Change the owner of the created stream
1. Retrieve the access rights of the example stream
1. (Test only) Verify the results of the above steps
1. (Test only) Cleanup the created stream, type, role, and user

## Configuring the sample

The sample is configured by modifying the file [appsettings.placeholder.json](appsettings.placeholder.json). Details on how to configure it can be found in the sections below. Before editing appsettings.placeholder.json, rename this file to `appsettings.json`. This repository's `.gitignore` rules should prevent the file from ever being checked in to any fork or branch, to ensure credentials are not compromised.

### Configuring appsettings.json

CONNECT data services is secured by obtaining tokens from its identity endpoint. Client credentials clients provide a client application identifier and an associated secret (or key) that are authenticated against the token endpoint. You must replace the placeholders in your `appsettings.json` file with the authentication-related values from your tenant and a client-credentials client created in your Cds tenant.

```json
{
  "Resource": "https://uswe.datahub.connect.aveva.com",
  "ApiVersion": "v1",
  "TenantId": "PLACEHOLDER_REPLACE_WITH_TENANT_ID",
  "NamespaceId": "PLACEHOLDER_REPLACE_WITH_NAMESPACE_ID",
  "CommunityId": null,
  "ClientId": "PLACEHOLDER_REPLACE_WITH_APPLICATION_IDENTIFIER",
  "ClientSecret": "PLACEHOLDER_REPLACE_WITH_APPLICATION_SECRET",
  "ContactGivenName": "PLACEHOLDER_REPLACE_WITH_CONTACT_GIVEN_NAME",
  "ContactSurname": "PLACEHOLDER_REPLACE_WITH_CONTACT_SURNAME",
  "ContactEmail": "PLACEHOLDER_REPLACE_WITH_CONTACT_EMAIL"
}
```

## Running the sample

To run this example from the command line once the `appsettings.json` is configured, run

```shell
python program.py
```

## Running the automated test

To test the sample, run

```shell
pip install pytest
python -m pytest test.py
```

Note: Example Type and Stream names are hardcoded, and will need to be updated if they are changed in program.py

---

Tested against Python 3.9.1

For the main Cds samples page [ReadMe](https://github.com/AVEVA/AVEVA-Samples-CloudOperations)  
For the main AVEVA samples page [ReadMe](https://github.com/AVEVA/AVEVA-Samples)
