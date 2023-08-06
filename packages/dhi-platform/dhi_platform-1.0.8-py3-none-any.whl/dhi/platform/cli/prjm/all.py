#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("-l", "--limit", default=50, help="Limit output size in one call")

def main():
    args = ClientArgs.ParsePlatform(description="List customers", init=initParser)
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    response = clientv3.GetUserList()

    tablefmt = "{!s:32}\t{!s:13}\t{!s:23}\t{!s:7}\t{!s:32}\t{!s:13}"
    tablefields = ["userId", "displayName", "email", "isAdmin", "customerId", "customerName"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
