#!/usr/bin/env python
from time import sleep
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV2Helper
from dhi.platform.generated.metadatagen import MetadataGenClientV2, MetadataGenClientV3, StagedFileUploadInputV1, StagedFilesUploadInputV1
from dhi.platform.generated.rawgen import RawGenClientV2
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-s", "--sourceprojectid", default=None, help="Source projectid")

def __getProjectDatasets(clientv3: MetadataGenClientV3, projectid: str):
    offset = 0
    totalcount = 1
    while offset < totalcount:
        response = clientv3.GetRecursiveDatasetListV3(projectid, offset=offset, datasettype="file")

        totalcount = response.Body.get("totalCount")
        data = response.Body.get("data")
        offset += len(data)

        for dataset in data:
            yield dataset

def main():
    args = ClientArgs.ParseForProject(description="Copy datasets with hierarchy", init=__initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    rawclientv2 = RawGenClientV2(**vars(args))
    clientv2 = MetadataGenClientV2(**vars(args))
    clientv3 = MetadataGenClientV3(**vars(args))
    stageblobs = None
    folders = dict()

    if args.sourceprojectid:
        for dataset in __getProjectDatasets(clientv3, args.sourceprojectid):
            name = dataset.get("name")
            relativepath = dataset.get("relativePath")
            relativepath = relativepath.rstrip("/") if relativepath else ""
            dataseturl = dataset.get("datasetUrl")

            folder = folders.get(relativepath)
            if not folder:
                folder = StagedFilesUploadInputV1(files=list(), destinationPath=relativepath, createDestinationPathIfNotExists=True)
                folders[relativepath] = folder

            if not stageblobs:
                response = rawclientv2.GetStagingUrls(args.projectid, 100)
                stageblobs = [x.get("url") for x in response.Body.get("data")]
            tmpurl = stageblobs.pop()

            print(f"Copy {relativepath}/{name} -> {tmpurl}")
            uploadresult = MetadataClientV2Helper.UploadBlobFromUrl(tmpurl, dataseturl)
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
