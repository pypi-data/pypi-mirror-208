#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForProject(description="Get SAS token", defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    response = clientv2.GetSasTokenV2(args.projectid)

    Format.FormatResponse(response, None, args.format)

if __name__ == '__main__':
    main()
