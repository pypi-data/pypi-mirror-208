#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV3Contracts
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--targetfilename", help="Target file name")
    parser.add_argument("--readername", help="Reader name")
    parser.add_argument("--writername", help="Writer name")
    parser.add_argument("--readerparameters", help="Reader parameters")
    parser.add_argument("--writerparameters", help="Writer parameters")
    parser.add_argument("--transformations", help="Transformations")

def main():
    args = ClientArgs.ParseForDataset(description="Download convert file", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    input = MetadataClientV3Contracts.PrepareDownloadConvertDatasetInput(
        ClientArgs.LoadJson(args.inputfile),
        args.targetfilename,
        args.readername,
        args.writername,
        ClientArgs.LoadJsonStr(args.readerparameters),
        ClientArgs.LoadJsonStr(args.writerparameters),
        ClientArgs.LoadJsonStr(args.transformations))
    response = clientv3.DownloadConvertDatasetV3(input, args.datasetid)

    Format.FormatResponse(response, lambda r: r.Body, args.format)

if __name__ == '__main__':
    main()
