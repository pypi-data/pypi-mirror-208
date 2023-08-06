#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("--includesastokens", help="true to get SAS tokens", action="store_true")

def main():
    args = ClientArgs.ParseForProject(description="Get datasets", init=initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    response = clientv3.GetDatasetListV3(args.projectid, args.includesastokens)

    tablefmt = "{!s:32}\t{}"
    tablefields = ["id", "name"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
