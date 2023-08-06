#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForProject(description="Get project path")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    response = clientv3.GetProjectPathV3(args.projectid)

    tablefmt = "{!s:32}\t{!s:26}\t{!s:12}\t{!s:16}\t{}"
    tablefields = ["id", "name", "accessLevel", "inheritsMembers", "efectiveUserRole"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
