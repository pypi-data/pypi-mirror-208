import unittest
import uuid
from dhi.platform.metadata import MetadataClient
from dhi.platform.base.exceptions import MikeCloudRestApiException
from .testcredentials import TEST_IDENTITY

class TestCreateProject(unittest.TestCase):

    _verbosity = 3

    def test_get_nonexisting_project_raises(self):
        metadataclient = MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        project_id = str(uuid.uuid4())

        try:

            p = metadataclient.get_project(project_id)

        except MikeCloudRestApiException as ex:

            self.assertTrue(ex.message)
            self.assertTrue(ex.status_code)
    
if __name__ == "__main__":
    unittest.main()