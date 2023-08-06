#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.enginegen import EngineGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParsePlatform(description="Get available configurations")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = EngineGenClientV2(**vars(args))

    response = clientv2.GetAllConfigurations()

    tablefmt = "{!s:10}\t{:13}\t{:8}"
    tablefields = ["poolType", "numberOfCores", "gpuCount"]
    Format.FormatResponse(response, lambda r: r.Body.get("data"), args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
