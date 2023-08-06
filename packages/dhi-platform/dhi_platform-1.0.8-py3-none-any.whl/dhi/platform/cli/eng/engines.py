#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.enginegen import EngineGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParsePlatform(description="Get available engines")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = EngineGenClientV2(**vars(args))

    response = clientv2.GetAllEngines()

    tablefmt = "{!s:10}\t{}"
    tablefields = ["name", "versions"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
