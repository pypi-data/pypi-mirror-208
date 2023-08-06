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

import itertools
import os
from types import SimpleNamespace
from .base.client import Contracts
from .generated.metadatagen import MetadataGenClientV2


class MetadataClientV2Helper:
    @classmethod
    def UploadFromFile(cls, filepath, clientv2: MetadataGenClientV2):
        uploadurlresponse = clientv2.GetUploadUrlV2()
        uploadurl = uploadurlresponse.Body.get("data")
        cls.UploadBlobFromFile(uploadurl, filepath)
        return uploadurl

    @staticmethod
    def UploadBlobFromFile(url, filepath):
        from azure.storage.blob import BlobClient
        blob = BlobClient.from_blob_url(url)
        with open(filepath, "rb") as f:
            blob.upload_blob(f)

    @classmethod
    def UploadFromUrl(cls, url, clientv2: MetadataGenClientV2):
        uploadurlresponse = clientv2.GetUploadUrlV2()
        uploadurl = uploadurlresponse.Body.get("data")
        cls.UploadBlobFromUrl(uploadurl, url)
        return uploadurl

    @staticmethod
    def UploadBlobFromUrl(url, sourceurl):
        from azure.storage.blob import BlobClient
        blob = BlobClient.from_blob_url(url)
        return blob.start_copy_from_url(sourceurl)

    @staticmethod
    def DownloadBlobToFile(url, filepath):
        from azure.storage.blob import BlobClient
        blob = BlobClient.from_blob_url(url)
        download = blob.download_blob()
        if not filepath:
            filepath = os.path.basename(download.name)
            pos = filepath.find("_")
            if pos >= 0:
                filepath = filepath[pos+1:]
        with open(filepath, "wb") as f:
            download.readinto(f)

    @staticmethod
    def DeleteBlob(url):
        from azure.storage.blob import BlobClient
        blob = BlobClient.from_blob_url(url)
        if blob.exists():
            blob.delete_blob()

    @staticmethod
    def ListBlobs(url, prefix):
        from azure.storage.blob import ContainerClient
        container = ContainerClient.from_container_url(url)
        for blob in container.list_blobs(prefix):
            blobclient = container.get_blob_client(blob.name)
            yield SimpleNamespace(url = blobclient.url, name = blob.name)

class MetadataClientV2Contracts(Contracts):
    @classmethod
    def PrepareUploadStagedFilesInput(cls, input=None, uploadurl=None, filename=None, destinationpath=None, createdestinationpathifnotexists=None):
        body = input.copy() if input else {}
        files = body.get("files")
        if not files:
            files = []
            cls.SetBodyField(body, "files", files)
        file1 = { "url": uploadurl, "filename": filename }
        files.append(file1)
        cls.SetBodyField(body, "destinationPath", destinationpath)
        cls.SetBodyField(body, "createDestinationPathIfNotExists", createdestinationpathifnotexists)
        return body


class MetadataClientV3Contracts(Contracts):
    @classmethod
    def PreparePrepareHierarchyInput(cls, input=None, actiontype=None, path=None, isfolder=None, defaultaccesslevel=None, sastokenexpiration=None):
        body = input.copy() if input else {}
        actions = body.get("actions")
        if not actions:
            actions = []
            body["actions"] = actions
        allfields = itertools.zip_longest(actiontype if actiontype else [], path if path else [], isfolder if isfolder else [])
        for t, p, isf in allfields:
            item = {}
            cls.SetBodyField(item, "type", t)
            cls.SetBodyField(item, "path", p)
            cls.SetBodyField(item, "isFolder", isf)
            actions.append(item)
        cls.SetBodyField(body, "defaultaccesslevel", defaultaccesslevel)
        cls.SetBodyField(body, "sastokenexpiration", sastokenexpiration)
        return body

    @classmethod
    def PrepareCreateProjectInput(cls, input=None, name=None, description=None, accesslevel=None, metadata=None, settings=None, members=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "name", name)
        cls.SetBodyField(body, "description", description)
        cls.SetBodyField(body, "accesslevel", accesslevel)
        cls.SetBodyField(body, "metadata", metadata, {})
        cls.SetBodyField(body, "settings", settings, {})
        cls.SetBodyField(body, "members", members, [])
        return body

    @classmethod
    def PrepareUpdateProjectInput(cls, input=None, projectid=None, name=None, description=None, metadata=None, settings=None, members=None, rowversion=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "id", projectid)
        cls.SetBodyField(body, "name", name)
        cls.SetBodyField(body, "description", description)
        cls.SetBodyField(body, "metadata", metadata, {})
        cls.SetBodyField(body, "settings", settings, {})
        cls.SetBodyField(body, "members", members, [])
        cls.SetBodyField(body, "rowversion", rowversion)
        return body

    @classmethod
    def PrepareConversionInput(cls, input=None, projectid=None, uploadurl=None, originalfilename=None, name=None, description=None, metadata=None, properties=None, readername=None, writername=None, readerparameters=None, writerparameters=None, transformations=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "projectId", projectid)
        cls.SetBodyField(body, "uploadUrl", uploadurl)
        cls.SetBodyField(body, "originalFilename", originalfilename)
        odd = body.get("outputDatasetData")
        if not odd:
            odd = {}
            cls.SetBodyField(body, "outputDatasetData", odd)
        cls.SetBodyField(odd, "name", name)
        cls.SetBodyField(odd, "description", description)
        cls.SetBodyField(odd, "metadata", metadata, {})
        cls.SetBodyField(odd, "properties", properties, {})
        cls.SetBodyField(body, "readerName", readername)
        cls.SetBodyField(body, "writerName", writername)
        cls.SetBodyField(body, "readerParameters", readerparameters, [])
        cls.SetBodyField(body, "writerParameters", writerparameters, [])
        cls.SetBodyField(body, "transformations", transformations, [])
        return body

    @classmethod
    def PrepareUpdateInput(cls, input=None, uploadurl=None, originalfilename=None, readername=None, writername=None, readerparameters=None, writerparameters=None, transformations=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "uploadUrl", uploadurl)
        cls.SetBodyField(body, "originalFilename", originalfilename)
        cls.SetBodyField(body, "readerName", readername)
        cls.SetBodyField(body, "writerName", writername)
        cls.SetBodyField(body, "readerParameters", readerparameters, [])
        cls.SetBodyField(body, "writerParameters", writerparameters, [])
        cls.SetBodyField(body, "transformations", transformations, [])
        return body

    @classmethod
    def PrepareAppendInput(cls, input=None, uploadurl=None, originalfilename=None, readername=None, writername=None, readerparameters=None, writerparameters=None, transformations=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "uploadUrl", uploadurl)
        cls.SetBodyField(body, "originalFilename", originalfilename)
        cls.SetBodyField(body, "readerName", readername)
        cls.SetBodyField(body, "writerName", writername)
        cls.SetBodyField(body, "readerParameters", readerparameters, [])
        cls.SetBodyField(body, "writerParameters", writerparameters, [])
        cls.SetBodyField(body, "transformations", transformations, [])
        return body

    @classmethod
    def PrepareDownloadDatasetInput(cls, input=None, dformat=None, srid=None, arguments=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "format", dformat)
        cls.SetBodyField(body, "srid", srid)
        cls.SetBodyField(body, "arguments", arguments, {})
        return body
    
    @classmethod
    def PrepareDownloadConvertDatasetInput(cls, input=None, targetfilename=None, readername=None, writername=None, readerparameters=None, writerparameters=None, transformations=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "targetFileName", targetfilename)
        cls.SetBodyField(body, "readerName", readername)
        cls.SetBodyField(body, "writerName", writername)
        cls.SetBodyField(body, "readerParameters", readerparameters, [])
        cls.SetBodyField(body, "writerParameters", writerparameters, [])
        cls.SetBodyField(body, "transformations", transformations, [])
        return body

    @classmethod
    def PrepareUploadInput(cls, input=None, projectid=None, inputformat=None, appenddatasetid=None, uploadurl=None, filename=None, srid=None, arguments=None, destinations=None, name=None, description=None, metadata=None, properties=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "projectId", projectid)
        cls.SetBodyField(body, "format", inputformat)
        cls.SetBodyField(body, "appenddatasetid", appenddatasetid)
        cls.SetBodyField(body, "uploadUrl", uploadurl)
        cls.SetBodyField(body, "filename", filename)
        cls.SetBodyField(body, "srid", srid)
        cls.SetBodyField(body, "arguments", arguments, {})
        cls.SetBodyField(body, "destinations", destinations, [])
        dsid = body.get("datasetImportData")
        if not dsid:
            dsid = {}
            cls.SetBodyField(body, "datasetImportData", dsid)
        cls.SetBodyField(dsid, "name", name)
        cls.SetBodyField(dsid, "description", description)
        cls.SetBodyField(dsid, "metadata", metadata, {})
        cls.SetBodyField(dsid, "properties", properties, {})
        return body

    @classmethod
    def PrepareCreateProjectMemberInput(cls, input=None, userid=None, role=None):
        body = input.copy() if input else {}
        cls.SetBodyField(body, "userid", userid)
        cls.SetBodyField(body, "role", role)
        return body


if __name__ == '__main__':
    print(__file__)
    print(dir())
