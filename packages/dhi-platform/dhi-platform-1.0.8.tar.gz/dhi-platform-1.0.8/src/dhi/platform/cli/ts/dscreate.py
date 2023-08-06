#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.timeserieshelper import TimeSeriesV2Contracts
from dhi.platform.generated.timeseriesgen import TimeSeriesGenClientV2
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", help="Input file path, '-' to read stdin")
    parser.add_argument("--schemaproperties", help="Time series schema properties")
    parser.add_argument("--name", help="Time series name")
    parser.add_argument("--description", help="Time series description")
    parser.add_argument("--metadata", help="Time series metadata JSON, {}")
    parser.add_argument("--properties", help="Time series settings JSON, {}")

def main():
    args = ClientArgs.ParseForProject(description="Create time series", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = TimeSeriesGenClientV2(**vars(args))

    input = TimeSeriesV2Contracts.PrepareCreateTimeseriesDatasetV2Input(
        ClientArgs.LoadJson(args.inputfile),
        schemaproperties=args.schemaproperties,
        name=args.name,
        description=args.description,
        metadata=ClientArgs.LoadJsonStr(args.metadata),
        properties=ClientArgs.LoadJsonStr(args.properties))
    response = clientv2.CreateTimeseriesDatasetV2(args.projectid, input)

    tablefields = ["id", "name"]
    Format.FormatResponse(response, lambda r: r.Body, args.format, None, tablefields)

if __name__ == '__main__':
    main()
