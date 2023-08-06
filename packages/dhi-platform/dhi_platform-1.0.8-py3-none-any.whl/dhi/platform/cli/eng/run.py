#!/usr/bin/env python
import asyncio, platform
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.eventinghelper import ExecutionSession
from dhi.platform.generated.enginegen import EngineGenClientV2
from dhi.platform.generated.metadatagen import MetadataGenClientV2, MetadataGenClientV3
from dhi.platform.fmt import Format

def __initParser(parser):
    parser.add_argument("-f", "--inputfile", default=ClientArgs.GetDefault("DHIINPUT"), help="Input file path")
    parser.add_argument("--pooltype", help="Pool type", choices=["VM-S-5", "VM-S-40", "VM-S-100", "VM-H-60", "VM-G-5", "VM-G-40"])
    parser.add_argument("--nodecount", type=int, help="Node count")
    parser.add_argument("--maxtime", type=float, help="Max execution time [hours]")
    parser.add_argument("-w", "--wait", default=False, help="Wait to finish", action="store_true")
    parser.add_argument("-l", "--showlog", default=False, help="Show log", action="store_true")

async def main():
    args = ClientArgs.ParseForProject(description="Run engine", init=__initParser, defaultformat="yaml")
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = EngineGenClientV2(**vars(args))

    metadataclientv2 = MetadataGenClientV2(**vars(args))
    metadataclientv3 = MetadataGenClientV3(**vars(args))
    executionsession = ExecutionSession(args.showlog, metadataclientv2, metadataclientv3, args.verbose)
    async with executionsession.subscribe(args.projectid, ["/dhi/platform/engineexecution"], 200, None):
        try:
            await executionsession.wait_pubsubconnected()

            input = ClientArgs.LoadJson(args.inputfile)
            options = input.get("options")
            if not options:
                options = dict()
                input["options"] = options
            if args.pooltype:
                options["poolType"] = args.pooltype
            if args.nodecount:
                options["nodeCount"] = args.nodecount
            if args.maxtime:
                options["maxExecutionElapsedTimeHours"] = args.maxtime
            if args.showlog:
                inputitems = input.get("inputs")
                if inputitems:
                    for i in inputitems:
                        if i.get("engine"):
                            tmp = i.get("reportLogUpdatesLines")
                            if not tmp or tmp == 0:
                                i["reportLogUpdatesLines"] = 300
            response = clientv2.RunExecution(args.projectid, input)

            executionsession.set_resourceid(response.Body.get("executionId"))

            tablefields = ["executionId", "outputLocation"]
            Format.FormatResponse(response, lambda r: r.Body, args.format, None, tablefields)

            if args.wait:
                await executionsession.wait_finished()
        finally:
            await executionsession.wait(0)

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
