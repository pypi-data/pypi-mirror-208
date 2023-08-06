#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV3Contracts
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--actiontype", choices=["PathActionCreate", "PathActionCreateIfNotExists", "PathActionDelete"], action="append", help="File/folder path")
    parser.add_argument("--path", action="append", help="File/folder path")
    parser.add_argument("--isfolder", type=bool, action="append", help="Project description")
    parser.add_argument("--defaultaccesslevel", choices=["Confidential", "Private", "Shared"], help="Default access level for newly created subprojects/folders")
    parser.add_argument("--sastokenexpiration", help="Project members array JSON, []")

def main():
    args = ClientArgs.ParseForProject(description="Prepare files and subfolders", init=__initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    input = MetadataClientV3Contracts.PreparePrepareHierarchyInput(
        ClientArgs.LoadJson(args.inputfile),
        actiontype=args.actiontype,
        path=args.path,        
        isfolder=args.isfolder,
        defaultaccesslevel=args.defaultaccesslevel,
        sastokenexpiration=args.sastokenexpiration)
    response = clientv3.PrepareHierarchy(input, args.projectid)

    tablefields = ["id", "name"]
    Format.FormatResponse(response, lambda r: r.Body, args.format, None, tablefields)

if __name__ == '__main__':
    main()
