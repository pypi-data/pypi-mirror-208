#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV2Helper, MetadataClientV2Contracts
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--uploadurl", help="Upload url")
    parser.add_argument("--uploadfile", help="Upload file")
    parser.add_argument("--filename", help="File name")
    parser.add_argument("--destinationpath", help="Destination path")
    parser.add_argument("--createdestinationpathifnotexists", action="store_true", help="Create destination path")

def main():
    args = ClientArgs.ParseForProject(description="Upload file", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    tmpurl = None
    if args.uploadfile:
        tmpurl = MetadataClientV2Helper.UploadFromFile(args.uploadfile, clientv2)
        args.uploadurl = tmpurl

    input = MetadataClientV2Contracts.PrepareUploadStagedFilesInput(
        ClientArgs.LoadJson(args.inputfile),
        args.uploadurl,
        args.filename,
        args.destinationpath,
        args.createdestinationpathifnotexists)
    response = clientv2.UploadStagedFilesV2(input, args.projectid)

    tablefmt1 = "{!s:32}\t{}"
    tablefields1 = ["datasetId", "fileName"]
    tablefmt2 = "{!s:32}\t{}"
    tablefields2 = ["fileName", "message"]
    Format.FormatResponseItems(response, lambda r: [(r.Body.get("datasets"), tablefmt1, tablefields1), (r.Body.get("failures"), tablefmt2, tablefields2)], args.format)

    if tmpurl:
        MetadataClientV2Helper.DeleteBlob(tmpurl)

if __name__ == '__main__':
    main()
