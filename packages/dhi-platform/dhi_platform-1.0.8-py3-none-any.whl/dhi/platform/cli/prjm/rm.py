#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("userids", metavar="userid", help="User id", nargs="+")

def main():
    args = ClientArgs.ParseForProject(description="Remove project members", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    responses = (clientv3.DeleteProjectMemberV3(id, args.projectid) for id in args.userids)

    Format.FormatResponses(responses, None, args.format)

if __name__ == '__main__':
    main()
