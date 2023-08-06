import unittest
import datetime
from unittest.case import _AssertRaisesContext
from dhi.platform import metadata, sharing, timeseries
from dhi.platform.base.exceptions import MikeCloudRestApiException
from .testcredentials import TEST_IDENTITY

class TestPublications(unittest.TestCase):

    _verbosity = 0
    
    def setUp(self) -> None:
        self._metadataclient = metadata.MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._timeseriesclient = timeseries.TimeSeriesClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._sharingclient = sharing.SharingClient(verbose=self._verbosity, identity=TEST_IDENTITY)
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

    def skip_test_create_update_delete_publication_is_ok(self):
        project = self._create_project()
        self._projects_to_delete.append(project.id)

        t = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        ds_name = "Py TS"
        ds_description = "Test TS dataset"
        dataset_id = self._create_ts_dataset(project.id, ds_name, ds_description)

        dataset = self._metadataclient.get_dataset(dataset_id)
        self.assertIsNotNone(dataset)

        tenant_id = '980552ba-58a1-4742-9248-cbcf3b3a4ece' # dhi1 in DEV0
        #catalog_id = self._sharingclient.create_catalog(tenant_id, sharing.CreateCatalogInput(f"Pytest test catalog {t}"))
        catalog_id = '70e9d380-9ac5-4d1e-a3e2-8fd00e715da6' # FIKR's catalog in DEV0

        catalogs = list(self._sharingclient.list_catalogs(project.id))

        self.assertTrue(len(catalogs) > 0)

        publication_id = self._sharingclient.create_publication(project.id, sharing.CreatePublicationInput(f"PyTest {t}", catalog_id, dataset.id, "Pytest publication", {"foo": "bar"}))

        publication = self._sharingclient.get_publication(project.id, publication_id)

        publication_updated = self._sharingclient.update_publication(project.id, sharing.EditPublicationInput(publication_id, publication.name, publication.resource_id, metadata = {"foo": "spam", "eggs": 1}, row_version=publication.row_version))

        self.assertEqual(publication_updated.name, publication.name)
        self.assertEqual(publication_updated.metadata["foo"], "spam")
        self.assertEqual(publication_updated.metadata["eggs"], 1)

        self._sharingclient.delete_publication(project.id, publication_id, publication.resource_id)

        deleted = self._metadataclient.delete_dataset(dataset_id, permanently=True)
        self.assertTrue(deleted)


if __name__ == "__main__":
    unittest.main()