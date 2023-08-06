#!/usr/bin/env python
import datetime
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.enginehelper import EnginesClientV2Contracts
from dhi.platform.fmt import Format
from dhi.platform.generated.enginegen import EngineGenClientV2

def __initParser(parser):
    parser.add_argument("--starttime", help="Start time")
    parser.add_argument("--endtime", help="End time")


def main():
    args = ClientArgs.ParseForProject(description="Get list of execution runs", init=__initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = EngineGenClientV2(**vars(args))

    def getResponses():
        cursor = None
        nextlink = None
        while True:
            #if nextlink:
            #    response = clientv2.GetExecutions(args.projectid, nextlink=nextlink)
            if cursor:
                response = clientv2.GetExecutions(args.projectid, cursor=cursor)
            else:
                response = clientv2.GetExecutions(args.projectid, starttime=args.starttime, endtime=args.endtime, cursor=cursor)
            yield response
            cursor = response.Body.get("cursor")
            nextlink = response.Body.get("@nextLink")
            listobjdata = response.Body.get("data")
            if (not cursor and not nextlink) or not listobjdata:
                break
    responses = getResponses()

    def getList(r):
        l = [EnginesClientV2Contracts.SetComputedDuration(EnginesClientV2Contracts.SetComputedPreparation(x)) for x in r.Body.get("data")]
        l.sort(reverse=True, key=lambda x: x.get("createdAt"))
        return l
    tablefmt = "{!s:36}\t{!s:25}\t{!s:28}\t{!s:14}\t{!s:14}\t{!s:9}\t{}"
    tablefields = ["executionId", "status", "createdAt", "preparation", "duration", "nodeCount", "engines"]
    Format.FormatResponses(responses, getList, args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
