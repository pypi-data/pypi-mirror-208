#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForProjectList(description="Delete projects")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    responses = (clientv3.DeleteProjectV3(id) for id in args.projectids)
    Format.FormatResponses(responses)

if __name__ == '__main__':
    main()
