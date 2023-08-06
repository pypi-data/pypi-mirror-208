# Vault Credential Fetcher
Convenient wrapper for executing codes on AWS for connecting and fetching credentials from vault.

## Install with pip
```bash
$ pip install AwsVaultCredential
```

## Usage
1. Import the library.
    ```python
   from AwsVaultCredential import VaultCredentialFetcher
    ```

1. Create an instance.
    ```python 
   vc = VaultCredentialFetcher(project_path="",
                               logger=<your_logger_instance>,
                               environment="",
                               vault_region="",
                               vault_role_id="",
                               display_vault_info=True,
                               vault_config_path="")
    ```
    Arguments (all are mandatory):
    * `project_path`: Project name, which would serve as the logger's name (*if specified*), and the prefix for log filenames.
    * `logger`: your Logger Instance
    * `"environment"`: Execution Environment
    * `"vault_region"`: Region in which application is deployed on AWS while vault onborarding
    * `"vault_role_id"`: Role ID/Role Name specific to your application when onboarded 
    * `"display_vault_info"`: By default it is False, used for displaying vault info
    * `"vault_config_path"`: Path where vault config is kept, relative to project path
    
2. Get a logger and start logging.
    ```python
   VaultCreds = vc.get_vault_cred()
    ```

## Author

**&copy; 2022, [Priyansh Gupta](priyansh.gupta@gartner.com)**.