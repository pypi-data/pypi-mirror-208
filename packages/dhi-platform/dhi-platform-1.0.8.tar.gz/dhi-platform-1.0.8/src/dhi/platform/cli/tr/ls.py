#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("--fromtime", help="From time")
    parser.add_argument("--totime", help="To time")
    parser.add_argument("--status", help="Status filter")
    parser.add_argument("--offset", default=0, help="Output offset")
    parser.add_argument("--limit", default=50, help="Limit output size in one call")

def main():
    args = ClientArgs.ParseForProject(description="List transfers", init=initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    response = clientv2.GetProjectTransferListV2(args.projectid, args.fromtime, args.totime, args.status, args.offset, args.limit)

    tablefmt = "{!s:32}\t{!s:10}\t{!s:26}\t{!s:16}\t{}"
    tablefields = ["id", "status", "createdAt", "type", "format"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
