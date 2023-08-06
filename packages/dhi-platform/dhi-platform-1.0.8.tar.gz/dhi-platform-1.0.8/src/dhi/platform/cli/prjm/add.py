#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV3Contracts
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--adduserid", help="User id")
    parser.add_argument("--addrole", help="User role")

def main():
    args = ClientArgs.ParseForProject(description="Add project member", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    input = MetadataClientV3Contracts.PrepareCreateProjectMemberInput(
        ClientArgs.LoadJson(args.inputfile), userid=args.adduserid, role=args.addrole)
    response = clientv3.CreateProjectMemberV3(input, args.projectid)

    Format.FormatResponse(response, None, args.format)

if __name__ == '__main__':
    main()
