#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.rawhelper import RawClientV2Contracts
from dhi.platform.generated.rawgen import RawGenClientV2
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--id", action="append", help="Dataset id")
    parser.add_argument("--sastoken", action="append", help="SAS token")
    parser.add_argument("--name", action="append", help="File name")
    parser.add_argument("--url", action="append", help="Source data URL")
    parser.add_argument("--lastmodified", action="append", help="File last modification time")
    parser.add_argument("--size", action="append", help="File size")
    parser.add_argument("--forcecopy", action="append", help="Set to ")

def main():
    args = ClientArgs.ParseForProject(description="Upload files", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = RawGenClientV2(**vars(args))

    input = RawClientV2Contracts.PrepareUploadBulkFilesInput(
        ClientArgs.LoadJson(args.inputfile),
        id=args.id,
        sastoken=args.sastoken,
        name=args.name,
        url=args.url,
        lastmodified=args.lastmodified,
        size=args.size,
        forcecopy=args.forcecopy)
    response = clientv2.UploadBulkFiles(args.projectid, input)

    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format)

if __name__ == '__main__':
    main()
