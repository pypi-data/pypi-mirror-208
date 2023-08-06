#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForProjectList(description="Get project capabilities", defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    responses = (clientv3.GetProjectCapabilitiesV3(id) for id in args.projectids)

    tablefields = ["canEdit", "canEditAccessLevel", "canDelete", "canGrantAccess", "canCreateContent", "canListContent", "canUpdateContent", "canDeleteContent", "canReadContent"]
    Format.FormatResponses(responses, lambda r: r.Body, args.format, None, tablefields)

if __name__ == '__main__':
    main()
