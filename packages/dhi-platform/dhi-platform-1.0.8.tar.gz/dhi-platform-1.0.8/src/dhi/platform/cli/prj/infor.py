#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForProjectList(description="Get details about deleted project", defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    responses = (clientv2.GetRecyclableProjectV2(id) for id in args.projectids)

    tablefmt = "{!s:36}\t{!s:16}\t{!s:14}\t{!s:26}\t{!s:26}\t{}"
    tablefields = ["id", "name", "accessLevel", "createdAt", "updatedAt", "deletedAt"]
    Format.FormatResponses(responses, lambda r: r.Body, args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
