import unittest
from unittest.mock import ANY, create_autospec, Mock
import datetime
from unittest.case import _AssertRaisesContext
import uuid
from dhi.platform import metadata, transfer
from dhi.platform.authentication import ApiKeyIdentity
from dhi.platform.base.client import Response
from dhi.platform.raw import RawClientV2
import os

class TestTransferTest(unittest.TestCase):

    _verbosity = 0
    _project_id = None
    _identity = None
    _test_data_dir = None
    
    def setUp(self) -> None:
        if not self._identity:
            self._identity = ApiKeyIdentity(str(uuid.uuid4()), str(uuid.uuid4()))
        self._metadata2 = create_autospec(metadata.MetadataClientV2(verbose=self._verbosity, identity=self._identity))
        self._metadata3 = create_autospec(metadata.MetadataClientV3(verbose=self._verbosity, identity=self._identity))
        self._raw2 = create_autospec(RawClientV2(verbose=self._verbosity, identity=self._identity))

        self._transferclient = transfer.TransferClient(
            verbose=self._verbosity, 
            identity=self._identity,
            MetadataClientV2=self._metadata2,
            MetadataClientV3=self._metadata3,
            RawClientV2=self._raw2)
        
        self._test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self._project_id = str(uuid.uuid4())

    def tearDown(self) -> None:
        super().tearDown()
        
    def test_get_readers_is_ok(self):
        readers = [*self._transferclient.get_readers()]
        self._metadata2.GetReadersListV2.assert_called_once()

    def test_simple_file_upload_is_ok(self):

        self._metadata3.UploadConvertV3 = Mock(return_value=Response(1, 200, "", {}, body={
            "id": str(uuid.uuid4()),
            "createdAt": "2022-01-01T01:01:01",
            "createdBy": str(uuid.uuid4()),
            "type": "Import",
            "format": None,
            "status": "Completed"
        }))

        destination_project_id = str(uuid.uuid4())
        self._transferclient.create_url_import(destination_project_id, "http://url", "file") \
            .execute()

        self._metadata3.UploadConvertV3.assert_called_once_with({
            "originalFileName": "file",
            "uploadUrl": "http://url",
            "outputDatasetData": { "name": "file" },
            "readerName": "FileReader",
            "writerName": "FileWriter",
            "projectId": destination_project_id
        })

    def test_upload_with_parameters_is_ok(self):

        self._metadata3.UploadConvertV3 = Mock(return_value=Response(1, 200, "", {}, body={
            "id": str(uuid.uuid4()),
            "createdAt": "2022-01-01T01:01:01",
            "createdBy": str(uuid.uuid4()),
            "type": "Import",
            "format": None,
            "status": "Completed"
        }))

        destination_project_id = str(uuid.uuid4())
        reader = transfer.DfsuReader()
        reader.with_allowed_items(("item1", "item2"))

        self._transferclient.create_url_import(destination_project_id, "http://url", "dataset", "file") \
            .with_reader(reader) \
            .with_writer(transfer.MDWriter()) \
            .execute()
        
        self._metadata3.UploadConvertV3.assert_called_once_with({
            "originalFileName": "file",
            "uploadUrl": "http://url",
            "outputDatasetData": { "name": "dataset" },
            "projectId": destination_project_id,
            "readerName": "DfsuReader",
            "readerParameters": [{"name": "AllowedItemNames", "value": ["item1", "item2"]}],
            "writerName": "MDWriter"
        })
    
    def test_get_dataset_transfer_list_is_ok(self):
        project_id = str(uuid.uuid4())
        dataset_id = str(uuid.uuid4())
        date = datetime.date.today()

        self._metadata2.GetProjectTransferListV2 = Mock(return_value=Response(1, 200, "", {}, body={
            "data": []
        }))

        transfers = [*self._transferclient.list_dataset_transfers(project_id, dataset_id, from_=date)]

        self.assertEqual(transfers, [])

        self._metadata2.GetProjectTransferListV2.assert_called_once_with(
            projectid=project_id,
            datasetid=dataset_id,
            from_=date,
            to=None,
            status=(),
            offset=ANY,
            limit=ANY
        )

    def test_get_project_transfer_list_is_ok(self):
        project_id = str(uuid.uuid4())
        date = datetime.date.today()

        self._metadata2.GetProjectTransferListV2 = Mock(return_value=Response(1, 200, "", {}, body={
            "data": []
        }))

        transfers = [*self._transferclient.list_project_transfers(project_id, from_=date)]

        self.assertEqual(transfers, [])

        self._metadata2.GetProjectTransferListV2.assert_called_once_with(
            project_id,
            datasetid=None,
            from_=date,
            to=None,
            status=(),
            offset=ANY,
            limit=ANY
        )

    def test_is_dataset_id_locked_is_ok(self):
        project_id = str(uuid.uuid4())
        dataset_id = str(uuid.uuid4())

        self._metadata2.GetProjectTransferListV2 = Mock(return_value=Response(1, 200, "", {}, body={
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "createdAt": "2022-01-01T01:01:01",
                    "createdBy": str(uuid.uuid4()),
                    "type": "Import",
                    "format": "file",
                    "status": "InProgress"
                }
            ]
        }))
        
        is_locked = self._transferclient.is_dataset_locked(project_id, dataset_id)
        
        self.assertTrue(is_locked)

        self._metadata2.GetProjectTransferListV2.assert_called_once_with(
            projectid=project_id,
            datasetid=dataset_id,
            from_=None,
            to=None,
            status=(transfer.TransferStatus.NONE, transfer.TransferStatus.PENDING, transfer.TransferStatus.INPROGRESS),
            offset=ANY,
            limit=ANY
        )

    def test_upload_staged_files_is_ok(self):
        project_id = str(uuid.uuid4())
        upload_input = transfer.StagedFilesUploadInput(files=[], create_destination_path_if_not_exists=True)
        expected = transfer.StagedFilesUploadOutput(datasets=[], failures=[])

        self._metadata2.UploadStagedFilesV2 = Mock(return_value=Response(1, 200, "", {}, body={
            "datasets": [],
            "failures": []
        }))

        result = self._transferclient.upload_staged_files(project_id, upload_input)

        self.assertEqual(result.datasets, expected.datasets)
        self.assertEqual(result.failures, expected.failures)
        

if __name__ == "__main__":
    unittest.main()