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

import datetime
from enum import Enum
from typing import Generator
from .base import constants
from dhi.platform.base.exceptions import MikeCloudException
from .generated.sharinggen import SharingGenClientV1

class CatalogType(Enum):
    INTRA_TENANT = 0
    PUBLIC = 1

    @classmethod
    def from_string(self, catalog_type: str):
        options = {
            'IntraTenant': self.INTRA_TENANT,
            'Public': self.PUBLIC,
        }
        if catalog_type in options:
            return options[catalog_type]
        else:
            raise MikeCloudException("Invalid catalog type", catalog_type)
        
    @property
    def name(self):
        options = {
            'INTRA_TENANT': 'IntraTenant',
            'PUBLIC': 'Public',
        }
        if self._name_ in options:
            return options[self._name_]
        else:
            raise MikeCloudException("Invalid catalog type", self._name_)


class SubscriptionMode(Enum):
    OPEN = 100
    ON_APPROVAL = 200

    @classmethod
    def from_string(self, mode: str):
        options = {
            'Open': self.OPEN,
            'OnApproval': self.ON_APPROVAL,
        }
        if mode in options:
            return options[mode]
        else:
            raise MikeCloudException("Invalid subscription mode", mode)
    
    @property
    def name(self):
        options = {
            'OPEN': 'Open',
            'ON_APPROVAL': 'OnApproval'
        }
        if self._name_ in options:
            return options[self._name_]
        else:
            raise MikeCloudException("Invalid subscription mode", self._name_)


class PublicationResourceType(Enum):
    DATASET = 100
    FOLDER = 200

    @classmethod
    def from_string(self, resource_type: str):
        options = {
            'Dataset': self.DATASET,
            'Folder': self.FOLDER,
        }
        if resource_type in options:
            return options[resource_type]
        else:
            raise MikeCloudException("Invalid resource type", resource_type)


class PublicationOutput:
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
        location: object,
        metadata: dict,
        properties: dict,
        resource_id: str,
        resource_type: PublicationResourceType,
        discoverable: bool,
        subscription_mode: SubscriptionMode,
        published_until:datetime.datetime,
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
        self._location = location
        self._metadata = metadata
        self._properties = properties
        self._resource_id = resource_id
        self._resource_type = resource_type
        self._discoverable = discoverable
        self._subscription_mode = subscription_mode
        self._published_until = published_until
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
    def properties(self) -> dict:
        return self._properties
    
    @property
    def resource_id(self) -> str:
        return self._resource_id
    
    @property
    def resource_type(self) -> PublicationResourceType:
        return self._resource_type

    @property
    def discoverable(self) -> bool:
        return self._discoverable

    @property
    def subscription_mode(self) -> bool:
        return self._subscription_mode
    
    @property
    def published_until(self) -> datetime.datetime:
        return self._published_until
    
    @property
    def row_version(self) -> str:
        return self._row_version

    @classmethod
    def from_body(cls, body: dict):
        updated_at = None if body.get("updatedAt", None) is None else datetime.datetime.strptime(body["updatedAt"][:26], constants.DATETIMEFORMAT)
        deleted_at = None if body.get("deletedAt", None) is None else datetime.datetime.strptime(body["deletedAt"][:26], constants.DATETIMEFORMAT)
        published_until = None if body.get("publishedUntil", None) is None else datetime.datetime.strptime(body["publishedUntil"][:26], constants.DATETIMEFORMAT)
        return cls(
            id = body["id"],
            created_at = datetime.datetime.strptime(body["createdAt"][:26], constants.DATETIMEFORMAT),
            created_by = body["createdBy"],
            updated_at = updated_at,
            updated_by = body.get("updatedBy", None),
            deleted_at = deleted_at,
            deleted_by = body.get("deletedBy", None),
            name = body["name"],
            description = body.get("description", None),
            location = body.get("location", None),
            metadata = body["metadata"],
            properties = body["properties"],
            resource_id = body["resourceId"],
            resource_type = PublicationResourceType.from_string(body["resourceType"]),
            subscription_mode = SubscriptionMode.from_string(body["subscriptionMode"]),
            discoverable = body["discoverable"],
            published_until = published_until,
            row_version = body["rowVersion"]
        )


class EditPublicationInput:
    def __init__(self, id:str, name: str, resource_id:str, row_version:str, description: str = None, metadata: dict = {}, discoverable = None, location = None, properties:dict = {}):
        self._id = id
        self._name = name
        self._description = "" if description is None else description
        self._discoverable = discoverable
        self._location = location
        self._resource_id = resource_id
        self._row_version = row_version
        self._metadata = metadata
        self._properties = properties

    @property 
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
    
    @property 
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property 
    def discoverable(self) -> bool:
        return self._discoverable

    @discoverable.setter
    def discoverable(self, discoverable):
        self._discoverable = discoverable

    @property 
    def resource_id(self):
        return self._resource_id

    @resource_id.setter
    def resource_id(self, resource_id:str):
        self._resource_id = resource_id

    @property 
    def metadata(self) -> dict:
        return self._metadata
    
    @property 
    def location(self) -> object:
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    def body(self):
        body = {
            "id": self._id,
            "rowVersion": self._row_version
        }

        if self._name is not None:
            body["name"] = self._name
        if self._description is not None:
            body["description"] = self._description
        if self._discoverable is not None:
            body["discoverable"] = self._discoverable
        if self._metadata is not None:
            body["metadata"] = self._metadata
        if self._properties is not None:
            body["properties"] = self._properties
        if self._resource_id is not None:
            body["resourceId"] = self._resource_id
        if self._location is not None:
            body["location"] = self._location
        return body


class CreatePublicationInput:
    def __init__(self, name: str, catalog_id:str, resource_id:str, description: str = None, metadata: dict = {}, subscription_mode:SubscriptionMode = SubscriptionMode.OPEN, discoverable=True, resource_type:PublicationResourceType=PublicationResourceType.DATASET, published_until:datetime.datetime=None):
        self._name = name
        self._catalog_id = catalog_id
        self._resource_id = resource_id
        self._description = "" if description is None else description
        self._subscription_mode = subscription_mode
        self._discoverable = discoverable
        self._resource_type = resource_type
        self._published_until = published_until
        self._metadata = metadata
        self._properties = {}

    @property 
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property 
    def catalog_id(self) -> str:
        return self._catalog_id

    @catalog_id.setter
    def catalog_id(self, catalog_id):
        self._catalog_id = catalog_id

    @property 
    def resource_id(self) -> str:
        return self._resource_id

    @resource_id.setter
    def resource_id(self, resource_id):
        self._resource_id = resource_id
    
    @property 
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property 
    def discoverable(self) -> bool:
        return self._discoverable

    @discoverable.setter
    def discoverable(self, discoverable):
        self._discoverable = discoverable

    def set_metadata_item(self, key, value):
        self._metadata[key] = value

    @property 
    def resource_type(self):
        return self._resource_type

    @resource_type.setter
    def resource_type(self, resource_type:PublicationResourceType):
        self._resource_type = resource_type

    @property 
    def metadata(self) -> dict:
        return self._metadata
    
    @property 
    def published_until(self) -> datetime.datetime:
        return self._published_until

    @published_until.setter
    def published_until(self, published_until):
        self._published_until = published_until

    def body(self):
        body = {
            "name": self._name,
            "catalogId": self._catalog_id,
            "resourceId": self._resource_id,
            "description": self._description,
            "subspcriptionMode": self._subscription_mode.name,
            "discoverable": self._discoverable,
            "resourceType": self._resource_type.name.title()
        }

        if self._metadata:
            body["metadata"] = self._metadata

        if self._properties:
            body["properties"] = self._properties

        if self._published_until is not None:
            body["publishedUntil"] = self._published_until.strftime(constants.DATETIMEFORMAT)
        return body


class CatalogOutput:
    def __init__(
        self,
        id: str,
        created_at: datetime.date,
        created_by: str,
        updated_at: datetime.date,
        updated_by: str,
        deleted_at: datetime.date,
        deleted_by: str,
        catalog_type: CatalogType,
        name: str
    ):
        self._id = id
        self._created_at = created_at
        self._created_by = created_by
        self._updated_at = updated_at
        self._updated_by = updated_by
        self._deleted_at = deleted_at
        self._deleted_by = deleted_by
        self._name = name,
        self._catalog_type = catalog_type

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name
    
    @property
    def catalog_type(self):
        return self._catalog_type

    @property
    def created_at(self):
        return self._created_at
    
    @property
    def created_by(self):
        return self._created_by
    
    @classmethod
    def from_body(cls, body: dict):
        updated_at = None if body.get("updatedAt", None) is None else datetime.datetime.strptime(body["updatedAt"][:26], constants.DATETIMEFORMAT)
        deleted_at = None if body.get("deletedAt", None) is None else datetime.datetime.strptime(body["deletedAt"][:26], constants.DATETIMEFORMAT)
        return cls(
            id = body["id"],
            created_at = datetime.datetime.strptime(body["createdAt"][:26], constants.DATETIMEFORMAT),
            created_by = body["createdBy"],
            updated_at = updated_at,
            updated_by = body.get("updatedBy", None),
            deleted_at = deleted_at,
            deleted_by = body.get("deletedBy", None),
            name = body["name"],
            catalog_type = CatalogType.from_string(body["catalogType"])
        )


class CreateCatalogInput:
    def __init__(self, name: str, catalog_type:CatalogType = CatalogType.PUBLIC):
        self._name = name
        self._catalog_type = catalog_type
        
    @property 
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
    
    @property 
    def catalog_type(self) -> CatalogType:
        return self._catalog_type

    @catalog_type.setter
    def catalog_type(self, catalog_type:CatalogType):
        self._catalog_type = catalog_type

    def body(self):
        return {
            "name": self._name,
            "catalogType": self._catalog_type.name
        }


class SharingClientV1(SharingGenClientV1):
    def __init__(self, inspectFnc=SharingGenClientV1.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)


class SharingClient():
    
    def __init__(self, inspectFnc=SharingGenClientV1.DefaultInspectFnc, **kwargs):
        self._client1 = SharingClientV1(inspectFnc, **kwargs)
        
    def list_publications(self, catalog_id, project_id=None, resource_id=None) -> Generator[PublicationOutput, None, None]:
        """
        List publications

        :param catalog_id: ID of the catalog to list publications from
        :param project_id: Optional ID of the project to limit the results to
        :param resource_id: Optional ID of the resource (e.g. project or dataset) to limit the results to
        :return: generator of publications
        :rtype: Generator[PublicationOutput, None, None]
        """
        is_first_query = True
        cursor = None
        while cursor or is_first_query:
            response = self._client1.GetPublicationList(project_id, resource_id, catalog_id, sortby=None, sortorder=None, cursor=cursor, limit=1000)
            is_first_query = False
            cursor = response.Body.get("cursor", None)
            for p in response.Body['data']:
                yield PublicationOutput.from_body(p)

    def get_publication(self, project_id, publication_id) -> PublicationOutput:
        """
        Get publication
        
        :param project_id: ID of the project to get the publication from
        :param publication_id: ID of the publication to get
        :return: publication details
        :rtype: PublicationOutput
        """
        response = self._client1.GetPublication(project_id, publication_id)
        return PublicationOutput.from_body(response.Body)

    def create_publication(self, project_id, input:CreatePublicationInput) -> str:
        """
        Create publication
        
        :param project_id: Optional ID of the project to limit the results to
        :param input: CreatePublicationInput instance defining the publication details
        :return: publication ID
        :rtype: str
        """
        response = self._client1.CreatePublication(project_id, input.body())
        return response.Body["publicationId"]

    def update_publication(self, project_id, input:EditPublicationInput) -> PublicationOutput:
        """
        Update publication
        
        :param project_id: Project ID of the publication
        :param input: EditPublicationInput instance defining the new properties of the publication
        :return: updated publication details
        :rtype: PublicationOutput
        """
        response = self._client1.UpdatePublication(project_id, input.body())
        return PublicationOutput.from_body(response.Body)

    def delete_publication(self, project_id, publication_id, resource_id) -> bool:
        """
        Delete publication, the publication is deleted permanently
        
        :param project_id: Project ID of the publication
        :param publication_id: ID of the publication
        :param resource_id: ID of the project or dataset the publication refers to, needed for authorization evaluation
        :return: True if the request was successful, raises otherwise
        :rtype: bool
        """
        response = self._client1.DeletePublication(project_id, publication_id, resource_id)
        return response.IsOk
    
    def create_catalog(self, project_id, input:CreateCatalogInput) -> str:
        """
        Create catalog
        
        :param project_id: ID of the project where the catalog should reside in
        :param input: CreateCatalogInput instance defining the catalog properties
        :return: catalog ID
        :rtype: srr
        """
        response = self._client1.CreateCatalog(project_id, input.body())
        return response.Body["catalogId"]
    
    def list_catalogs(self, project_id) -> Generator[CatalogOutput, None, None]:
        """
        List catalogs
        
        :param project_id: ID of the project to list catalogs from
        :return: generator of catalogs
        :rtype: Generator[CatalogOutput, None, None]
        """
        is_first_query = True
        cursor = None
        while cursor or is_first_query:
            response = self._client1.GetCatalogList(project_id, cursor=cursor, limit=1000)
            is_first_query = False
            cursor = response.Body.get("cursor", None)
            for p in response.Body['data']:
                yield CatalogOutput.from_body(p)


if __name__ == '__main__':
    print(__file__)
    print(dir())
