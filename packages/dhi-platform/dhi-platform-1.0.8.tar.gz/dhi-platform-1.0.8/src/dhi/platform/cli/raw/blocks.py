#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.rawgen import RawGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForDatasetPos(description="Get dataset blocks", defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = RawGenClientV2(**vars(args))

    response = clientv2.GetDatasetBlocksChecksums(args.projectid, args.datasetid)

    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format)

if __name__ == '__main__':
    main()
