#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("--fromtime", help="From time")
    parser.add_argument("--totime", help="To time")
    parser.add_argument("--status", help="Status filter")

def main():
    args = ClientArgs.ParsePlatform(description="List transfer summaries", init=initParser)
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    response = clientv2.GetTransferListV2(args.fromtime, args.totime, args.status)

    tablefmt = "{!s:32}\t{!s:10}\t{!s:26}\t{!s:16}\t{}"
    tablefields = ["id", "status", "createdAt", "type", "format"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
