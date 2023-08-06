#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.enginegen import EngineGenClientV2
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("engines", metavar="engine", help="Engine name", nargs="+")

def main():
    args = ClientArgs.ParsePlatform(description="Get engine info", init=__initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = EngineGenClientV2(**vars(args))

    responses = (clientv2.GetEngine(name) for name in args.engines)

    tablefmt = "{!s:10}\t{}"
    tablefields = ["name", "versions"]
    Format.FormatResponses(responses, lambda r: r.Body, args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
