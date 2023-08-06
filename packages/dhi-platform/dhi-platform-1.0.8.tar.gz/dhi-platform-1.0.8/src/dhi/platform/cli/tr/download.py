#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.metadatahelper import MetadataClientV2Helper
from dhi.platform.fmt import Format

def initParser(parser):
    parser.add_argument("transferid", help="Transfer id")
    parser.add_argument("--outputpath", help="Output path")

def main():
    args = ClientArgs.ParsePlatform(description="Transfer download", init=initParser, defaultformat="yaml")
    ClientConfig.UpdatePlatformFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    response = clientv2.GetTransferV2(args.transferid)

    Format.FormatResponse(response, lambda r: r.Body, args.format)

    if response.Body.get("status") == "Completed":
        url = response.Body.get("downloadPath")
        if url:
            MetadataClientV2Helper.DownloadBlobToFile(url, args.outputpath)

if __name__ == '__main__':
    main()
