#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("services", metavar="service", help="Service name", nargs="+")

def main():
    args = ClientArgs.ParsePlatform(description="Get service base URL", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    responses = (clientv3.GetServiceUrlV3(name) for name in args.services)

    Format.FormatResponses(responses, lambda r: r.Body, args.format)

if __name__ == '__main__':
    main()
