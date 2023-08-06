#!/usr/bin/env python
#************************************************************************
# Copyright 2021 O7 Conseils inc (Philippe Gosselin)
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
"""Module for O7 Command Line Interface"""

#--------------------------------
#
#--------------------------------
import sys
import argparse
import logging
import pkg_resources

import botocore

import o7lib.aws.reports
import o7lib.aws.costexplorer
import o7lib.aws.cloudformation
import o7lib.aws.ec2
import o7lib.aws.ecs
import o7lib.aws.s3
import o7lib.aws.asg
import o7lib.aws.cloudmap
import o7lib.aws.lambdafct
import o7lib.aws.rds
import o7lib.aws.pipeline
import o7lib.aws.codebuild
import o7lib.aws.codecommit
import o7lib.aws.logs
import o7lib.aws.ssm_ps
import o7lib.aws.secret
import o7lib.version
import o7lib.util.pypi
import o7lib.util.displays


logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
def credential_help():
    """Print help about credential issues"""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration
    print('There are different way to configure your AWS credentials')
    print('ref: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration')
    print('')
    print('- If you have the AWS CLI install, use -> aws configure')
    print('- Else, create your own credential file (see ref link)')
    print('')
    print('Note: o7 supports the usage of multiple profile, option -p')
    print('')


#*************************************************
#
#*************************************************
def version_verification():
    """Verify if runngin latest version and notify accordingly"""

    lastest_version = o7lib.util.pypi.Pypi(project='o7cli').GetLatestVersion()

    if o7lib.version.VERSION_ID == 'LOCAL_VERSION':
        o7lib.util.displays.PrintWarning(f'You are using a LOCAL VERSION, latest release is {lastest_version}')

    elif lastest_version is not None:
        if pkg_resources.parse_version(lastest_version) > pkg_resources.parse_version(o7lib.version.VERSION_ID):
            o7lib.util.displays.PrintWarning(f'You are using version o7cli {o7lib.version.VERSION_ID}, however, version {lastest_version} is available.')
            o7lib.util.displays.PrintWarning("Please consider upgrading via the 'pip install --upgrade o7cli' command.")

#*************************************************
#
#*************************************************
def command_line(argv): # pylint: disable=too-many-statements,too-many-locals
    """Main Menu for CLI"""

    version_verification()

    parser = argparse.ArgumentParser(
        prog='o7',
        description='Useful CLI and scripts for O7 Conseils DevOps practice',
        epilog=f'version: {o7lib.version.VERSION_ID}'
    )

    parser.add_argument('-p', '--profile', dest='profile', help='AWS Profile')
    parser.add_argument('-r', '--region', dest='region', help='AWS Region')
    parser.add_argument('-d', '--debug', dest='debug', help='Enable Debug Traces', action='store_true')
    parser.add_argument('-v', '--version', dest='version', help='Print version', action='store_true')



    subparsers = parser.add_subparsers(title='O7 Module', description='Select a target module', metavar='MODULE', help=None, required=False)

    parser_report = subparsers.add_parser('report', help='Conformity report')
    parser_report.set_defaults(func=o7lib.aws.reports.run_conformity)

    parser_cost = subparsers.add_parser('cost', help='Analyse account cost')
    parser_cost.set_defaults(func=o7lib.aws.costexplorer.menu)

    parser_log= subparsers.add_parser('log', help='Cloudwatch Logs')
    parser_log.set_defaults(func=o7lib.aws.logs.menu)

    parser_ps = subparsers.add_parser('ps', help='SSM - Parameter Store')
    parser_ps.set_defaults(func=o7lib.aws.ssm_ps.menu)

    parser_secret = subparsers.add_parser('secret', help='Secrets Manager')
    parser_secret.set_defaults(func=o7lib.aws.secret.menu)

    parser_cm = subparsers.add_parser('cm', help='Cloud Map')
    parser_cm.set_defaults(func=o7lib.aws.cloudmap.menu)

    parser_s3 = subparsers.add_parser('s3', help='S3 (Simple Scalable Storage)')
    parser_s3.set_defaults(func=o7lib.aws.s3.menu)

    parser_rds = subparsers.add_parser('rds', help='Relational DB')
    parser_rds.set_defaults(func=o7lib.aws.rds.menu)

    parser_ec2 = subparsers.add_parser('ec2', help='Elastic Computing')
    parser_ec2.set_defaults(func=o7lib.aws.ec2.menu)

    parser_ecs = subparsers.add_parser('ecs', help='Elastic Container Service')
    parser_ecs.set_defaults(func=o7lib.aws.ecs.menu)

    parser_lf = subparsers.add_parser('lf', help='Lambda Functions')
    parser_lf.set_defaults(func=o7lib.aws.lambdafct.menu)

    parser_asg = subparsers.add_parser('asg', help='Auto Scaling Group')
    parser_asg.set_defaults(func=o7lib.aws.asg.menu)

    parser_cfn = subparsers.add_parser('cf', help='Cloudformation')
    parser_cfn.set_defaults(func=o7lib.aws.cloudformation.menu)

    parser_pl = subparsers.add_parser('pl', help='Code Pipeline')
    parser_pl.set_defaults(func=o7lib.aws.pipeline.menu)

    parser_cb = subparsers.add_parser('cb', help='Code Build')
    parser_cb.set_defaults(func=o7lib.aws.codebuild.menu)

    parser_cc = subparsers.add_parser('cc', help='Code Commit')
    parser_cc.set_defaults(func=o7lib.aws.codecommit.menu)

    args = parser.parse_args()
    param = {
        'profile' : args.profile,
        'region' : args.region
    }

    if args.debug:
        print('Setting debug mode')
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)-5.5s] [%(name)s] %(message)s"
        )

    if args.version:
        print(f'{o7lib.version.VERSION_ID}')
        sys.exit(0)

    if not hasattr(args, 'func'):
        parser.print_usage()
        sys.exit(0)


    try :
        args.func(**param)

    except botocore.exceptions.NoRegionError:
        o7lib.util.displays.PrintError('ERROR! No AWS default region found')
        print('')
        print ("use -r option OR set an AWS Default Region ('export AWS_DEFAULT_REGION=ca-central-1') ")

    except botocore.exceptions.NoCredentialsError:
        o7lib.util.displays.PrintError('ERROR! No AWS credential found')
        print('')
        credential_help()

    except botocore.exceptions.ProfileNotFound:
        o7lib.util.displays.PrintError('ERROR! Profile do not exist')

    except KeyboardInterrupt:

        print (f'{o7lib.util.displays.Colors.ENDC}\nGoodby...')



#*************************************************
#
#*************************************************
def main():
    """Callable from Script"""
    command_line(sys.argv[1:])


#*************************************************
#
#*************************************************
if __name__ == "__main__":
    command_line(sys.argv[1:])
