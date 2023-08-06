# Copyright (c) 2021 DHI A/S - DHI Water Environment Health 
# All rights reserved.
# 
# This code is licensed under the MIT License.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import datetime
import time
from typing import List

from dhi.platform.base.exceptions import MikeCloudException
from .generated.jobgen import CronJobDefinitionInputV1, CronJobOutputCollectionResponseV1, CronJobOutputV1, JobDefinitionInputV1, JobGenClientV1, JobLogsOutputV1, JobOutputV1, JobStateTypeV1


class JobClient(JobGenClientV1):
    def __init__(self, inspectFnc=JobGenClientV1.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)
    
    def get_job(self, project_id, job_id) -> JobOutputV1:
        """
        Get job details
        
        :param project_id: ID of the project to get a job from
        :param job_id: ID of the job
        :return: job details
        :rtype: JobOutputV1
        """
        response = super().GetJob(project_id, job_id)
        return JobOutputV1.from_dict(response.Body)
    
    def get_job_logs(self, project_id, job_id, taillines:int = None) -> JobLogsOutputV1:
        """
        Get job details
        
        :param project_id: ID of the project to get a job from
        :param job_id: ID of the job
        :param taillines: Optional integer indicating how many lines of log to include
        :return: job logs
        :rtype: JobLogsOutputV1
        """
        response = super().GetJobLogs(project_id, job_id, taillines)
        return JobLogsOutputV1.from_dict(response.Body)
    
    def cancel_job(self, project_id, job_id) -> bool:
        """
        Cancel job
        
        :param project_id: ID of the project to cancel a job in
        :param job_id: ID of the job
        :return: True if request was successful, raises otherwise
        :rtype: bool
        """
        response = super().CancelJob(project_id, job_id)
        return response.IsOk
    
    def create_cron_job(self, project_id, input:CronJobDefinitionInputV1) -> CronJobOutputV1:
        """
        Get job details
        
        :param project_id: ID of the project to create a cron job in
        :param input: cron job definition
        :return: cron job details
        :rtype: CronJobOutputV1
        """
        response = super().CreateCronJob(project_id, input.to_dict())
        return CronJobOutputV1.from_dict(response.Body)
    
    def get_cron_job(self, project_id, cron_job_id) -> CronJobOutputV1:
        """
        Get cron job details
        
        :param project_id: ID of the project to get a job from
        :param cron_job_id: ID of the cron job
        :return: cron job details
        :rtype: CronJobOutputV1
        """
        response = super().GetCronJob(project_id, cron_job_id)
        return CronJobOutputV1.from_dict(response.Body)
    
    def execute_job(self, project_id, input:JobDefinitionInputV1) -> JobOutputV1:
        """
        Get job details
        
        :param project_id: ID of the project to execute a job in
        :param input: job definition
        :return: job details
        :rtype: JobOutputV1
        """
        response = super().ExecuteJob(project_id, input.to_dict())
        return JobOutputV1.from_dict(response.Body)
    
    def execute_job_and_wait(
            self, 
            project_id, 
            input:JobDefinitionInputV1, 
            timeout_minutes = 60, 
            polling_interval_seconds = 30,
            progress_reporter = lambda j: print('UTC', datetime.datetime.now(), j.jobId, j.jobState, j.statusMessage),
            log_reporter = None,
            log_on_error_reporter = lambda lg: print('==> Container ', lg.containerName, lg.log),
            cancel_job_on_timeout = False,
            raise_on_timeout = True
        ) -> JobOutputV1:
        """
        Execute job and wait until it finishes.

        :param project_id:
        :param input: job definition
        :param timeout_minutes: How many minutes should this client wait for the job to finish
        :param polling_interval_seconds: How often should this client check the job status while the job is running
        :param progress_reporter: callable that takes the job as input and is called every polling_interval_seconds, or None for no reporting
        :param log_reporter: callable that takes job log as a parameter and is called every polling_interval_seconds, or None for no reporting
        :param log_on_error_reporter: callable that takes the job log as a parmeter and is called when the job fails, or None for no reporting
        :param cancel_job_on_timeout: cancel the job if it runs for more than timeout_minutes, default is False
        :param raise_on_timeout: raise MikeCloudException when the job runs for more than timeout_minutes, default is True
        :return: job details
        :rtype: JobOutputV1
        """
        job = self.execute_job(project_id, input)
        t = datetime.datetime.utcnow()
        timeout = timeout_minutes * 60
        elappsed_time = datetime.datetime.utcnow() - t
        
        while elappsed_time.total_seconds() < timeout:
            job = self.get_job(project_id, job.jobId)
            
            if progress_reporter is not None:
                progress_reporter(job)
            
            if job.jobState == JobStateTypeV1.FINISHED:
                break

            if log_reporter is not None:
                logs = self.get_job_logs(project_id, job.jobId)
                for lg in logs.logs:
                    log_reporter(lg)
            
            if job.hasError and log_on_error_reporter is not None:
                logs = self.get_job_logs(project_id, job.jobId)
                for lg in logs.logs:
                    log_on_error_reporter(lg)

            time.sleep(polling_interval_seconds)
            elappsed_time = datetime.datetime.utcnow() - t
        
        if elappsed_time.total_seconds() >= timeout:
            if cancel_job_on_timeout:
                self.cancel_job(project_id, job.jobId)
            if raise_on_timeout:
                raise MikeCloudException(f"Job monitoring timed out but the job {job.jobId} last job state was {job.jobState}")
            
        return job
    
    def list_cron_jobs(self, project_id) -> List[CronJobOutputV1]:
        """
        List cron job definitions
        
        :param project_id: ID of the project to get cron jobs from
        :return: list of cron job details
        :rtype: List[CronJobOutputV1]
        """
        response = super().GetCronJobList(project_id)
        collection = CronJobOutputCollectionResponseV1.from_dict(response.Body)
        return collection.data
    
    def remove_cron_job(self, project_id, cron_job_id) -> bool:
        """
        Remove cron job
        
        :param project_id: ID of the project to remove cron job from
        :param cron_job_id: Cron Job ID
        :return: True if request is successful, raises otherwise
        :rtype: bool
        """
        response = super().RemoveCronJob(project_id, cron_job_id)
        return response.IsOk

if __name__ == '__main__':
    print(__file__)
    print(dir())
