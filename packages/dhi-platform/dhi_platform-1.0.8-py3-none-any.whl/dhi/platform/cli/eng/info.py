#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.generated.enginegen import EngineGenClientV2
from dhi.platform.fmt import Format

def main():
    args = ClientArgs.ParseForExecutionRunList(description="Status for engine runs", defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = EngineGenClientV2(**vars(args))

    responses = (clientv2.GetExecution(args.projectid, id) for id in args.executionids)

    tablefmt = "{!s:36}\t{!s:25}\t{!s:28}\t{!s:14}\t{!s:14}\t{!s:9}\t{}"
    tablefields = ["executionId", "status", "createdAt", "preparation", "duration", "nodeCount", "engines"]
    Format.FormatResponses(responses, lambda r: r.Body, args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
