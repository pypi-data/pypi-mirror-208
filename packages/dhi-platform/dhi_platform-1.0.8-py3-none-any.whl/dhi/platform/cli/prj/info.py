#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForProjectList(description="Get projects details", defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    responses = (clientv3.GetProjectV3(id) for id in args.projectids)

    tablefmt = "{!s:36}\t{!s:16}\t{!s:16}\t{!s:26}\t{!s:14}\t{!s:26}\t{}"
    tablefields = ["id", "name", "description", "lastActivityAt", "accessLevel", "createdAt", "updatedAt"]
    Format.FormatResponses(responses, lambda r: r.Body, args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
