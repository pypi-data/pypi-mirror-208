#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV3Contracts
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--uploadurl", help="Upload url")
    parser.add_argument("--originalfilename", help="Original file name")
    parser.add_argument("--readername", help="Reader name")
    parser.add_argument("--writername", help="Writer name")
    parser.add_argument("--readerparameters", help="Reader parameters array JSON, []")
    parser.add_argument("--writerparameters", help="Writer parameters array JSON, []")
    parser.add_argument("--transformations", help="Transformations array JSON, []")

def main():
    args = ClientArgs.ParseForDataset(description="Append into dataset", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdateDatasetFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    input = MetadataClientV3Contracts.PrepareAppendInput(
        ClientArgs.LoadJson(args.inputfile),
        args.uploadurl,
        args.originalfilename,
        args.readername,
        args.writername,
        ClientArgs.LoadJsonStr(args.readerparameters),
        ClientArgs.LoadJsonStr(args.writerparameters),
        ClientArgs.LoadJsonStr(args.transformations))
    response = clientv3.AppendDatasetV3(input, args.datasetid)

    tablefields = ["id", "type", "format", "status"]
    Format.FormatResponse(response, lambda r: r.Body, args.format, None, tablefields)

if __name__ == '__main__':
    main()
