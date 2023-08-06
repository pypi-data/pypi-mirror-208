import unittest
import datetime
from unittest.case import _AssertRaisesContext
import uuid
from dhi.platform import metadata
from dhi.platform.base.exceptions import MikeCloudRestApiException
from .testcredentials import TEST_IDENTITY

class TestCreateProject(unittest.TestCase):

    _verbosity = 0
    
    def setUp(self) -> None:
        self._metadataclient = metadata.MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)
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

    def test_metadata_client_can_initialize_is_ok(self):
        metadataclient = metadata.MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)
        self.assertIsNotNone(metadataclient)
    
    def test_create_get_and_destroy_project_is_ok(self):
        stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        name = 'Python test ' + stamp
        projectInput = metadata.CreateProjectInput(name, 'Project created by Python SDK test')
        project = self._metadataclient.create_project(projectInput)
        self.assertIsNotNone(project)
        self.assertEqual(project.name, name)
        self._projects_to_delete.append(project.id)
        single_project = self._metadataclient.get_project(project.id)
        self.assertIsNotNone(single_project)
        self.assertEqual(project.id, single_project.id)
        self.assertEqual(project.name, single_project.name)
        self._metadataclient.delete_project(project.id, permanently=True)
    
    def test_get_nonexisting_project_raises(self):
        project_id = str(uuid.uuid4())
        with self.assertRaises(MikeCloudRestApiException):
            self._metadataclient.get_project(project_id)
    
    def test_list_projects_is_ok(self):
        projects = self._metadataclient.list_projects()
        self.assertTrue(projects)
        first_project = next(projects)
        self.assertIsNotNone(first_project)
        self.assertTrue(first_project.id)
        self.assertTrue(first_project.name)

    def test_update_project_is_ok(self):
        stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        name = 'Python test ' + stamp
        description = 'Project created by Python SDK test'
        projectInput = metadata.CreateProjectInput(name, description)
        project = self._metadataclient.create_project(projectInput)
        self.assertIsNotNone(project)
        self._projects_to_delete.append(project.id)

        update_project_input = metadata.UpdateProjectInput(project.id, name + " Updated", description + " Updated", metadata={"foo": "bar", "spam": 1})
        updated = self._metadataclient.update_project(update_project_input)
        self.assertEqual(updated.name, name + " Updated")
        self.assertEqual(updated.description, description + " Updated")
        self.assertTrue("foo" in updated.metadata)
        self.assertTrue("spam" in updated.metadata)
        self.assertEqual(updated.metadata["foo"], "bar")
        self.assertEqual(updated.metadata["spam"], 1)

        update_project_input_2 = metadata.UpdateProjectInput(project.id, name + " Updated 2", metadata={"spam": None, "eggs": 2 })
        updated_2 = self._metadataclient.update_project(update_project_input_2)

        self.assertEqual(updated_2.name, name + " Updated 2")
        self.assertIsNone(updated_2.description)
        self.assertTrue("foo" not in updated_2.metadata)
        self.assertTrue("eggs" in updated_2.metadata)
        self.assertTrue("spam" in updated_2.metadata)
        self.assertIsNone(updated_2.metadata["spam"])
        self.assertEqual(updated_2.metadata["eggs"], 2)

    def test_project_members_is_ok(self):
        users = self._metadataclient.get_users()
        
        self.assertTrue(users)
        if(len(users) < 2):
            raise Exception("test_project_members_is_ok requires at least 2 users")

        project = self._create_project()
        self.assertIsNotNone(project)
        self._projects_to_delete.append(project.id)

        project_members = self._metadataclient.get_project_members(project.id)
        
        self.assertEqual(len(project_members), 0)

        """
        # Working with project members changed in November 2022, see https://develop.mike-cloud.com/docs/API/Privileges-and-Access-Levels
        first_member = project_members[0]

        second_user = [u for u in users if u.user_id != first_member.user_id][0]
        second_member = metadata.ProjectMember(second_user.user_id, metadata.ProjectMemberRole.CONTRIBUTOR)

        self._metadataclient.add_project_member(project.id, second_member)

        project_members = self._metadataclient.get_project_members(project.id)

        self.assertEqual(len(project_members), 2)

        self._metadataclient.remove_project_member(project.id, second_member.user_id)

        project_members = self._metadataclient.get_project_members(project.id)

        self.assertEqual(len(project_members), 1)

        row_version_output = self._metadataclient.set_project_members(project.id, [first_member, second_member])

        project_members = self._metadataclient.get_project_members(project.id)

        self.assertEqual(len(project_members), 2)
        """

    def skip_update_project_access_level_is_ok(self):
        print("Project Access Level has been deprecated since November 2022, see https://develop.mike-cloud.com/docs/API/Privileges-and-Access-Levels")

    def test_subprojects_is_ok(self):
        project = self._create_project()
        self.assertIsNotNone(project)
        self._projects_to_delete.append(project.id)

        sub1input = metadata.SubprojectInput("Subproject 1")
        sub1 = self._metadataclient.create_subproject(project.id, sub1input)
        
        self.assertIsNotNone(sub1)

        sub2input = metadata.SubprojectInput("Subproject 2")
        sub2 = self._metadataclient.create_subproject(project.id, sub2input)

        self.assertIsNotNone(sub2)

        sub11input = metadata.SubprojectInput("Subproject 1 1", description="Subproject 1 of 1")
        sub11 = self._metadataclient.create_subproject(sub1.id, sub11input)
        
        self.assertIsNotNone(sub11)

        subprojects = self._metadataclient.list_subprojects(project.id)
        subs = [*subprojects]
        
        self.assertEqual(len(subs), 2)

        sub11path = self._metadataclient.get_project_path(sub11.id)
        path = "/".join([s.name for s in sub11path])

        expected_path = "dhi1/" + project.name + "/Subproject 1/Subproject 1 1"
        print(path, expected_path)
        self.assertEqual(path, expected_path)

        self._metadataclient.move_project(sub11.id, sub2.id)

        subs1 = [*self._metadataclient.list_subprojects(sub1.id)]

        self.assertFalse(subs1)

        subs2 = [*self._metadataclient.list_subprojects(sub2.id)]
        
        self.assertEqual(len(subs2), 1)

    def test_prepare_hierarchy(self):
        project = self._create_project()    
        self.assertIsNotNone(project)
        self._projects_to_delete.append(project.id)

        actions = [
            metadata.PathAction.create_if_not_exists("foo", True),
            metadata.PathAction.create("foo/bar"),
            metadata.PathAction.create("foo/spam", True),
            metadata.PathAction.create("foo/spam/eggs"),
            metadata.PathAction.delete("foo/fred", True)
        ]

        hierarchy = self._metadataclient.prepare_hierarchy(project.id, actions)
        results = hierarchy.results
        self.assertTrue(results)
        self.assertEqual(4, len(results))
        self.assertEqual(2, len([r for r in results if r.datasetId is not None]))

    def test_get_sas_token_is_ok(self):
        project = self._create_project()
        self._projects_to_delete.append(project.id)
        token = self._metadataclient.get_sas_token_string(project.id, None, datetime.timedelta(hours=2))
        self.assertIsInstance(token, str)

    def test_get_service_url_is_ok(self):
        url = self._metadataclient.get_service_url("pubsub")
        self.assertIsInstance(url, str)

        

if __name__ == "__main__":
    unittest.main()
