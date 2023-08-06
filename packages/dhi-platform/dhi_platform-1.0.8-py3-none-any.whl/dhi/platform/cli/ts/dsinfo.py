#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.timeseriesgen import TimeSeriesGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForDatasetList(description="Get time series dataset details", defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = TimeSeriesGenClientV2(**vars(args))

    responses = (clientv2.GetTimeSeriesDatasetV2(args.projectid, id) for id in args.datasetids)

    tablefmt = "{!s:32}\t{}"
    tablefields = ["id", "items"]
    Format.FormatResponses(responses, lambda r: r.Body, args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
