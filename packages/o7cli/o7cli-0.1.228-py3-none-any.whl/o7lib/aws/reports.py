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


#--------------------------------
#
#--------------------------------
import logging
import o7lib.util.report
import o7lib.aws.base
import o7lib.aws.cloudtrail
import o7lib.aws.guardduty
import o7lib.aws.costexplorer
import o7lib.aws.sts
import o7lib.aws.iam



logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Report(o7lib.aws.base.Base):
    """Class for AWS Reports"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session=session)

    #*************************************************
    #
    #*************************************************
    def Conformity(self):
        """Conformity Report"""

        r = o7lib.util.report.Report(f'Account Conformity Report - {self.TitleLine()}')
        r.AddParameter(name='Account Id', value=o7lib.aws.sts.Sts(session=self.session).GetAccountId())

        o7lib.aws.iam.IAM(session=self.session).ConformityReport(report=r)
        o7lib.aws.cloudtrail.Cloudtrail(session=self.session).ConformityReport(report=r)
        o7lib.aws.guardduty.Guardduty(session=self.session).ConformityReport(report=r)
        o7lib.aws.costexplorer.CostExplorer(session=self.session).ConformityReport(report=r)

        r.Complete()

        # TO DO
        # Pager is there

        return True


    #*************************************************
    # TBR
    #*************************************************
    def Run(self,reportName):

        if reportName == 'conformity' : self.Conformity()
        else: print(f"Unknown Report Name: {reportName}")


#*************************************************
#
#*************************************************
def run_conformity(**kwargs):
    """Run Conformity Report"""
    Report(**kwargs).Conformity()

#*************************************************
#
#*************************************************
if __name__ == "__main__":

    Report(profile='cw').Run('conformity')