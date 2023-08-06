import unittest
import datetime
import os
from dhi.platform import metadata, multidimensional, transfer
from dhi.platform.commonmodels import SpatialFilter, TemporalFilter
from dhi.platform.protobufparser.enums import DataBlockIndex
from .testcredentials import TEST_IDENTITY

class TestMultidimensional(unittest.TestCase):

    _verbosity = 0
    
    def setUp(self) -> None:
        self._metadataclient = metadata.MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._transferclient = transfer.TransferClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._mdclient = multidimensional.MultidimensionalClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self._projects_to_delete = []

        self._output = multidimensional.BinaryQueryOutput()
        self._blocks = []
        self._mesh_reader = multidimensional.MeshBinaryReader()
        self._binary_options = multidimensional.BinaryOptions(1, 1, 5, True)

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

    def test_query_timestep_is_ok(self):
        project = self._create_project()
        self._projects_to_delete.append(project.id)
        local_file = os.path.join(self._test_data_dir, 'EqD2.dfs2')
        
        transfer_process = self._transferclient \
            .create_file_import(project.id, local_file) \
            .with_dfs2_reader() \
            .with_multidimensional_writer() \
            .execute_and_wait()
        
        self.assertIsNotNone(transfer_process)
        self.assertIsNotNone(transfer_process.dataset_id)

        dataset_id = transfer_process.dataset_id

        dataset = self._mdclient.get_dataset(project.id, dataset_id)

        self.assertIsNotNone(dataset)
        self.assertIsNotNone(dataset.id)

        geom = "POLYGON((833978 0, 834000 0, 834000 500, 833978 500, 833978 0))"
        srid = 600030
        
        output = self._mdclient.query_timesteps(
            project.id, 
            dataset_id, 
            SpatialFilter(geom, srid),
            TemporalFilter.create_index_filter(0, 1),
            None,
            [0]
        )

        self.assertIsNotNone(output)
        self.assertFalse(output.time_steps) # time steps are only available in query_timeseries method result
        self.assertEqual(output.binary_protocol_version, (1, 1, 0, 0))
        self.assertEqual(output.srid, 600030)
        self.assertEqual(len(output.elements), 30)
        self.assertFalse(output.mesh_pages) # mesh pages are only available when querying mesh multidimensional dataset
        
        self.assertTrue(len(output.data_blocks) == 2)
        first_data_block = output.data_blocks[0]
        self.assertEqual(first_data_block.indexes[DataBlockIndex.ITEM], 0)
        self.assertEqual(first_data_block.indexes[DataBlockIndex.TEMPORAL], 2)
        self.assertEqual(first_data_block.indexes[DataBlockIndex.LAYER], 1)
        float_data = first_data_block.get_data_float()
        self.assertEqual(len(float_data), 30)


if __name__ == "__main__":
    unittest.main()