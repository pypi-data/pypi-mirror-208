#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("--nameprefix", help="Name prefix")
    parser.add_argument("--offset", default=0, help="Output offset")
    parser.add_argument("--limit", default=200, help="Limit output size in one call")

def main():
    args = ClientArgs.ParseForProject(description="List projects hierarchy", init=initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    response = clientv3.GetRecursiveProjectListV3(args.projectid, offset=args.offset, limit=args.limit)

    tablefmt = "{!s:32}\t{}"
    tablefields = ["id", "relativePath"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
