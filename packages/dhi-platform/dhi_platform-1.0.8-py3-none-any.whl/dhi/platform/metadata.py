# Copyright (c) 2021 DHI A/S - DHI Water Environment Health 
# All rights reserved.
# 
# This code is licensed under the MIT License.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#from _typeshed import Self
from enum import Enum
import datetime
import time
from typing import Generator, List, Tuple
from dhi.platform.base.exceptions import MikeCloudException, MikeCloudRestApiException
from .generated.metadatagen import AccessLevelV3, DatasetOutputV3, DatasetRecursiveListOutputV3, ItemIdV3, MetadataGenClientV1, MetadataGenClientV2, MetadataGenClientV3, PathActionCreateIfNotExistsV3, PathActionCreateV3, PathActionDeleteV3, PathActionV3, PrepareHierarchyInputV3, PrepareHierarchyOutputV3, UnitIdV3
from .base import constants
from .commonmodels import DatasetType


class AccessLevel(Enum):
    SHARED = 100
    PRIVATE = 200
    CONFIDENTIAL = 300

    @classmethod
    def from_string(self, access_level: str):
        options = {
            'Shared': self.SHARED,
            'Private': self.PRIVATE,
            'Confidential': self.CONFIDENTIAL,
        }
        if access_level in options:
            return options[access_level]
        else:
            raise MikeCloudException("Invalid project access level", access_level)


class ProjectMemberRole(Enum):
    READER = 100
    CONTRIBUTOR = 200
    OWNER = 300

    @classmethod
    def from_string(self, role: str):
        options = {
            'Reader': self.READER,
            'Contributor': self.CONTRIBUTOR,
            'Owner': self.OWNER,
        }
        if role in options:
            return options[role]
        else:
            raise MikeCloudException("Invalid project member role", role)


class ProjectMemberInput:
    def __init__(self, user_id: str, role: ProjectMemberRole) -> None:
        self._data = {
            "userId": user_id,
            "role": role.name.title()
        }
    
    def body(self):
        return self._data


class ProjectMemberOutput:
    def __init__(self, user_id : str, role: ProjectMemberRole):
        self._user_id = user_id
        self._role = role
    
    @property
    def user_id(self):
        self._user_id
    
    @property
    def role(self):
        self._role

    @classmethod
    def from_body(cls, data: dict):
        user_id = data["userId"]
        role = ProjectMemberRole.from_string(data["role"])
        return cls(user_id, role)


class CreateProjectInput:
    def __init__(self, name: str, description: str = None, access_level: AccessLevel = AccessLevel.SHARED, metadata: dict = {}, members: list = []):
        self._name = name
        self._access_level = access_level
        self._description = "" if description is None else description
        self._metadata = metadata
        self._settings = {}
        self._members = members

    @property 
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description
    
    @property 
    def access_level(self):
        return self._access_level

    @access_level.setter
    def access_level(self, access_level):
        self._access_level = access_level

    def set_metadata_item(self, key, value):
        self._metadata[key] = value

    def body(self):
        return {
            "name": self._name,
            "accessLevel": self._access_level.name.title(),
            "description": self._description,
            "metadata": self._metadata,
            "settings": self._settings,
            "members": [m.body() for m in self._members]
        }


class ProjectOutput:
    def __init__(
        self,
        id: str,
        created_at: datetime.date,
        created_by: str,
        updated_at: datetime.date,
        updated_by: str,
        deleted_at: datetime.date,
        deleted_by: str,
        name: str,
        description: str,
        metadata: dict,
        settings: dict,
        access_level: AccessLevel,
        members: list,
        capabilities: list,
        parent_project_id: str, 
        inherits_members: bool,
        row_version: str
    ):
        self._id = id
        self._created_at = created_at
        self._created_by = created_by
        self._updated_at = updated_at
        self._updated_by = updated_by
        self._deleted_at = deleted_at
        self._deleted_by = deleted_by
        self._name = name
        self._description = description
        self._metadata = metadata
        self._settings = settings
        self._access_level = access_level
        self._members = members
        self._capabilities = capabilities
        self._parent_project_id = parent_project_id
        self._inherits_members = inherits_members
        self._row_version = row_version

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description

    @property
    def created_at(self):
        return self._created_at
    
    @property
    def created_by(self):
        return self._created_by

    @property
    def updated_at(self):
        return self._updated_at

    @property
    def updated_by(self):
        return self._updated_by

    @property
    def deleted_by(self):
        return self._deleted_by

    @property
    def deleted_at(self):
        return self._deleted_at

    @property
    def metadata(self) -> dict:
        return self._metadata

    @property
    def settings(self) -> dict:
        return self._settings
    
    @property
    def access_level(self) -> AccessLevel:
        return self._access_level
    
    @property
    def capabilities(self) -> dict:
        return self._capabilities

    @property
    def parent_project_id(self) -> str:
        return self._parent_project_id

    @property
    def inherits_members(self) -> bool:
        return self._inherits_members
    
    @property
    def row_version(self) -> str:
        return self._row_version
    
    @property
    def capabilities(self) -> dict:
        return self._capabilities

    @property
    def members(self) -> list:
        return self._members

    @classmethod
    def from_body(cls, body: dict):
        updated_at = None if body.get("updatedAt", None) is None else datetime.datetime.strptime(body["updatedAt"][:26], constants.DATETIMEFORMAT)
        deleted_at = None if body.get("deletedAt", None) is None else datetime.datetime.strptime(body["deletedAt"][:26], constants.DATETIMEFORMAT)
        return cls(
            id = body["id"],
            created_at = datetime.datetime.strptime(body["createdAt"][:26], constants.DATETIMEFORMAT),
            created_by = body["createdBy"],
            updated_at = updated_at,
            updated_by = body["updatedBy"],
            deleted_at = deleted_at,
            deleted_by = None if "deletedBy" not in body else body["deletedBy"],
            name = body["name"],
            description = None if "description" not in body else body["description"],
            metadata = body["metadata"],
            settings = body["settings"],
            access_level = AccessLevel.from_string(body["accessLevel"]),
            members = [ProjectMemberOutput.from_body(m) for m in body["members"]],
            capabilities = body["capabilities"],
            parent_project_id = None if "parentProjectId" not in body else body["parentProjectId"],
            inherits_members = body["inheritsMembers"],
            row_version = body["rowVersion"]
        )


class ListProjectOutput:
    def __init__(
        self,
        id: str,
        created_at: datetime.date,
        created_by: str,
        updated_at: datetime.date,
        updated_by: str,
        deleted_at: datetime.date,
        deleted_by: str,
        name: str,
        description: str,
        access_level: AccessLevel,
        parent_project_id: str, 
        row_version: str
    ):
        self._id = id
        self._created_at = created_at
        self._created_by = created_by
        self._updated_at = updated_at
        self._updated_by = updated_by
        self._deleted_at = deleted_at
        self._deleted_by = deleted_by
        self._name = name
        self._description = description
        self._access_level = access_level
        self._parent_project_id = parent_project_id
        self._row_version = row_version

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description

    @property
    def created_at(self):
        return self._created_at
    
    @property
    def created_by(self):
        return self._created_by

    @property
    def updated_at(self):
        return self._updated_at

    @property
    def updated_by(self):
        return self._updated_by

    @property
    def deleted_by(self):
        return self._deleted_by

    @property
    def deleted_at(self):
        return self._deleted_at
    
    @property
    def access_level(self) -> AccessLevel:
        return self._access_level

    @property
    def parent_project_id(self) -> str:
        return self._parent_project_id
    
    @property
    def row_version(self) -> str:
        return self._row_version

    @classmethod
    def from_body(cls, body: dict):
        updated_at = None if "updatedAt" not in body else datetime.datetime.strptime(body["updatedAt"][:26], constants.DATETIMEFORMAT)
        deleted_at = None if "DeletedAt" not in body else datetime.datetime.strptime(body["deletedAt"][:26], constants.DATETIMEFORMAT)
        return cls(
            id = body["id"],
            created_at = datetime.datetime.strptime(body["createdAt"][:26], constants.DATETIMEFORMAT),
            created_by = body["createdBy"],
            updated_at = updated_at,
            updated_by = body["updatedBy"],
            deleted_at = deleted_at,
            deleted_by = None if "deletedBy" not in body else body["deletedBy"],
            name = body["name"],
            description = None if "description" not in body else body["description"],
            access_level = AccessLevel.from_string(body["accessLevel"]),
            parent_project_id = None if "parentProjectId" not in body else body["parentProjectId"],
            row_version = body["rowVersion"]
        )


class RowVersionOutput:
    def __init__(self, id: str, row_version: str):
        self._id = id
        self._row_version = row_version

    @property
    def id(self):
        return self._id
    
    @property
    def row_version(self) -> str:
        return self._row_version

    @classmethod
    def from_body(cls, body: dict):
        return cls(
            id = body["id"],
            row_version = body["rowVersion"]
        )


class UpdateProjectInput:
    def __init__(self, id, name: str, description: str = None, metadata: dict = {}, settings: dict = {}):
        self._id = id
        self._name = name
        self._description = description
        self._metadata = metadata
        self._settings = settings
    
    @property 
    def id(self):
        return self._id

    @property 
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
    
    @property 
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description
    
    @property 
    def access_level(self):
        return self._access_level
    
    def set_metadata_item(self, key, value):
        self._metadata[key] = value

    def set_settings_item(self, key, value):
        self._settings[key] = value

    def body(self):
        body = {
            "id": self._id,
            "name": self._name
        }

        if self._description:
            body["description"] = self._description
        
        if self._metadata:
            body["metadata"] = self._metadata
        
        if self._settings:
            body["settings"] = self._settings
        
        return body


class ProjectMember:
    def __init__(self, user_id, role: ProjectMemberRole):
        self._user_id = user_id
        self._role = role
    
    @property 
    def user_id(self):
        return self._user_id

    @property 
    def role(self):
        return self._role
    
    def body(self):
        return {
            "userId": self._user_id,
            "role": self._role.name.title()
        }

    @classmethod
    def from_body(cls, body: dict):
        return cls(
            user_id=body["userId"],
            role=ProjectMemberRole.from_string(body["role"])
        )

class PlatformUser:
    def __init__(self, user_id, display_name: str, email: str, is_admin: bool, customer_id: str, customer_name: str) -> None:
        self._user_id = user_id
        self._display_name = display_name
        self._email = email
        self._is_admin = is_admin
        self._customer_id = customer_id
        self._customer_name = customer_name
    
    @property
    def user_id(self):
        return self._user_id
    
    @property
    def display_name(self):
        return self._display_name

    @property
    def email(self):
        return self._email

    @property
    def is_admin(self):
        return self._is_admin

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def customer_name(self):
        return self._customer_name

    @classmethod
    def from_body(cls, body: dict):
        return cls(
            user_id = body["userId"],
            display_name = body["displayName"],
            email = body.get("email", None),
            is_admin = body.get("isAdmin", False),
            customer_id = body.get("customerId", None),
            customer_name = body.get("customerName", None)
        )

class ProjectCapabilities:
    def __init__(self,
        can_edit: bool,
        can_edit_access_level: bool,
        can_delete: bool,
        can_grant_access: bool,
        can_create_content: bool,
        can_list_content: bool,
        can_update_content: bool,
        can_delete_content: bool,
        can_read_content: bool
    ) -> None:
        self._can_edit = can_edit
        self._can_edit_access_level = can_edit_access_level,
        self._can_delete = can_delete,
        self._can_grant_access = can_grant_access,
        self._can_create_content = can_create_content,
        self._can_list_content = can_list_content,
        self._can_update_content = can_update_content,
        self._can_delete_content = can_delete_content,
        self._can_read_content = can_read_content

    @property
    def can_edit(self):
        return self._can_edit

    @property
    def can_edit_access_level(self):
        return self._can_edit_access_level

    @property
    def can_delete(self):
        return self.can_delete

    @property
    def can_grant_access(self):
        return self._can_grant_access

    @property
    def can_create_content(self):
        return self._can_create_content

    @property
    def can_list_content(self):
        return self._can_list_content

    @property
    def can_update_content(self):
        return self._can_update_content

    @property
    def can_delete_content(self):
        return self._can_delete_content

    @property
    def can_read_content(self):
        return self._can_read_content

    @classmethod
    def from_body(cls, body: dict):
        return cls(
            can_edit = body.get("canEdit", False),
            can_edit_access_level = body.get("canEditAccessLevel", False),
            can_delete = body.get("canDelete", False),
            can_grant_access = body.get("canGrantAccess", False),
            can_create_content = body.get("canCreateContent", False),
            can_list_content = body.get("canListContent", False),
            can_update_content = body.get("canUpdateContent", False),
            can_delete_content = body.get("canDeleteContent", False),
            can_read_content = body.get("canReadContent", False)
        )

class ProjectPathNode:
    def __init__(
        self,
        id,
        name,
        parent_project_id,
        is_deleted,
        capabilities,
        access_level,
        inherit_members,
        effective_user_role
    ) -> None:
        self._id = id
        self._name = name
        self._parent_project_id = parent_project_id
        self._is_deleted = is_deleted
        self._capabilities = capabilities
        self._access_level = access_level
        self._inherit_members = inherit_members
        self._effective_user_role = effective_user_role

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def parent_project_id(self):
        return self._parent_project_id

    @property
    def is_deleted(self):
        return self._is_deleted

    @property
    def capabilities(self):
        return self._capabilities

    @property
    def access_level(self):
        return self._access_level

    @property
    def inherit_members(self):
        return self._inherit_members

    @property
    def effective_user_role(self):
        return self._effective_user_role


    @classmethod
    def from_body(cls, body: dict):
        return cls(
            id = body["id"],
            name = body["name"],
            parent_project_id = body.get("parentProjectId", None),
            is_deleted = body.get("isDeleted", True),
            capabilities = ProjectCapabilities.from_body(body["capabilities"]),
            access_level = AccessLevel.from_string(body.get("accessLevel", AccessLevel.SHARED.name.title())),
            inherit_members = body.get("inheritsMembers", True),
            effective_user_role = ProjectMemberRole.from_string(body.get("effectiveUserRole", ProjectMemberRole.READER.name.title()))
        )
        
class SubprojectInput:
    def __init__(
        self,
        name: str,
        access_level: AccessLevel = None,
        description: str = None,
        metadata: dict = None,
        settings: dict = None,
        members: List[ProjectMember] = None
    ) -> None:
        self._name = name
        self._access_level = access_level
        self._description = description
        self._metadata = metadata
        self._settings = settings
        self._members = members

    def body(self) -> dict:
        body = {
            "name": self._name
        }

        if self._access_level:
            body["accessLevel"] = self._access_level

        if self._description:
            body["description"] = self._description
        
        if self._metadata:
            body["metadata"] = self._metadata
        
        if self._settings:
            body["settings"] = self._settings
        
        if self._members:
            body["members"] = [m.body() for m in self._members]
        
        return body

class PrepareHierarchyInput(PrepareHierarchyInputV3):
    pass

class PrepareHierarchyOutput(PrepareHierarchyOutputV3):
    pass

class PathAction(PathActionV3):
    
    @classmethod
    def create(cls, path:str, is_folder:bool=False):
        return PathActionCreateV3(path, is_folder)
    
    @classmethod
    def create_if_not_exists(cls, path:str, is_folder:bool=False):
        return PathActionCreateIfNotExistsV3(path, is_folder)
    
    @classmethod
    def delete(cls, path:str, is_folder:bool=False):
        return PathActionDeleteV3(path, is_folder)


class DatasetOutput(DatasetOutputV3):
    pass


class DatasetRecursiveListOutput(DatasetRecursiveListOutputV3):
    pass

    
UnitId = UnitIdV3
ItemId = ItemIdV3

class MetadataClientV1(MetadataGenClientV1):
    def __init__(self, inspectFnc=MetadataGenClientV1.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)


class MetadataClientV2(MetadataGenClientV2):
    def __init__(self, inspectFnc=MetadataGenClientV2.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)


class MetadataClientV3(MetadataGenClientV3):
    def __init__(self, inspectFnc=MetadataGenClientV3.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)


class MetadataClient():
    
    def __init__(self, inspectFnc=MetadataGenClientV1.DefaultInspectFnc, **kwargs):
        self._client1 = MetadataClientV1(inspectFnc, **kwargs)
        self._client2 = MetadataClientV2(inspectFnc, **kwargs)
        self._client3 = MetadataClientV3(inspectFnc, **kwargs)

    def list_projects(self, nameprefix=None) -> Generator[ListProjectOutput, None, None]:
        is_first_query = True
        cursor = None
        while cursor or is_first_query:
            response = self._client3.GetProjectListV3(nameprefix, role=None, capability=None, sortby=None, sortorder=None, cursor=cursor, limit=1000)
            is_first_query = False
            cursor = response.Body.get("cursor", None)
            for p in response.Body['data']:
                yield ListProjectOutput.from_body(p)

    def get_project(self, project_id) -> ProjectOutput:
        response = self._client3.GetProjectV3(project_id)
        return ProjectOutput.from_body(response.Body)

    def create_project(self, project_input: CreateProjectInput) -> ProjectOutput:
        response = self._client3.CreateProjectV3(project_input.body())
        return ProjectOutput.from_body(response.Body)

    def delete_project(self, project_id, permanently=False) -> bool:
        response = self._client3.DeleteProjectV3(project_id)
        if permanently:
            response = self._client2.DestroyProjectV2(project_id)
        return response.IsOk            
    
    def update_project(self, update_input: UpdateProjectInput) -> ProjectOutput:
        """
        Update selected project properties.

        This is a hard update in the sense that you must include all properties in the 'update_intput' parameter.
        If you do not include a property in the 'update_intput' parameter, or you set it to None, that property will be set to None by the update.
        For 'metadata' and 'settings' parts, if key is absent in the input, the key and its value will be dropped by the update.
        If it is set to None, the value for that key will be set to None by the update.
        """
        project = self.get_project(update_input.id)
        body = update_input.body()
        body["rowVersion"] = project.row_version
        response = self._client3.UpdateProjectV3(body)
        return ProjectOutput.from_body(response.Body)

    def update_project_access_level(self, project_id, access_level: AccessLevel) -> RowVersionOutput:
        print("Project Access Level has been deprecated since November 2022, see https://develop.mike-cloud.com/docs/API/Privileges-and-Access-Levels")
        return RowVersionOutput(project_id, '')
    
    def get_project_members(self, project_id) -> List[ProjectMember]:
        response = self._client3.GetProjectMemberV3(project_id)
        body = response.Body
        return [ProjectMember.from_body(d) for d in body["data"]]

    def add_project_member(self, project_id, member: ProjectMember) -> ProjectMember:
        """Add one project member to a project"""
        response = self._client3.CreateProjectMemberV3(member.body(), project_id)
        return ProjectMember.from_body(response.Body)

    def set_project_members(self, project_id, members: List[ProjectMember]) -> RowVersionOutput:
        """Replace all existing project members with new 'members'"""
        project = self.get_project(project_id)
        body = {
            "members": [m.body() for m in members],
            "rowVersion": project.row_version
        }
        response = self._client3.SetProjectMembersV3(body, project_id)
        return RowVersionOutput.from_body(response.Body)
    
    def remove_project_member(self, project_id, member_id) -> bool:
        response = self._client3.DeleteProjectMemberV3(member_id, project_id)
        response.IsOk
    
    def inherit_project_members(self, project_id) -> RowVersionOutput:
        """Set project to inherit all members from its parent project"""
        project = self.get_project(project_id)
        body = { "rowVersion": project.row_version }
        response = self._client3.SetInheritMembersV3(body, project_id)
        return RowVersionOutput.from_body(response.Body)

    def get_users(self) -> List[PlatformUser]:
        response = self._client3.GetUserList()
        return [PlatformUser.from_body(u) for u in response.Body["data"]]

    def get_project_capabilities(self, project_id) -> ProjectCapabilities:
        response = self._client3.GetProjectCapabilitiesV3(project_id)
        return ProjectCapabilities.from_body(response.Body)
    
    def move_project(self, source_project_id, target_project_id) -> bool:
        body = {"targetProjectId": target_project_id}
        response = self._client3.MoveProjectV3(body, source_project_id)
        return response.IsOk

    def prepare_hierarchy(self, project_id, actions:Tuple[PathAction], default_access_level:AccessLevelV3=AccessLevelV3.SHARED, sas_token_expiration:datetime.timedelta=datetime.timedelta(hours=1)) -> PrepareHierarchyOutput:
        """Create hierarchy of subprojects and blob files in a project

        This method is intended for syncing folders between local system and the cloud platform.
        
        :param project_id: root project of the hierarchy.
        :param actions: Definition of the hierarchy as in iterable of PathAction instances like:
            [
                PathAction.create_if_not_exists("foo", True),
                PathAction.create("foo/bar"),
                PathAction.create("foo/spam", True),
                PathAction.create("foo/spam/eggs"),
                PathAction.delete("foo/fred", True)
            ]
        :param default_access_level: access level used for created subprojects if not specified explicitely
        :sas_token_expiration: Time for which the resulting sas tokens should be valid so that files can be uploaded. Default is 1 hour.
        :return: Object with iterable results property of path action outputs
        :rtype: PrepareHierarchyOutput
        """
        input = PrepareHierarchyInput(actions, defaultAccessLevel=default_access_level, sasTokenExpiration=str(sas_token_expiration))
        response = self._client3.PrepareHierarchy(input.to_dict(), project_id)
        return PrepareHierarchyOutput.from_dict(response.Body)

    def get_project_path(self, project_id) -> List[ProjectPathNode]:
        response = self._client3.GetProjectPathV3(project_id)
        data = response.Body["data"]
        return [ProjectPathNode.from_body(node) for node in data]
    
    def create_subproject(self, project_id, input: SubprojectInput) -> ProjectOutput:
        response = self._client3.CreateSubProjectV3(input.body(), project_id)
        return ProjectOutput.from_body(response.Body)

    def list_subprojects(self, project_id, nameprefix: str = None, role:ProjectMemberRole = None, sortby:str=None, descending=False) -> Generator[ListProjectOutput, None, None]:
        """
        List of direct subprojects of project 'project_id'.

        :param project_id: ID of the project to start from
        :param nameprefix: Search only for subproject that start with nameprefix
        :param role: return results where the effective user role the value of this parameter.
        :para sortby: can be one of Name, CreatedAt, UpdatedAt, AccessLevel
        :param descending: sort results in descending order if True, otherwise sort in ascending orded, default is False
        """
        limit = 1000
        is_first_query = True
        cursor = None
        sortorder = "Desc" if descending else "Asc"
        while cursor or is_first_query:
            response = self._client3.GetSubProjectListV3(project_id, nameprefix, role, capability=None, sortby=sortby, sortorder=sortorder, cursor=cursor, limit=limit)
            is_first_query = False
            cursor = response.Body.get("cursor", None)
            for p in response.Body['data']:
                yield ListProjectOutput.from_body(p)
        limit = 1000

    def list_datasets(self, project_id, includesastokens:bool=False) -> Generator[DatasetOutput, None, None]:
        """
        List datasets in a project
        
        :param project_id: ID of the project where the datasets reside
        :param includesastokens: if True, the response will include sas tokens where possible, default is False
        :return: Generator of DatasetOutput instances
        """
        response = self._client3.GetDatasetListV3(project_id, includesastokens=includesastokens)
        data = response.Body["data"]
        return (DatasetOutput.from_dict(d) for d in data)

    def list_datasets_recursive(self, project_id, includesastokens:bool=False, dataset_type:DatasetType=None) -> Generator[DatasetRecursiveListOutput, None, None]:
        """
        List datasets in a project recursively
        
        :param project_id: ID of the project where the datasets reside
        :param includesastokens: if True, the response will include sas tokens where possible, default is False
        :param dataset_type: Return only datasets of selected dataset type, default is None for all dataset types
        :return: Generator of DatasetRecursiveListOutput instances
        """
        limit = 1000
        offset = 0
        first_query = True
        request_dataset_type = getattr(dataset_type, 'name', None)
        while True:
            if not first_query:
                if not response.Body["data"]:
                    break
            response = self._client3.GetRecursiveDatasetListV3(project_id, offset=offset, limit=limit, includesastokens=includesastokens, datasettype=request_dataset_type)
            for i in response.Body["data"]:
                yield DatasetRecursiveListOutput.from_dict(i)
            offset = offset + limit + 1
            first_query = False

    def get_dataset(self, dataset_id):
        """
        Get dataset
        
        :param dataset_id: ID of the dataset
        :return: DatasetOutput
        :rtype: DatasetOutput
        """
        response = self._client3.GetDatasetV3(dataset_id)
        return DatasetOutput.from_dict(response.Body)

    def delete_dataset(self, dataset_id, permanently:bool=False) -> bool:
        """
        Delete dataset

        :param dataset_id: ID of the dataset
        :return: True if the dataset was deleted successfully
        :rtype: bool
        """
        response = self._client3.DeleteDatasetV3(dataset_id)
        if permanently:
            response = self._client2.DestroyDatasetV2(dataset_id)
        return response.IsOk

    def update_dataset(self, project_id, dataset_id, name:str=None, description:str=None, metadata:dict=None) -> DatasetOutput:
        """
        Update dataset

        :param project_id: ID of the project where the dataset resides
        :param dataset_id: ID of the dataset
        :param name: new name to use, no update to name is made if None, which is the default
        :param description: new description to use, no update to description is made if None, which is the default
        :param metadata: new metadata to use, no update to metadata is made if None, which is the default. If not empty, metadata will be completely replaced by the new entry.
        :return: DatasetOutput
        :rtype: DatasetOutput
        """
        dataset = self.get_dataset(dataset_id)
        datadict = dataset.to_dict()
        
        if name:
            datadict["name"] = name
        if description is not None:
            datadict["description"] = description
        if metadata is not None:
            datadict["metadata"] = metadata

        response = self._client3.UpdateDatasetV3(datadict, project_id)
        return DatasetOutput.from_dict(response.Body)

    def move_dataset(self, dataset_id, target_project_id) -> bool:
        """
        Move dataset to another project

        :param dataset_id: ID of the dataset
        :param target_project_id: ID of the project the dataset should be moved to
        :return: True if the dataset was moved successfully
        :rtype: bool
        """
        body = {"targetProjectId": target_project_id}
        response = self._client3.MoveDatasetV3(body, dataset_id)
        return response.IsOk

    def get_service_url(self, servicename) -> str:
        """Get service url by service name
        :param servicename: Short name of the service to get full URL for
        :return: Service URL
        :rtype: str
        """
        response = self._client3.GetServiceUrlV3(servicename)
        return response.Body["data"]

    def get_sas_token_string(self, project_id, resourse_id=None, expiration:datetime.timedelta=datetime.timedelta(hours=1)) -> str:
        """Get Shared Access Signature (SAS) token as a string
        :param project_id: ID of the projec to get SAS token for
        :param resource_id: Optional resource id to get SAS token for. This is typically the dataset ID.
        :param expiration: Time for which the token should be valid, default is 1 hour.
        :return: SAS token
        :rtype: str
        """
        response = self._client2.GetSasTokenV2(project_id, resourse_id, str(expiration))
        sas_token = response.Body["data"]
        return sas_token
    
    def wait_until_dataset_exists(self, dataset_id, timeout:float=7.0, timeout_handler=lambda: (_ for _ in ()).throw(MikeCloudException(f"Dataset did not exists within a specified timeout."))):
        """Wait until dataset exists in metadata.

        This is a utility method used for example when creating a time series service.
        The system has to wait until the dataset exists in metadata before it can say it exists.

        :param dataset_id: Dataset id to wait for.
        :param timeout: Optional. How many seconds to wait before a timeout handler is invoked.
        :param timeout_handler: Optional callable to call when timeout is reached.
        """
        elapsed_time = 0.0
        sleep_interval = 0.75
        dataset = None
        while dataset is None:
            try:
                dataset = self.get_dataset(dataset_id)
            except MikeCloudRestApiException as ex:
                if ex.status_code == 404 or ex.status_code == 403:
                    time.sleep(sleep_interval)
                    elapsed_time += sleep_interval
                    if(elapsed_time >= timeout):
                        timeout_handler()


if __name__ == '__main__':
    print(__file__)
    print(dir())
