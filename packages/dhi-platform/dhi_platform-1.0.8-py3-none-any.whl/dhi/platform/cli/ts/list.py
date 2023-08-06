#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.timeseriesgen import TimeSeriesGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForDatasetPos(description="List time series")
    ClientConfig.UpdateDatasetFromConfiguration(args)
    clientv2 = TimeSeriesGenClientV2(**vars(args))

    response = clientv2.GetAllTimeSeriesV2(args.projectid, args.datasetid)

    tablefmt = "{!s:32}\t{}"
    tablefields = ["id", "item"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
