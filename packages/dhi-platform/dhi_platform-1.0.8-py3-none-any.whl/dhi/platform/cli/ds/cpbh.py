#!/usr/bin/env python
from time import sleep
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV2Helper
from dhi.platform.generated.metadatagen import MetadataGenClientV2, StagedFileUploadInputV1, StagedFilesUploadInputV1
from dhi.platform.generated.rawgen import RawGenClientV2
from dhi.platform.fmt import Format
import os.path

def __initParser(parser):
    parser.add_argument("-s", "--sourcecontainerurl", default=None, help="Source container url")
    parser.add_argument("-f", "--sourcepath", default=None, help="Source files path")

def __getContainerBlobs(url: str, prefix: str):
    return MetadataClientV2Helper.ListBlobs(url, prefix)

def main():
    args = ClientArgs.ParseForProject(description="Copy blobs with hierarchy", init=__initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    rawclientv2 = RawGenClientV2(**vars(args))
    clientv2 = MetadataGenClientV2(**vars(args))
    stageblobs = None
    folders = dict()

    if args.sourcecontainerurl:
        for blob in __getContainerBlobs(args.sourcecontainerurl, args.sourcepath):
            relativefilepath = blob.name
            bloburl = blob.url
            name = os.path.basename(relativefilepath)
            relativepath = os.path.dirname(relativefilepath)

            folder = folders.get(relativepath)
            if not folder:
                folder = StagedFilesUploadInputV1(files=list(), destinationPath=relativepath, createDestinationPathIfNotExists=True)
                folders[relativepath] = folder

            if not stageblobs:
                response = rawclientv2.GetStagingUrls(args.projectid, 100)
                stageblobs = [x.get("url") for x in response.Body.get("data")]
            tmpurl = stageblobs.pop()

            print(f"Copy {relativepath}/{name} -> {tmpurl}")
            uploadresult = MetadataClientV2Helper.UploadBlobFromUrl(tmpurl, bloburl)
            print(f"  -> uploadresult: {uploadresult}")
            print(f"  -> copy {relativepath}/{name} done")

            folder.files.append(StagedFileUploadInputV1(url=tmpurl, fileName=name))

        # wait for copy operation to finish
        sleep(1.0)

        for folder in folders.values():
            filenames = ",".join((x.fileName for x in folder.files))
            print(f"Upload {filenames} into {folder.destinationPath}")
            clientv2.UploadStagedFilesV2(folder.to_dict(), args.projectid)
            print(f"  -> upload {filenames} into {folder.destinationPath} done")

if __name__ == '__main__':
    main()
