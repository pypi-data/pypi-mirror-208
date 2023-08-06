#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForProjectList(description="Restore deleted project")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    responses = (clientv2.RestoreProjectV2(id) for id in args.projectids)
    Format.FormatResponses(responses)

if __name__ == '__main__':
    main()
