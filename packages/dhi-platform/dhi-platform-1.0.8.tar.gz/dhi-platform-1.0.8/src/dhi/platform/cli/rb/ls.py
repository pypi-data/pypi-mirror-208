#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV1
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("--offset", default=0, help="Output offset")
    parser.add_argument("--limit", default=200, help="Limit output size")

def main():
    args = ClientArgs.ParsePlatform(description="Get all deleted items", init=initParser)
    ClientConfig.UpdatePlatformFromConfiguration(args)
    client1 = MetadataGenClientV1(**vars(args))

    response = client1.GetAllDeletedItems(offset=args.offset, limit=args.limit)

    tablefmt = "{!s:10}\t{!s:10}\t{!s:32}\t{!s:32}\t{}"
    tablefields = ["itemType", "datasetType", "id", "projectId", "name"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
