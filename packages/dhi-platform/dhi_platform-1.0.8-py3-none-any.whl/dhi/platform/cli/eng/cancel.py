#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.enginegen import EngineGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForExecutionRunList(description="Cancel execution runs", defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = EngineGenClientV2(**vars(args))

    responses = (clientv2.CancelExecution(args.projectid, id) for id in args.executionids)
    Format.FormatResponses(responses)

if __name__ == '__main__':
    main()
