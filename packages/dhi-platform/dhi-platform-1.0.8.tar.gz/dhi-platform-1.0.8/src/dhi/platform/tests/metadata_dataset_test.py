import unittest
import datetime
from unittest.case import _AssertRaisesContext
import uuid
from dhi.platform import metadata, timeseries
from dhi.platform.base.exceptions import MikeCloudRestApiException
from .testcredentials import TEST_IDENTITY

class TestCreateProject(unittest.TestCase):

    _verbosity = 0
    
    def setUp(self) -> None:
        self._metadataclient = metadata.MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._timeseriesclient = timeseries.TimeSeriesClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._projects_to_delete = []

    def tearDown(self) -> None:
        super().tearDown()
        for p in self._projects_to_delete:
            try:
                self._metadataclient.delete_project(p, permanently=True)
            except:
                pass
        self._projects_to_delete = []

    def _create_project(self, title_root="Python test ", description="Project created by Python SDK test"):
        stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        name = title_root + stamp
        projectInput = metadata.CreateProjectInput(name, description)
        project = self._metadataclient.create_project(projectInput)
        return project

    def _create_ts_dataset(self, project_id, name, description):
        dataset = self._timeseriesclient.create_timeseries_dataset_from_schema(project_id, name, description)
        return dataset.id

    def test_get_and_delete_dataset_is_ok(self):
        project = self._create_project()
        self._projects_to_delete.append(project.id)

        ds_name = "Py TS"
        ds_description = "Test TS dataset"
        dataset_id = self._create_ts_dataset(project.id, ds_name, ds_description)

        dataset = self._metadataclient.get_dataset(dataset_id)
        self.assertIsNotNone(dataset)
        self.assertTrue(ds_name, dataset.name)
        self.assertTrue(ds_name, dataset.description)

        deleted = self._metadataclient.delete_dataset(dataset_id, permanently=True)
        self.assertTrue(deleted)

    def test_list_datasets_is_ok(self):
        project = self._create_project()
        self._projects_to_delete.append(project.id)

        tsd1_id = self._create_ts_dataset(project.id, "TSD 1", "ts dataset 1")
        tsd2_id = self._create_ts_dataset(project.id, "TSD 2", "ts dataset 2")
        
        datasets = [*self._metadataclient.list_datasets(project.id)]

        self.assertTrue(datasets)
        self.assertEqual(len(datasets), 2)

    def test_list_datasets_recursive_is_ok(self):
        project = self._create_project()
        self._projects_to_delete.append(project.id)

        tsd1_id = self._create_ts_dataset(project.id, "TSD 1", "ts dataset 1")
        tsd2_id = self._create_ts_dataset(project.id, "TSD 2", "ts dataset 2")
        
        datasets = [*self._metadataclient.list_datasets_recursive(project.id)]

        self.assertTrue(datasets)
        self.assertEqual(len(datasets), 2)

    def test_update_dataset_is_ok(self):
        project = self._create_project()
        self._projects_to_delete.append(project.id)
        name = "TSD 1"
        description = "ts dataset 1"
        tsd1_id = self._create_ts_dataset(project.id, name, description)

        metadata = { "foo": "bar", "spam": 1 }

        updated_dataset = self._metadataclient.update_dataset(project.id, tsd1_id, name + "Updated", description + "Updated", metadata)

        self.assertEqual(name + "Updated", updated_dataset.name)
        self.assertEqual(description + "Updated", updated_dataset.description)
        self.assertEqual(metadata, updated_dataset.metadata)

    def test_move_dataset_is_ok(self):
        project = self._create_project()
        self._projects_to_delete.append(project.id)
        project2 = self._create_project()
        self._projects_to_delete.append(project2.id)

        dataset_id = self._create_ts_dataset(project.id, "Py TS", "Test TS dataset")

        moved = self._metadataclient.move_dataset(dataset_id, project2.id)
        self.assertTrue(moved)


if __name__ == "__main__":
    unittest.main()