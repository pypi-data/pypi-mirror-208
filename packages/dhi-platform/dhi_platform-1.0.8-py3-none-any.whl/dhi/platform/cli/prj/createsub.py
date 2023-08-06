#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV3Contracts
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--description", help="Project description")
    parser.add_argument("--accesslevel", choices=["Confidential", "Private", "Shared"], help="Project accel level")
    parser.add_argument("--metadata", help="Project metadata JSON, {}")
    parser.add_argument("--settings", help="Project settings JSON, {}")
    parser.add_argument("--members", help="Project members array JSON, []")

def main():
    args = ClientArgs.ParseForProject(description="Create subproject", init=initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    input = MetadataClientV3Contracts.PrepareCreateProjectInput(
        ClientArgs.LoadJson(args.inputfile),
        name=args.name,
        description=args.description,
        accesslevel=args.accesslevel,
        metadata=ClientArgs.LoadJsonStr(args.metadata),
        settings=ClientArgs.LoadJsonStr(args.settings),
        members=ClientArgs.LoadJsonStr(args.members))
    response = clientv3.CreateSubProjectV3(input, args.projectid)

    tablefields = ["id", "name"]
    Format.FormatResponse(response, lambda r: r.Body, args.format, None, tablefields)

if __name__ == '__main__':
    main()
