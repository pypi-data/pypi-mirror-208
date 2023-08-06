#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("--filter", choices=["All", "File", "Dedicated"], help="Filter")

def main():
    args = ClientArgs.ParsePlatform(description="List readers", init=initParser)
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    response = clientv2.GetReadersListV2(args.filter)

    tablefmt = "{!s:32}\t{!s:16}\t{}"
    tablefields = ["name", "datasetFormat", "description"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
