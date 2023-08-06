#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("transferids", metavar="transferid", help="Transfer id", nargs="+")

def main():
    args = ClientArgs.ParsePlatform(description="Transfers info", init=initParser, defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    responses = (clientv2.GetTransferV2(id) for id in args.transferids)

    tablefmt = "{!s:32}\t{!s:32}\t{!s:16}\t{!s:10}\t{!s:20}\t{!s:26}\t{}"
    tablefields = ["id", "projectId", "type", "status", "format", "createdAt", "updatedAt"]
    Format.FormatResponses(responses, lambda r: r.Body, args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
