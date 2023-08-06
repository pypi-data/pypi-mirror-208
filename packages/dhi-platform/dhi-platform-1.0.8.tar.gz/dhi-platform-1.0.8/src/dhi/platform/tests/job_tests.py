import time
import unittest
import datetime
from dhi.platform.base.exceptions import MikeCloudRestApiException
from dhi.platform.generated.jobgen import ContainerInputV1, ContainerRuntimeSpecV1, CronJobDefinitionInputV1, InputDataSpecV1, JobDefinitionInputV1, JobStateTypeV1, OutputDataSpecV1, PlatformInputLocationV1, PlatformOutputLocationV1
from .testcredentials import TEST_IDENTITY
from dhi.platform import job, metadata
import os


class TestJobTest(unittest.TestCase):

    _verbosity = 0
    _project_id = None
    _identity = None
    _test_data_dir = None
    
    def setUp(self) -> None:
        if not self._identity:
            self._identity = TEST_IDENTITY
        
        self._jobclient = job.JobClient(
            verbose=self._verbosity, 
            identity=self._identity
        )

        self._metadataclient = metadata.MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)

        self._test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self._stamp = stamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        if not self._project_id:
            name = 'Python test job' + self._stamp
            projectInput = metadata.CreateProjectInput(name, 'Project created by Python SDK test')
            project = self._metadataclient.create_project(projectInput)
            self._project_id = project.id

    def tearDown(self) -> None:
        super().tearDown()
        if self._project_id:
            self._metadataclient.delete_project(self._project_id, permanently=True)
        
    def test_job_execution_is_ok(self):

        containers = [
            ContainerInputV1(
                image="mcr.microsoft.com/dotnet/aspnet:7.0-jammy", 
                command=["/bin/sh", "-c", "echo 'hi'; sleep 10"]
            )
        ]
        runtime_spec = ContainerRuntimeSpecV1(containers)
        input_data = InputDataSpecV1([PlatformInputLocationV1(projectId=self._project_id)])
        
        input = JobDefinitionInputV1(runtime_spec, input_data, outputData=None)

        job = self._jobclient.execute_job_and_wait(self._project_id, input, timeout_minutes=10, polling_interval_seconds=10)
        
        self.assertEqual(job.jobState, JobStateTypeV1.FINISHED)

    def test_create_get_list_delete_cron_job_is_ok(self):
        
        containers = [
            ContainerInputV1(
                image="mcr.microsoft.com/dotnet/aspnet:7.0-jammy", 
                command=["/bin/sh", "-c", "echo 'hi'; sleep 10"]
            )
        ]
        input = CronJobDefinitionInputV1(ContainerRuntimeSpecV1(containers), schedule="* * 1 * *")
        
        cron_job = self._jobclient.create_cron_job(self._project_id, input)

        self.assertTrue(cron_job.cronJobId is not None)
        self.assertEqual(cron_job.projectId, self._project_id)

        cron_job_got = self._jobclient.get_cron_job(self._project_id, cron_job.cronJobId)

        self.assertEqual(cron_job.cronJobId, cron_job_got.cronJobId)
        self.assertEqual(cron_job.projectId, cron_job_got.projectId)
        self.assertEqual(cron_job.schedule, cron_job_got.schedule)

        cron_jobs = self._jobclient.list_cron_jobs(self._project_id)

        listed = [cj for cj in cron_jobs if cj.cronJobId == cron_job.cronJobId]
        self.assertEqual(len(listed), 1)

        self._jobclient.remove_cron_job(self._project_id, cron_job.cronJobId)
        
        cron_jobs = self._jobclient.list_cron_jobs(self._project_id)
        listed = [cj for cj in cron_jobs if cj.cronJobId == cron_job.cronJobId]
        self.assertEqual(len(listed), 0)

        self.assertRaises(MikeCloudRestApiException, self._jobclient.get_cron_job, self._project_id, cron_job.cronJobId)


if __name__ == "__main__":
    unittest.main()