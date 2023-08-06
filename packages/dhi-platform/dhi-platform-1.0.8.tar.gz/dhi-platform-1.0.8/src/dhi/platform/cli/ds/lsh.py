#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("--offset", default=0, help="Output offset")
    parser.add_argument("--limit", default=200, help="Limit output size")
    parser.add_argument("--datasettype", help="Dataset type")
    parser.add_argument("--includesastokens", help="Turn on to get SAS tokens", action="store_true")

def main():
    args = ClientArgs.ParseForProject(description="List datasets hierarchy", init=initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    response = clientv3.GetRecursiveDatasetListV3(args.projectid, args.offset, args.limit, args.datasettype, args.includesastokens)

    tablefmt = "{!s:32}\t{!s:10}\t{!s:26}\t{}"
    tablefields = ["id", "datasetType", "name", "relativePath"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
