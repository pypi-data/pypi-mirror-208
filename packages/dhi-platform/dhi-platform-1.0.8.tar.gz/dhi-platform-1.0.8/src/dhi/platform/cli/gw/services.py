#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParsePlatform(description="List services", defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    response = clientv3.GetServiceIds()

    tablefmt = "{}"
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, None)

if __name__ == '__main__':
    main()
