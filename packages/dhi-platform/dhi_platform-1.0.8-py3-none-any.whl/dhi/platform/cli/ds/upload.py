#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.metadatahelper import MetadataClientV3Contracts
from dhi.platform.generated.metadatagen import MetadataGenClientV3
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    #format: string
    #projectId: 3fa85f64-5717-4562-b3fc-2c963f66afa6
    #appendDatasetId: 3fa85f64-5717-4562-b3fc-2c963f66afa6
    #uploadUrl: string
    #fileName: string
    #srid: 0
    #arguments: {}
    #destinations:
    #  - Dedicated
    #datasetImportData:
    #  name: string
    #  description: string
    #  metadata: {}
    #  properties: {}
    parser.add_argument("--inputformat", help="Input format")
    parser.add_argument("--appenddatasetid", help="Append dataset id")
    parser.add_argument("--uploadurl", help="Upload URL")
    parser.add_argument("--filename", help="File name")
    parser.add_argument("--srid", help="SRID")
    parser.add_argument("--arguments", help="Arguments JSON, {}")
    parser.add_argument("--destinations", default="[\"Dedicated\"]", help="Destinations array JSON, []")
    parser.add_argument("--name", help="Name")
    parser.add_argument("--description", help="Description")
    parser.add_argument("--metadata", help="Dataset metadata JSON, {}")
    parser.add_argument("--properties", help="Dataset properties JSON, {}")

def main():
    args = ClientArgs.ParseForProject(description="Upload file", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv3 = MetadataGenClientV3(**vars(args))

    input = MetadataClientV3Contracts.PrepareUploadInput(
        ClientArgs.LoadJson(args.inputfile),
        args.projectid,
        args.inputformat,
        args.appenddatasetid,
        args.uploadurl,
        args.filename,
        args.srid,
        ClientArgs.LoadJsonStr(args.arguments),
        ClientArgs.LoadJsonStr(args.destinations),
        args.name if args.name else args.filename,
        args.description,
        ClientArgs.LoadJsonStr(args.metadata),
        ClientArgs.LoadJsonStr(args.properties))
    response = clientv3.UploadV3(input)

    Format.FormatResponse(response, format=args.format)

if __name__ == '__main__':
    main()
