#************************************************************************
# Copyright 2022 O7 Conseils inc (Philippe Gosselin)
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
"""Module allows to view and access SSM Parameter Store"""


#--------------------------------
#
#--------------------------------
import pprint
import logging
import datetime

import o7lib.util.input
import o7lib.util.displays
import o7lib.aws.base


logger=logging.getLogger(__name__)



#*************************************************
#
#*************************************************
class SsmPs(o7lib.aws.base.Base):
    """Class for SSM Parameter Store """

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None):
        super().__init__(profile=profile, region=region)
        self.ssm = self.session.client('ssm')



    #*************************************************
    #
    #*************************************************
    def load_parameters(self):
        """Load all parameters in Region"""

        logger.info('load_parameters')

        parameters = []
        param={
            'MaxResults' : 50
        }

        done=False
        while not done:

            resp = self.ssm.describe_parameters(**param)
            #pprint.pprint(resp)

            if 'NextToken' in resp:
                param['NextToken'] = resp['NextToken']
            else:
                done = True

            found_params = resp.get('Parameters',[])
            logger.info(f'load_parameters: Number of Parameters found {len(found_params)}')
            parameters.extend(found_params)

        return parameters

    #*************************************************
    #
    #*************************************************
    def load_parameter(self, parameter_name : str):
        """Load  a single parameter"""

        logger.info(f'load_parameter: parameter_name={parameter_name}')
        resp = self.ssm.get_parameter(Name=parameter_name)
        return resp.get('Parameter',{})


    #*************************************************
    #
    #*************************************************
    def display_parameters(self, parameters):
        """Diplay Parameters"""
        self.ConsoleTitle(left='SSM Parameter Store List')
        print('')
        params = {
            'columns' : [
                {'title' : 'id',          'type': 'i',    'minWidth' : 4  },
                {'title' : 'Name',        'type': 'str',  'dataName': 'Name'},
                {'title' : 'Type',        'type': 'str',  'dataName': 'Type'},
                {'title' : 'Description', 'type': 'str',  'dataName': 'Description'},
                {'title' : 'V.' ,     'type': 'int',  'dataName': 'Version'},
                {'title' : 'DataType',     'type': 'str',  'dataName': 'DataType'},

            ]
        }
        o7lib.util.displays.Table(params, parameters)

    #*************************************************
    #
    #*************************************************
    def display_parameter(self, parameter_info : dict, parameter_last : dict):
        """Diplay Parameters"""
        self.ConsoleTitle(left='SSM Parameter')
        print('')
        print(f'Name: {parameter_info["Name"]}')
        print(f'Description: {parameter_info.get("Description","")}')
        print('')
        print(f'Value: {parameter_last.get("Value","")}')
        print('')
        print(f'Version: {parameter_last.get("Version","")}')
        print(f'LastModifiedDate: {parameter_last.get("LastModifiedDate",datetime.datetime.fromtimestamp(0)).isoformat()}')
        print('')
        print(f'Type: {parameter_info.get("Type","")}')
        print(f'DataType: {parameter_info.get("DataType","")}')
        print(f'Tier: {parameter_info.get("Tier","")}')
        print(f'Type: {parameter_info.get("Type","")}')
        print('')


    #*************************************************
    #
    #*************************************************
    def menu_parameter(self, parameter_info):
        """Single Parameter view & edit menu"""

        while True :

            parameter = self.load_parameter(parameter_info.get('Name'))
            # pprint.pprint(parameter)
            self.display_parameter(parameter_info = parameter_info, parameter_last = parameter)
            key_type, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Change Value (c): ')

            if key_type == 'str':
                if key.lower() == 'b':
                    break

            if key.lower() == 'c':
                new_value = o7lib.util.input.InputString('Enter New Value : ')
                if new_value is None:
                    continue

                if not o7lib.util.input.IsItOk(f'Confirm value -> {new_value}') :
                    continue

                self.ssm.put_parameter(Name=parameter_info.get('Name'), Value=new_value, Type=parameter_info.get('Type'), Overwrite=True)



    #*************************************************
    #
    #*************************************************
    def menu_parameters(self):
        """All Parameters view """

        while True :

            parameters = self.load_parameters()
            self.display_parameters(parameters)
            key_type, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Details(int): ')

            if key_type == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(parameters)
                    o7lib.util.input.WaitInput()

            if key_type == 'int' and  0 < key <= len(parameters):
                self.menu_parameter(parameter_info=parameters[key-1])

#*************************************************
#
#*************************************************
def menu(**kwargs):
    """Run Main Menu"""
    SsmPs(**kwargs).menu_parameters()

#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    SsmPs().menu_parameters()
