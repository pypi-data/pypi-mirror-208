#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV3Contracts
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--description", help="Project description")
    parser.add_argument("--metadata", help="Project metadata JSON, {}")
    parser.add_argument("--settings", help="Project settings JSON, {}")
    parser.add_argument("--members", help="Project members array JSON, []")
    parser.add_argument("--rowversion", help="Row version")

def main():
    args = ClientArgs.ParseForProject(description="Update project", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    input = MetadataClientV3Contracts.PrepareUpdateProjectInput(
        ClientArgs.LoadJson(args.inputfile),
        projectid=args.projectid,
        name=args.name,
        description=args.description,
        metadata=ClientArgs.LoadJsonStr(args.metadata),
        settings=ClientArgs.LoadJsonStr(args.settings),
        members=ClientArgs.LoadJsonStr(args.members),
        rowversion=args.rowversion)
    response = clientv3.UpdateProjectV3(input)

    tablefields = ["id", "name"]
    Format.FormatResponse(response, lambda r: r.Body, args.format, None, tablefields)

if __name__ == '__main__':
    main()
