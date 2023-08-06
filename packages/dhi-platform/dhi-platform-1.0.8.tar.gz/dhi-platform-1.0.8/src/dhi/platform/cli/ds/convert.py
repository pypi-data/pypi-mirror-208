#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV3, MetadataGenClientV2
from dhi.platform.metadatahelper import MetadataClientV2Helper, MetadataClientV3Contracts
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--uploadurl", help="Upload url")
    parser.add_argument("--uploadfile", help="Upload file")
    parser.add_argument("--originalfilename", help="Original file name")
    parser.add_argument("--name", help="Dataset name")
    parser.add_argument("--description", help="Dataset description")
    parser.add_argument("--metadata", help="Dataset metadata JSON, {}")
    parser.add_argument("--properties", help="Dataset properties JSON, {}")
    parser.add_argument("--readername", help="Reader name")
    parser.add_argument("--writername", help="Writer name")
    parser.add_argument("--readerparameters", help="Reader parameters array JSON, []")
    parser.add_argument("--writerparameters", help="Writer parameters array JSON, []")
    parser.add_argument("--transformations", help="Transformations array JSON, []")

def main():
    args = ClientArgs.ParseForProject(description="Convert into dataset", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))
    clientv2 = MetadataGenClientV2(**vars(args))

    tmpurl = None
    if args.uploadfile:
        tmpurl = MetadataClientV2Helper.UploadFromFile(args.uploadfile, clientv2)
        args.uploadurl = tmpurl

    input = MetadataClientV3Contracts.PrepareConversionInput(
        ClientArgs.LoadJson(args.inputfile),
        args.projectid,
        args.uploadurl,
        args.originalfilename,
        args.name,
        args.description,
        ClientArgs.LoadJsonStr(args.metadata),
        ClientArgs.LoadJsonStr(args.properties),
        args.readername,
        args.writername,
        ClientArgs.LoadJsonStr(args.readerparameters),
        ClientArgs.LoadJsonStr(args.writerparameters),
        ClientArgs.LoadJsonStr(args.transformations))
    response = clientv3.UploadConvertV3(input)

    tablefields = ["id", "type", "format", "status"]
    Format.FormatResponse(response, lambda r: r.Body, args.format, None, tablefields)

    if tmpurl:
        MetadataClientV2Helper.DeleteBlob(tmpurl)

if __name__ == '__main__':
    main()
