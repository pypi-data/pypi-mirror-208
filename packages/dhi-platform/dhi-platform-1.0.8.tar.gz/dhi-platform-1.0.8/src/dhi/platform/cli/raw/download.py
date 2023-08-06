#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.rawgen import RawGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForDatasetListOpt(description="Get downloads")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = RawGenClientV2(**vars(args))

    response = clientv2.GetDownloadDatasets(args.projectid, args.datasetids)

    tablefmt = "{!s:36}\t{!s:16}\t{}"
    tablefields = ["id", "name", "url"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
