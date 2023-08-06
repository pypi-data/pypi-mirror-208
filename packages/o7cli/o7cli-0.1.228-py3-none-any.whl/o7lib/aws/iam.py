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


import logging
import pprint

import o7lib.util.report
import o7lib.aws.base
import o7lib.aws.eventbridge

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/guardduty.html

logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class IAM(o7lib.aws.base.Base):
    """Class for AWS IAM"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session = session)
        self.iam = self.session.client('iam')


    #*************************************************
    #
    #*************************************************
    def ConformityReport(self, report : o7lib.util.report.Report = None):
        """Conformity Report"""

        r = report
        if r is None: r = o7lib.util.report.Report('Account Conformity Report', sectionName="IAM")
        else: r.AddSection("IAM")

        resp = self.iam.get_account_summary()
        summary = resp.get('SummaryMap', {})


        # pprint.pprint(summary)

        r.AddTest(name="Root Account MFA", critical=True)
        if summary.get('AccountMFAEnabled', 0) != 1:
            r.TestFail("Not Set")
        else:
            r.TestPass('Set')

        r.AddTest(name="Root Programatic Access Key", critical=True)

        if summary.get('AccountAccessKeysPresent', 1) != 0:
            r.TestFail("Present (should be removed)")
        else:
            r.TestPass('None')


        return True


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    IAM().ConformityReport()