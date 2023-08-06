#!/usr/bin/env python
from time import sleep
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV2Helper
from dhi.platform.generated.metadatagen import MetadataGenClientV2, StagedFilesUploadInputV1, StagedFileUploadInputV1
from dhi.platform.generated.rawgen import RawGenClientV2
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-s", "--sourceprojectid", default=None, help="Source projectid")

def __getSelectedDatasets(rawclientv2: RawGenClientV2, sourceprojectid: str, datasetids: list):
    response = rawclientv2.GetDownloadDatasets(sourceprojectid, datasetids)
    return (x for x in response.Body.get("data"))

def main():
    args = ClientArgs.ParseForDatasetListOpt(description="Copy selected datasets", init=__initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    rawclientv2 = RawGenClientV2(**vars(args))
    clientv2 = MetadataGenClientV2(**vars(args))
    stageblobs = None
    input = StagedFilesUploadInputV1()
    input.files = list()

    if args.datasetids:
        for dataset in __getSelectedDatasets(rawclientv2, args.sourceprojectid, args.datasetids):
            print(f"dataset: {dataset}")

            name = dataset.get("name")
            dataseturl = dataset.get("url")

            if not stageblobs:
                response = rawclientv2.GetStagingUrls(args.projectid, 10)
                stageblobs = [x.get("url") for x in response.Body.get("data")]
            tmpurl = stageblobs.pop()

            print(f"Copy {name} -> {tmpurl}")
            uploadresult = MetadataClientV2Helper.UploadBlobFromUrl(tmpurl, dataseturl)
            print(f"  -> uploadresult: {uploadresult}")
            print(f"  -> copy {name} done")

            file = StagedFileUploadInputV1()
            file.fileName = name
            file.url = tmpurl
            input.files.append(file)

        # wait for copy operations to finish
        sleep(1.0)

        print(f"Upload staged files")
        clientv2.UploadStagedFilesV2(input.to_dict(), args.projectid)
        print(f"  -> upload done")

if __name__ == '__main__':
    main()
