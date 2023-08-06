from pathlib import Path
import unittest
import datetime
from unittest.case import _AssertRaisesContext
import tempfile

from dhi.platform import metadata, transfer
from .testcredentials import TEST_IDENTITY
import os
import hashlib
import requests

class TestTransferTestIntegration(unittest.TestCase):

    _verbosity = 0
    _project_id = None
    _projects_to_remove = []
    
    def setUp(self) -> None:
        self._metadataclient = metadata.MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._transferclient = transfer.TransferClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self._test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        
        if not self._project_id:
            stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            name = 'Python test ' + stamp
            projectInput = metadata.CreateProjectInput(name, 'Project created by Python SDK test')
            project = self._metadataclient.create_project(projectInput)
            self._project_id = project.id
            self._projects_to_remove.append(self._project_id)

            self._temp_dir = os.path.join(self._test_data_dir, 'temp' + stamp)
            os.mkdir(self._temp_dir)

    def tearDown(self) -> None:
        super().tearDown()
        for pid in self._projects_to_remove:
            self._metadataclient.delete_project(pid, permanently=True)
        
        if os.path.exists(self._temp_dir):
            import shutil
            shutil.rmtree(self._temp_dir)

    def test_get_readers_is_ok(self):
        readers = self._transferclient.get_readers()
        self.assertTrue(readers)

    def test_get_writers_is_ok(self):
        writers = self._transferclient.get_writers()
        self.assertTrue(writers)

    def test_fluent_upload_is_ok(self):
        local_file = os.path.join(self._test_data_dir, 'EqD2.dfs2')
        transfer_process = self._transferclient.create_file_import(self._project_id, local_file) \
            .with_dataset_name("PyTest") \
            .with_dataset_description("Created from python test") \
            .execute_and_wait()
        
        self.assertIsNotNone(transfer_process)
        self.assertIsNotNone(transfer_process.dataset_id)

    def test_fluent_dataset_upadte_from_dataset_is_ok(self):
        local_file = os.path.join(self._test_data_dir, 'EqD2.dfs2')

        upload1 = self._transferclient \
            .create_file_import(self._project_id, local_file) \
            .with_dfs2_reader() \
            .with_multidimensional_writer() \
            .execute_and_wait()

        upload2 = self._transferclient \
            .create_file_import(self._project_id, local_file) \
            .with_dfs2_reader() \
            .with_multidimensional_writer() \
            .execute_and_wait()

        result = self._transferclient \
            .create_dataset_update_from_dataset(upload1.dataset_id, upload2.dataset_id) \
            .execute_and_wait()
        
        self.assertTrue(isinstance(result, transfer.EmptyTransferOutput))

    def test_upload_to_multidimensional_with_allowed_items_is_ok(self):
        local_file = os.path.join(self._test_data_dir, 'EqD2.dfs2')
        reader = transfer.Dfs2Reader()
        reader.with_allowed_items("Item2")

        result = self._transferclient \
            .create_file_import(self._project_id, local_file) \
            .with_reader(reader) \
            .with_multidimensional_writer() \
            .with_coordinate_system_transformation(3857) \
            .execute_and_wait()
        
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.dataset_id)

    def test_upload_staged_files_is_ok(self):
        file_name = 'EqD2.dfs2'
        local_file = os.path.join(self._test_data_dir, file_name)
        upload_folder = "Upload" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        staging_url = self._transferclient.stage_file(local_file)
        
        input = transfer.StagedFilesUploadInput(
            files=[ transfer.StagedFileUploadInput(staging_url, file_name=file_name) ],
            destination_path=upload_folder,
            create_destination_path_if_not_exists=True
        )

        result = self._transferclient.upload_staged_files(self._project_id, input)

        self.assertEqual(len(result.datasets), 1)
        self.assertFalse(result.failures)

    def _get_remote_file_url(self, file_name):
        return f"https://coreplatformdevstor.blob.core.windows.net/int-test-input/{file_name}"

    def _download_remote_file(self, url, destination_file):
        response = requests.get(url, stream=True)
        with open(destination_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

    def stream_large_file_in_is_ok(self):
        file_name = "CiudadDelPlata_Max.dfsu"
        sotrage_url = self._get_remote_file_url(file_name)
        local_file = os.path.join(self._temp_dir, file_name)
        processed_file = os.path.join(self._temp_dir, file_name + '.downloaded')

        self._download_remote_file(sotrage_url, local_file)

        dataset_id = None
        with open(local_file, 'rb') as stream:
            transfer_process_output = self._transferclient.create_stream_import(self._project_id, stream, file_name, file_name) \
                .with_reader_and_parameters("DfsuReader") \
                .with_writer_and_parameters("FileWriter") \
                .execute_and_wait()

            dataset_id = transfer_process_output.dataset_id

        self.assertIsNotNone(dataset_id)

        self._transferclient.download_file(self._project_id, dataset_id, processed_file)

        local_md5 = ''
        with open(local_file, 'rb') as stream:
            local_md5 = hashlib.md5(stream.read()).digest()
        
        processed_md5 = ''
        with open(processed_file, 'rb') as stream:
            processed_md5 = hashlib.md5(stream.read()).digest()
        
        self.assertEqual(local_md5, processed_md5)

    def test_folder_project_upload_download(self):

        stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        name = 'Python test ' + stamp
        projectInput = metadata.CreateProjectInput(name, 'Project created by Python SDK test')
        project = self._metadataclient.create_project(projectInput)
        self._projects_to_remove.append(project.id)

        temp_dir = tempfile.gettempdir()
        root_dir = os.path.join(temp_dir, f'foo{stamp}')
        Path(root_dir).mkdir(parents=True, exist_ok=True)
        
        files = [
            'aaa/one.csv',
            'aaa/two.csv',
            'bbb/alfa.dat',
            'bbb/beta.dat',
            'bbb/gamma.dat',
            'bbb/bbb1/ein.nc',
            'bbb/bbb2/uno.txt',
            'bbb/bbb2/due.txt',
            'bbb/bbb2/tres.txt',
            'ccc/dva.shp',
            'ccc/jeden.shp'
        ]

        # create tree structure of files
        for f in files:
            file_path = os.path.join(root_dir, f)
            Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as o:
                o.write("hello\n")
        
        # create empty folder
        Path(os.path.join(root_dir, 'ccc', 'ccc1')).mkdir(parents=True, exist_ok=True)
        
        uploaded = self._transferclient.upload_folder_to_project(root_dir, project.id)
        downloaded = self._transferclient.download_project_to_folder(project.id, root_dir)

        for d in downloaded:
            os.remove(d)
        

if __name__ == "__main__":
    unittest.main()