import unittest
import datetime
from dhi.platform.generated.enginegen import EngineInputItemV2, EngineModelItemV2
from .testcredentials import TEST_IDENTITY
from dhi.platform import eventing, metadata, transfer, engine
import os


class TestEngineTest(unittest.TestCase):

    _verbosity = 0
    _project_id = None
    _identity = None
    _test_data_dir = None
    
    def setUp(self) -> None:
        if not self._identity:
            self._identity = TEST_IDENTITY
        
        self._engine = engine.EngineClient(
            verbose=self._verbosity, 
            identity=self._identity
        )

        self._metadataclient = metadata.MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._transferclient = transfer.TransferClient(verbose=self._verbosity, identity=TEST_IDENTITY)

        self._test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self._stamp = stamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        if not self._project_id:
            name = 'Python test engine' + self._stamp
            projectInput = metadata.CreateProjectInput(name, 'Project created by Python SDK test')
            project = self._metadataclient.create_project(projectInput)
            self._project_id = project.id

    def tearDown(self) -> None:
        super().tearDown()
        if self._project_id:
            self._metadataclient.delete_project(self._project_id, permanently=True)
        
    def test_engine_execution_is_ok(self):

        input = [
            EngineInputItemV2("https://coreenginedev0inputs.blob.core.windows.net/data/lake.m21fm", engine="FemEngineHD"),
            EngineInputItemV2("https://coreenginedev0inputs.blob.core.windows.net/data/lake.mesh")
        ]

        pool_type = "VM-S-5" 
        # you can list different pool types, e.g. self._engine.list_configurations(project_id)[0].poolType

        engine_subscription = eventing.EngineSubscription()
        
        event_subscription = eventing.EventSubscriptionBuilder(self._metadataclient, self._project_id)\
            .with_message_handler(lambda m: print(m))\
            .with_on_close_handler(lambda: print("connection closed"))\
            .with_eventing_error_handler(lambda: print("An error during eventing"))\
            .with_engine_handler(engine_subscription, lambda m: print("Success", m), lambda m: print("Failure", m), lambda m: print("Cancelled", m))\
            .build()
        
        parameters = engine.EngineExecutionInputBuilder()\
            .with_input(input)\
            .with_options(pool_type, node_count=1)\
            .with_max_execution_elapsed_time_hours(1)\
            .build()
        
        event_subscription.start_and_subscribe()

        execution = self._engine.run_execution(self._project_id, parameters, engine_subscription)

        engine_subscription.wait()
        event_subscription.stop()

        executionDone = self._engine.get_execution(self._project_id, execution.executionId)
        
        self.assertEqual(execution.executionId, executionDone.executionId)    

    def test_engine_execution_with_platform_data_is_ok(self):
        
        print("Uploading some data...")

        transfer_process1 = self._transferclient.create_url_import(
            self._project_id, "https://coreenginedev0inputs.blob.core.windows.net/data/lake.m21fm", "lake.m21fm")\
            .execute_and_wait()
        
        print(f"Uploaded dataset {transfer_process1.dataset_id}")

        transfer_process2 = self._transferclient.create_url_import(
            self._project_id, "https://coreenginedev0inputs.blob.core.windows.net/data/lake.mesh", "lake.mesh")\
            .execute_and_wait()

        print(f"Uploaded dataset {transfer_process2.dataset_id}")

        models = [
            EngineModelItemV2(modelFileName="lake.m21fm", engine="FemEngineHD", overwriteResultsIfExists=True, resultsRelativePath="results")
        ]

        pool_type = "VM-S-5" 
        # you can list different pool types, e.g. self._engine.list_configurations(project_id)[0].poolType
      
        engine_subscription = eventing.EngineSubscription()

        event_subscription = eventing.EventSubscriptionBuilder(self._metadataclient, self._project_id)\
            .with_message_handler(lambda m: print(m))\
            .with_on_close_handler(lambda: print("connection closed"))\
            .with_eventing_error_handler(lambda: print("An error during eventing"))\
            .with_engine_handler(engine_subscription, lambda m: print("Success", m), lambda m: print("Failure", m), lambda m: print("Cancelled", m))\
            .build()
        
        parameters = engine.EngineExecutionInputParametersBuilder()\
            .with_models(models)\
            .with_options(pool_type, node_count=1)\
            .with_max_execution_elapsed_time_hours(1)\
            .build()
        
        event_subscription.start_and_subscribe()

        execution = self._engine.run_execution_with_platform_data(self._project_id, parameters, engine_subscription)

        engine_subscription.wait()
        event_subscription.stop()

        executionDone = self._engine.get_execution(self._project_id, execution.executionId)
        
        self.assertEqual(execution.executionId, executionDone.executionId)

if __name__ == "__main__":
    unittest.main()