#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.timeserieshelper import TimeSeriesV2Contracts
from dhi.platform.generated.timeseriesgen import TimeSeriesGenClientV2
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--id", help="Time series id")
    parser.add_argument("--name", help="Time series name")
    parser.add_argument("--unit", help="Time series unit")
    parser.add_argument("--item", help="Time series item (eum)")
    parser.add_argument("--datatype", help="Time series data type")
    parser.add_argument("--timeseriestype", help="Time series type")
    parser.add_argument("--properties", help="Time series settings JSON, {}")
    parser.add_argument("--datafileds", help="Time series data fields JSON, []")

def main():
    args = ClientArgs.ParseForDatasetPos(description="Add time series", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdateDatasetFromConfiguration(args)
    clientv2 = TimeSeriesGenClientV2(**vars(args))

    input = TimeSeriesV2Contracts.PrepareAddTimeSeriesV2Input(
        ClientArgs.LoadJson(args.inputfile),
        id=args.id,
        name=args.name,
        unit=args.unit,
        item=args.item,
        datatype=args.datatype,
        timeseriestype=args.timeseriestype,
        properties=ClientArgs.LoadJsonStr(args.properties),
        datafileds=ClientArgs.LoadJsonStr(args.datafileds))
    response = clientv2.AddTimeSeriesV2(args.projectid, input, args.datasetid)

    tablefields = ["id", "name"]
    Format.FormatResponse(response, lambda r: r.Body, args.format, None, tablefields)

if __name__ == '__main__':
    main()
