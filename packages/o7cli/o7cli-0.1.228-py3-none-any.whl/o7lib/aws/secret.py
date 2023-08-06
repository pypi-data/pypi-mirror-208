#************************************************************************
# Copyright 2023 O7 Conseils inc (Philippe Gosselin)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************
"""Module allows to view and access Secrets"""


#--------------------------------
#
#--------------------------------
import pprint
import logging
import json
import ast

import o7lib.util.input
import o7lib.util.displays
import o7lib.aws.base


logger=logging.getLogger(__name__)



#*************************************************
#
#*************************************************
class Secret(o7lib.aws.base.Base):
    """Class for Secrets Manager """

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None):
        super().__init__(profile=profile, region=region)
        self.secret = self.session.client('secretsmanager')



    #*************************************************
    #
    #*************************************************
    def load_secrets(self):
        """Load all secret in Region"""

        logger.info('load_parameters')

        secrets = []
        param={
            'IncludePlannedDeletion' : False,
            'MaxResults' : 50
        }

        done=False
        while not done:

            resp = self.secret.list_secrets(**param)
            #pprint.pprint(resp)

            if 'NextToken' in resp:
                param['NextToken'] = resp['NextToken']
            else:
                done = True

            found_params = resp.get('SecretList',[])
            logger.info(f'load_parameters: Number of Secret found {len(found_params)}')
            secrets.extend(found_params)

        return secrets

    #*************************************************
    #
    #*************************************************
    def load_secret_value(self, secret_name : str):
        """Load  a single secret"""

        logger.info(f'load_secret_value: secret_name={secret_name}')
        # secret_info = self.secret.describe_secret(SecretId=secret_name)

        secret_value = self.secret.get_secret_value(
            SecretId=secret_name
        )

        return secret_value


    #*************************************************
    #
    #*************************************************
    def display_secrets(self, parameters):
        """Diplay Parameters"""
        self.ConsoleTitle(left='Secret Managers List')
        print('')
        params = {
            'columns' : [
                {'title' : 'id',          'type': 'i',    'minWidth' : 4  },
                {'title' : 'Name',        'type': 'str',  'dataName': 'Name'},
                {'title' : 'Description', 'type': 'str',  'dataName': 'Description'},
                {'title' : 'Rotation?',        'type': 'str',  'dataName': 'RotationEnabled'},
            ]
        }
        o7lib.util.displays.Table(params, parameters)

    #*************************************************
    #
    #*************************************************
    # def display_parameter(self, parameter_info : dict, parameter_last : dict):
    #     """Diplay Parameters"""
    #     self.ConsoleTitle(left='SSM Parameter')
    #     print('')
    #     print(f'Name: {parameter_info["Name"]}')
    #     print(f'Description: {parameter_info.get("Description","")}')
    #     print('')
    #     print(f'Value: {parameter_last.get("Value","")}')
    #     print('')
    #     print(f'Version: {parameter_last.get("Version","")}')
    #     print(f'LastModifiedDate: {parameter_last.get("LastModifiedDate",datetime.datetime.fromtimestamp(0)).isoformat()}')
    #     print('')
    #     print(f'Type: {parameter_info.get("Type","")}')
    #     print(f'DataType: {parameter_info.get("DataType","")}')
    #     print(f'Tier: {parameter_info.get("Tier","")}')
    #     print(f'Type: {parameter_info.get("Type","")}')
    #     print('')


    #*************************************************
    #
    #*************************************************
    def menu_secret(self, parameter_info):
        """Single Parameter view & edit menu"""

        while True :

            secret_data = self.load_secret_value(parameter_info.get('Name'))

            secret_value = secret_data.get('SecretString','NA')

            secret_dict = json.loads(secret_value)
            pprint.pprint(secret_dict)

            o7lib.util.input.InputString('Press Enter to continue')
            return
            # exit(0)

            # self.display_parameter(parameter_info = parameter_info, parameter_last = parameter)
            # key_type, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Change Value (c): ')

            # if key_type == 'str':
            #     if key.lower() == 'b':
            #         break

            # if key.lower() == 'c':
            #     new_value = o7lib.util.input.InputString('Enter New Value : ')
            #     if new_value is None:
            #         continue

            #     if not o7lib.util.input.IsItOk(f'Confirm value -> {new_value}') :
            #         continue

            #     self.ssm.put_parameter(Name=parameter_info.get('Name'), Value=new_value, Type=parameter_info.get('Type'), Overwrite=True)



    #*************************************************
    #
    #*************************************************
    def menu_secrets(self):
        """All Secrets view """

        while True :

            secrets = self.load_secrets()
            self.display_secrets(secrets)
            key_type, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Details(int): ')

            if key_type == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(secrets)
                    o7lib.util.input.WaitInput()

            if key_type == 'int' and  0 < key <= len(secrets):
                self.menu_secret(parameter_info=secrets[key-1])

#*************************************************
#
#*************************************************
def menu(**kwargs):
    """Run Main Menu"""
    Secret(**kwargs).menu_secrets()

#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    Secret().menu_secrets()
