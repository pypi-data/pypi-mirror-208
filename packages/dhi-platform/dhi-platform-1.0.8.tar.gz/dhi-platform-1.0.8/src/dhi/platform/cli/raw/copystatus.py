#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.rawgen import RawGenClientV2
from dhi.platform.rawhelper import RawClientV2Contracts
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--id", action="append", help="Dataset id")
    parser.add_argument("--copyoperationid", action="append", help="Copy operation id")

def main():
    args = ClientArgs.ParseForProject(description="Get copy status", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = RawGenClientV2(**vars(args))

    input = RawClientV2Contracts.PrepareGetCopyFileStatusInput(
        ClientArgs.LoadJson(args.inputfile),
        id=args.id,
        copyoperationid=args.copyoperationid)
    response = clientv2.GetCopyFilesStatus(args.projectid, input)

    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format)

if __name__ == '__main__':
    main()
