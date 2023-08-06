#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParsePlatform(description="List deleted projects")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    response = clientv2.GetRecyclableProjectListV2()

    tablefmt = "{!s:32}\t{!s:20}\t{!s:27}\t{!s:32}"
    tablefields = ["id", "name", "deletedAt", "deletedBy"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
