import unittest
import datetime
import os
import filecmp
from dhi.platform import metadata, transfer
from .testcredentials import TEST_IDENTITY

class TestUploadDownload(unittest.TestCase):

    _verbosity = 0
    
    def setUp(self) -> None:
        self._metadataclient = metadata.MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._transferclient = transfer.TransferClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        name = 'Python upload/download test ' + stamp
        projectInput = metadata.CreateProjectInput(name, 'Project created from Python')
        self._project = self._metadataclient.create_project(projectInput)

    def tearDown(self) -> None:
        self._metadataclient.delete_project(self._project.id, permanently=True)
        if os.path.exists(self._downloaded_file):
            os.remove(self._downloaded_file)

    def test_file_upload_download_is_ok(self):
        test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        local_file = os.path.join(test_data_dir, 'esbjergSmall.txt')
        project_id = self._project.id

        dataset_id = self._transferclient.upload_file(local_file, project_id, verbose=True)

        self.assertTrue(dataset_id)

        downloaded_file = self._transferclient.download_file(project_id, dataset_id, local_file + '.downloaded', verbose=True)
        
        self.assertTrue(os.path.exists(downloaded_file))
        self.assertTrue(filecmp.cmp(local_file, downloaded_file, shallow=False))

        self._downloaded_file = downloaded_file

    
if __name__ == "__main__":
    unittest.main()