#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.enginegen import EngineGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForExecutionRunList(description="Get input for engine runs", defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = EngineGenClientV2(**vars(args))

    responses = (clientv2.GetExecutionInputs(args.projectid, id) for id in args.executionids)

    Format.FormatResponses(responses, lambda r: r.Body, args.format)

if __name__ == '__main__':
    main()
