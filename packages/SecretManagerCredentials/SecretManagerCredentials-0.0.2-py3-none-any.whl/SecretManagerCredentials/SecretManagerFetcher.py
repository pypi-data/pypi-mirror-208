"""Imports"""
import json
from logging import exception
import boto3
import hvac
from logging import Logger
from typing import NoReturn

vault_cred_json = dict()


class SecretManagerFetcher(object):
    """
    This Class helps connecting with vault application
    """
    # reads app_init files from path
    global vault_cred_json

    def __init__(self, project_path, logger, environment):
    # def __init__(self, project_path: str, logger: Logger, environment: str,
    #              display_vault_info: bool = False, vault_config_path: str = "",
    #              vault_region: str = "us-east-1") -> NoReturn:
        """
        :param project_path:
        :param logger:
        :param environment:
        """

        # self.project_path = project_path
        # with open(self.project_path + '/src/app_configs/vault_config.json') as json_data_file:
        #     v_config = json.load(json_data_file)
        # vault_params = dict(v_config['vault_paths'])
        # logger.info(vault_params)
        # 
        # self.env = environment
        # self.vault_role = vault_params[self.env]['vault_role']
        # self.vault_app_secret_path = vault_params[self.env]['vault_app_secret_path']
        # self.vault_app_secret_path = vault_params[self.env]['vault_app_secret_path']
        # self.vault_db_secret_path = vault_params[self.env]['vault_db_secret_path']
        # self.vault_pg_host_secret_path = vault_params[self.env]['vault_pg_host_secret_path']
        # self.vault_crm_host_secret_path = vault_params[self.env]['vault_crm_host_secret_path']
        # self.vault_baw_host_secret_path = vault_params[self.env]['vault_baw_host_secret_path']
        # self.vault_azure_host_secret_path = vault_params[self.env]['vault_azure_host_secret_path']
        # self.role_id = vault_params[self.env]['role_id']
        # self.logger = logger
        
        #global vault_cred_json
        # self.logger = logger
        # self.project_path = project_path
        # self.vault_region = vault_region
        # self.vault_config_path = vault_config_path
        # v_config = self.__load_json_file()
        # vault_paths = dict(v_config['vault_paths'])
        # self.vault_role = vault_paths[environment]['vault_role']
        # self.vault_app_secret_path = vault_paths[environment]['vault_app_secret_path']
        # self.vault_db_secret_path = vault_paths[environment]['vault_db_secret_path']
        # self.vault_pg_host_secret_path = vault_paths[environment]['vault_pg_host_secret_path']
        # self.vault_crm_host_secret_path = vault_paths[environment]['vault_crm_host_secret_path']
        # self.vault_baw_host_secret_path = vault_paths[environment]['vault_baw_host_secret_path']
        # self.vault_azure_host_secret_path = vault_paths[environment]['vault_azure_host_secret_path']
        # self.role_id = vault_paths[environment]['role_id']
        # self.hostname = vault_paths[environment]['host']
        # self.display_vault_info = display_vault_info
        temp = 0

    def __load_json_file(self):
        """
        This Function loads the config json file from the path specified
        :return: Config file after being loaded in memory
        """
        try:
            with open(
                    self.project_path + self.vault_config_path
            ) as json_data_file:
                v_config = json.load(json_data_file)
        except Exception:
            # self.logger.error(f"Exception raised while loading Json File")
            # self.logger.error(str("No such file or directory at path: 'vault_config.json'"))
            # self.logger.error("Vault path is : " + self.vault_config_path)
            print("Exception raised while loading Json File")
            raise FileNotFoundError
        else:
            return v_config

    def get_vault_cred(self, host_name):
        """
        :param host_name:
        :param self
        :return:
        """
        try:
            if len(vault_cred_json) <= 0:
                secret_name = f"/databases/dev/dev/iris"
                region_name = "us-east-1"
                # Create a Secrets Manager client
                session = boto3.session.Session()
                print(f'!!!session: {session}')
                print(f'!!!caller: {boto3.client("sts").get_caller_identity()}')
                client = session.client(
                    service_name='secretsmanager',
                    region_name=region_name,
                )
                get_secret_value_response = client.get_secret_value(
                    SecretId=secret_name
                )
                print(f'!!!get_secret_value_response: {get_secret_value_response}')
                # Decrypts secret using the associated KMS key.
                secret_db_creds = get_secret_value_response['SecretString']
                print('!!!!!secret: ' + secret_db_creds)

                # client = boto3.client("ssm")
                session = boto3.session.Session()
                client = session.client(
                    service_name='ssm',
                    region_name=region_name,
                )
                # secret_name = f"/database-hosts"

                secret_name = f"/database-hosts/dev/us-east-1/crmdev/crmdv_tools_svc"
                # Response will contain the parameter along with metadata
                crm_details = client.get_parameter(
                    Name=secret_name
                )
                crm_details = crm_details['Parameter']['Value']
                print(' parameter for database hosts crm : ', crm_details)

                secret_name = f"/database-hosts/dev/us-east-1/synapse/dev"
                # Response will contain the parameter along with metadata
                synapse_details = client.get_parameter(
                    Name=secret_name
                )
                synapse_details = synapse_details['Parameter']['Value']
                print(' parameter for database hosts synapse : ', synapse_details)

                secret_name = f"/database-hosts/dev/us-east-1/ssdtools/ssdtools"
                # Response will contain the parameter along with metadata
                pg_details = client.get_parameter(
                    Name=secret_name
                )
                pg_details = pg_details['Parameter']['Value']
                print(' parameter for database hosts pg : ', pg_details)

                # hostname = "https://" + host_name
                # vault_client = hvac.Client(url=hostname)
                #
                # self.logger.info("Role id : " + self.role_id)
                # self.logger.info("Hostname : " + hostname)
                #
                # # with open(self.project_path + '/tmp/secret.txt', 'r') as f:
                # # with open('/tmp/secret.txt', 'r') as f:
                #     # secret_key = f.readline()
                # # self.logger.debug('sec  ', secret_key)
                #
                # session = boto3.Session()
                # self.logger.info('Session Created in Vault')
                # session_credentials = session.get_credentials()
                # self.logger.info(session_credentials)
                #
                # # For deploying app using IAM Permissions
                #
                # vault_client.auth_aws_iam(session_credentials.access_key, session_credentials.secret_key,
                #                           session_credentials.token,
                #                           header_value=host_name,
                #                           role=self.vault_role, region="us-east-1", use_token=True)
                #
                # # For deploying app using APP Role Permissions
                # vault_client.auth_approle(self.role_id, secret_key)
                # vault_cred_json["app"] = vault_client.read(self.vault_app_secret_path)
                # vault_cred_json["db"] = vault_client.read(self.vault_db_secret_path)
                # vault_cred_json["pg_host"] = vault_client.read(self.vault_pg_host_secret_path)
                # vault_cred_json["baw_host"] = vault_client.read(self.vault_baw_host_secret_path)
                # vault_cred_json["azure_host"] = vault_client.read(self.vault_azure_host_secret_path)
                # vault_cred_json["crm_host"] = vault_client.read(self.vault_crm_host_secret_path)
                vault_cred_json["app"] = {}
                vault_cred_json["db"] = {'data': json.loads(secret_db_creds)}
                vault_cred_json["pg_host"] = {'data': json.loads(pg_details)}
                vault_cred_json["baw_host"] = {}
                vault_cred_json["azure_host"] = {'data': json.loads(synapse_details)}
                vault_cred_json["crm_host"] = {'data': json.loads(crm_details)}
                print('final secret manager structure output : ', vault_cred_json)
            else:
                #self.logger.warning("Vault_config : vault cred json already exists")
                print("Vault_config : vault cred json already exists")

        except Exception as e:
            if e.code == -1003:
                self.logger.error("Too many request")
                print("Too many request")
            else:
                # self.logger.error('------------- Exception, can not connect with vault --------------------')
                # self.logger.error(str(e))
                print('------------- Exception, can not connect with vault --------------------')
                return e
        else:
            # self.logger.info("---------------- Vault_config : vault cred json created -------------")
            # self.logger.info('----------------- Printing Vault Cred Json ---------------')
            # self.logger.info(vault_cred_json)
            print("---------------- Vault_config : vault cred json created -------------")
            print('----------------- Printing Vault Cred Json ---------------')
            print(vault_cred_json)
            return vault_cred_json
