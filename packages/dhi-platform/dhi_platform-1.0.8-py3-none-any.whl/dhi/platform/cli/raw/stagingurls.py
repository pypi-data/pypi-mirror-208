#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.rawgen import RawGenClientV2
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("--count", help="Count of staging blobs to get")

def main():
    args = ClientArgs.ParseForProject(description="Get staging urls", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = RawGenClientV2(**vars(args))

    response = clientv2.GetStagingUrls(args.projectid, args.count)

    tablefmt = "{}"
    tablefields = ["url"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
