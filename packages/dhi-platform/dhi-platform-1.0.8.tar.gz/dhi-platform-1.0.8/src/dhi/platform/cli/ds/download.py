#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV3Contracts
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--dformat", default="file", help="Format")
    parser.add_argument("--srid", type=int, help="SRID")
    parser.add_argument("--arguments", help="Arguments")
    parser.add_argument("datasetid", help="Dataset id")

def main():
    args = ClientArgs.ParsePlatform(description="Download file", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    input = MetadataClientV3Contracts.PrepareDownloadDatasetInput(
        ClientArgs.LoadJson(args.inputfile),
        args.dformat,
        args.srid,
        ClientArgs.LoadJsonStr(args.arguments))
    response = clientv3.DownloadDatasetV3(input, args.datasetid)

    Format.FormatResponse(response, lambda r: r.Body, args.format)

if __name__ == '__main__':
    main()
