#!/usr/bin/env python
from dhi.platform.args import ClientArgs
from dhi.platform.config import ClientConfig
from dhi.platform.enginehelper import EnginesClientV2Contracts
from dhi.platform.fmt import Format
from dhi.platform.generated.enginegen import EngineGenClientV2

def __initParser(parser):
    parser.add_argument("--sortby", help="Sort by field", choices=["ExecutionId", "Status", "ProjectId", "CreatedAt", "StartedAt", "UpdatedAt", "FinishedAt", "EngineName", "PoolType", "NodeCount", "TotalNumberOfSetups", "ScenarioName"])
    parser.add_argument("--asc", dest="sortorder", help="Use for ascending order", action="store_const", const="Asc")
    parser.add_argument("--desc", dest="sortorder", help="Use for descending order", action="store_const", const="Desc")
    parser.add_argument("--starttime", help="Start time filter")
    parser.add_argument("--endtime", help="End time filter")
    parser.add_argument("--scenarioname", help="Scenario name filter")
    parser.add_argument("--status", help="Status filter", choices=["Pending", "SettingUpComputeResources", "EvaluatingInputSize", "DownloadingInputFiles", "InProgress", "UploadingResults", "Success", "Failure", "Cancelling", "Cancelled", "Deleting"], nargs="+")
    parser.add_argument("--project", help="Project filter", nargs="+")
    parser.add_argument("--limit", type=int, help="Limit output size in one call")

def main():
    args = ClientArgs.ParseForProject(description="Get list of my execution runs", init=__initParser)
    ClientConfig.UpdateProjectFromConfiguration(args)
    clientv2 = EngineGenClientV2(**vars(args))

    def getResponses():
        cursor = None
        nextlink = None
        while True:
            if cursor:
                response = clientv2.GetMyExecutions(cursor=cursor)
            else:
                response = clientv2.GetMyExecutions(args.sortby, args.sortorder, args.starttime, args.endtime, args.scenarioname, args.status, args.project, args.limit, cursor=cursor)
            yield response
            cursor = response.Body.get("cursor")
            nextlink = response.Body.get("@nextLink")
            listobjdata = response.Body.get("data")
            if (not cursor and not nextlink) or not listobjdata:
                break
    responses = getResponses()

    def getList(r):
        return [EnginesClientV2Contracts.SetComputedDuration(EnginesClientV2Contracts.SetComputedPreparation(x)) for x in r.Body.get("data")]
    tablefmt = "{!s:36}\t{!s:25}\t{!s:28}\t{!s:14}\t{!s:14}\t{!s:9}\t{}"
    tablefields = ["executionId", "status", "createdAt", "preparation", "duration", "nodeCount", "engines"]
    Format.FormatResponses(responses, getList, args.format, tablefmt, tablefields)

if __name__ == '__main__':
    main()
