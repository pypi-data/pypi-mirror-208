#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.metadatagen import MetadataGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForDatasetList(description="Get details about deleted dataset", defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = MetadataGenClientV2(**vars(args))

    responses = (clientv2.GetRecyclableDatasetV2(id) for id in args.datasetids)

    tablefmt = "{!s:32}\t{!s:32}\t{!s:16}\t{!s:11}\t{!s:13}\t{!s:11}\t{!s:26}\t{}"
    tablefields = ["id", "projectId", "name", "datasetType", "datasetFormat", "storageSize", "createdAt", "updatedAt"]
    Format.FormatResponses(responses, lambda r: r.Body, args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
