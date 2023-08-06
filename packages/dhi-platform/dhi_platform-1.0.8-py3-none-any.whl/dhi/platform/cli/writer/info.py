#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("names", metavar="name", help="Writer name", nargs="+")

def main():
    args = ClientArgs.ParsePlatform(description="Writer info", init=initParser, defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    responses = (clientv2.GetWriterV2(n) for n in args.names)

    tablefmt = "{!s:32}\t{!s:16}\t{}"
    tablefields = ["name", "datasetFormat", "description"]
    Format.FormatResponses(responses, lambda r: r.Body, args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
