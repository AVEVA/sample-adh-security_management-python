# OSIsoft Cloud Services Security Management Python Sample

**Version:** 1.0.0

[![Build Status](https://dev.azure.com/osieng/engineering/_apis/build/status/product-readiness/OCS/osisoft.sample-ocs-security_management-python?repoName=osisoft%2Fsample-ocs-security_management-python&branchName=main)](https://dev.azure.com/osieng/engineering/_build/latest?definitionId=4027&repoName=osisoft%2Fsample-ocs-security_management-python&branchName=main)

Developed against Python 3.9.1.

## Requirements

- Python 3.9+
- Register a [Client-Credentials Client](https://cloud.osisoft.com/clients) in your OSIsoft Cloud Services tenant and create a client secret to use in the configuration of this sample. ([Video Walkthrough](https://www.youtube.com/watch?v=JPWy0ZX9niU))
- Install required modules: `pip install -r requirements.txt`

## About this sample

This sample uses the sample python library, which makes REST API calls to OCS, to manage the security of an OCS Namespace and Tenant. The steps are as follows

1. Create a custom role
1. Create a user and invite them to the Tenant
1. Create a Type
1. Create a Stream
1. Add the created role to the created stream's access control list (ACL) using a PUT REST call
1. Add the 'Tenant Member' role to the created stream's access control list (ACL) using a PATCH REST call
1. Change the owner of the created stream
1. Retrieve the access rights of the example stream
1. Cleanup the created stream, type, role, and user
## Configuring the sample

The sample is configured by modifying the file [config.placeholder.ini](config.placeholder.ini). Details on how to configure it can be found in the sections below. Before editing config.placeholder.ini, rename this file to `config.ini`. This repository's `.gitignore` rules should prevent the file from ever being checked in to any fork or branch, to ensure credentials are not compromised.

### Configuring config.ini

OSIsoft Cloud Services is secured by obtaining tokens from its identity endpoint. Client credentials clients provide a client application identifier and an associated secret (or key) that are authenticated against the token endpoint. You must replace the placeholders in your `config.ini` file with the authentication-related values from your tenant and a client-credentials client created in your OCS tenant.

```ini
[SourceConfiguration]
NamespaceId = REPLACE_WITH_CURRENT_NAMESPACE_ID
TenantId = REPLACE_WITH_CURRENT_TENANT_ID
ClientId = REPLACE_WITH_CURRENT_CLIENT_ID
ClientSecret = REPLACE_WITH_CURRENT_CLIENT_SECRET
Resource = https://dat-b.osisoft.com
ApiVersion = v1
```

## Running the sample

To run this example from the command line once the `config.ini` is configured, run

```shell
python program.py
```

## Running the automated test

To test the sample, run

```shell
pip install pytest
python -m pytest test.py
```

---

Tested against Python 3.9.1

For the main OCS samples page [ReadMe](https://github.com/osisoft/OSI-Samples-OCS)  
For the main OSIsoft samples page [ReadMe](https://github.com/osisoft/OSI-Samples)