#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("--nameprefix", help="Name prefix")
    parser.add_argument("--role", help="Role")
    parser.add_argument("--capability", help="Capability")
    parser.add_argument("--sortby", help="Sort by")
    parser.add_argument("--sortorder", help="Sort order")
    parser.add_argument("--limit", default=50, help="Limit output size in one call")

def main():
    args = ClientArgs.ParseForProject(description="List subprojects", init=initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    def getResponses():
        cursor = None
        while True:
            response = clientv3.GetSubProjectListV3(args.projectid, nameprefix=args.nameprefix, role=args.role, capability=args.capability, sortby=args.sortby, sortorder=args.sortorder, cursor=cursor, limit=args.limit)
            yield response
            cursor = response.Body.get("cursor")
            listobjdata = response.Body.get("data")
            if not cursor or not listobjdata:
                break
    responses = getResponses()

    tablefmt = "{!s:32}\t{}"
    tablefields = ["id", "name"]
    Format.FormatResponses(responses, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
