# Copyright (c) 2021 DHI A/S - DHI Water Environment Health 
# All rights reserved.
# 
# This code is licensed under the MIT License.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import datetime
from typing import List

from dhi.platform.base.exceptions import MikeCloudException

from dhi.platform.base.utils import sanitize_from_to
from dhi.platform.eventing import EngineSubscription
from .generated.enginegen import EngineExecutionDiagnosticsOutputV2, EngineExecutionInputOutputV2, EngineExecutionInputParametersV2, EngineExecutionOutputV2, EngineExecutionParametersV2, EngineExecutionSummaryOutputV2, EngineGenClientV2, EngineGetOutputV2, EngineInputItemV2, EngineModelItemV2, EngineOutputItemV2, EngineOutputPlatformItemV2, EngineRunOutputV2, EngineRunParameterV2, GetConfigurationOutputV2, OptionsV2

class EngineExecutionInputBuilderBase():
    
    def __init__(self) -> None:
        self._scenario_name = None
        self._options = None
        self._output = None
        self._input = None

    @property 
    def scenario_name(self):
        return self._scenario_name

    @property
    def options(self):  
        return self._options
    
    @property
    def output(self):
        return self._output
    
    @property
    def input(self):
        return self._input
    
    def _validate(self):
        messages = []
        
        if self._options is None:
            messages.append("Options are required")
        else:
            opts = self._options
            if not opts.poolType:
                messages.append("Pool type option is required")
            if not opts.nodeCount:
                messages.append("Node count option is required")
            if not opts.maxExecutionElapsedTimeHours:
                messages.append("Positive Maximum Execution Elaps Time Hous option is required")
        
        if messages:
            raise MikeCloudException("Execution input is invalid", messages)
    
    def with_options(self, pool_type:str, node_count:str, max_elapsed_time:float=24.0):
        max_elapsed_time = float(max_elapsed_time)
        self._options = OptionsV2(pool_type, node_count, max_elapsed_time)
        return self
    
    def with_max_execution_elapsed_time_hours(self, hours:int):
        self._maxExecutionElapsedTimeHours = hours
        return self
    
    def with_scenario_name(self, name:str):
        self._scenario_name = name
        return self
    
    def with_output(self, output:List[EngineOutputItemV2]):
        self._output = output
        return self


class EngineExecutionInputBuilder(EngineExecutionInputBuilderBase):

    def __init__(self) -> None:
        super().__init__()
        self._input = None
        self._platform_output = None

    def _validate(self):
        super()._validate()
    
    def with_input(self, input:List[EngineInputItemV2]):
        self._input = input
        return self

    def with_platform_output(self, platform_output:List[EngineOutputPlatformItemV2]):
        self._platform_output = platform_output
        return self

    def build(self) -> EngineExecutionParametersV2:
        
        self._validate()

        parameters = EngineExecutionParametersV2(
            self._input,
            self.output,
            self._platform_output,
            self.options,
            self.scenario_name
        )

        return parameters


class EngineExecutionInputParametersBuilder(EngineExecutionInputBuilderBase):
    
    def __init__(self) -> None:
        super().__init__()
        self._models = None
    
    def _validate(self):
        super()._validate()
        messages = []

        for model in self._models:
            if not model.resultsRelativePath:
                messages.append(f"Model {model} must have 'resultsRelativePath'")

        if messages:
            raise MikeCloudException('Cannot build EngineExecutionParametersV2', messages)

    def with_models(self, models=List[EngineModelItemV2]):
        self._models = models
        return self

    def build(self) -> EngineExecutionParametersV2:
        
        self._validate()

        parameters = EngineExecutionInputParametersV2(
            self._models,
            self.output,
            self.options,
            self.scenario_name
        )

        return parameters


class EngineClient(EngineGenClientV2):
    def __init__(self, inspectFnc=EngineGenClientV2.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)

    @staticmethod
    def _page_to_list(t, response):
        return [t.from_dict(d) for d in response.Body["data"]]
    
    def get_execution(self, project_id, execution_id) -> EngineExecutionOutputV2:
        """
        Get multidimensional dataset details
        
        :param project_id: ID of the project to get an execution from
        :param execution_id: ID of the execution
        :return: engine execution details
        :rtype: EngineExecutionOutputV2
        """
        response = super().GetExecution(project_id, execution_id)
        return EngineExecutionOutputV2.from_dict(response.Body)

    def list_executions(self, project_id, from_:datetime.datetime=None, to:datetime.datetime=None) -> List[EngineExecutionSummaryOutputV2]:
        """
        List engine executions
        
        :param project_id: ID of the project to list executions from
        :param from_: Executions started after this time
        :param to_: Executions started before this time
        :return: list of engine execution details
        :rtype: List[EngineExecutionSummaryOutputV2]
        """
        from_, to = sanitize_from_to(from_, to)
        data = []
        cursor = None
        response = super().GetExecutions(project_id, starttime=from_, endtime=to, cursor=cursor)
        cursor = response.Body["cursor"]
        data += self._page_to_list(EngineExecutionSummaryOutputV2, response)
        while cursor:
            response = super().GetExecutions(project_id, starttime=from_, endtime=to, cursor=cursor)
            data += self._page_to_list(EngineExecutionSummaryOutputV2, response)
            cursor = response.Body["cursor"]
        return data

    def cancel_execution(self, project_id, execution_id) -> bool:
        """
        Cancel engine execution
        
        :param project_id: ID of the project cancel execution in
        :param execution_id: ID of the execution
        :return: true if the cancellation request succeeded, otherwise false.
        :rtype: bool
        """
        response = super().CancelExecution(project_id, execution_id)
        return response.IsOk

    def delete_execution(self, project_id, execution_id) -> bool:
        """
        Delete engine execution
        
        :param project_id: ID of the project to delete execution in
        :param execution_id: ID of the execution
        :return: true if the deletion request succeeded, otherwise false.
        :rtype: bool
        """
        response = super().DeleteExecution(project_id, execution_id)
        return response.IsOk

    def list_configurations(self) -> List[GetConfigurationOutputV2]:
        """
        List configuration, i.e. information on available machine types

        :return: List[GetConfigurationOutputV2]
        :rtype: List of available configurations
        """
        response = super().GetAllConfigurations()
        return self._page_to_list(GetConfigurationOutputV2, response)

    def list_engines(self) -> List[EngineGetOutputV2]:
        """
        List available engines

        :return: List[EngineGetOutputV2]
        :rtype: List of available engines
        """
        response = super().GetAllEngines()
        return self._page_to_list(EngineGetOutputV2, response)
        
    def get_execution_diagnostics(self, project_id, execution_id) -> EngineExecutionDiagnosticsOutputV2:
        """
        Delete engine execution
        
        :param project_id: ID of the project to delete execution in
        :param execution_id: ID of the execution
        :return: true if the deletion request succeeded, otherwise false.
        :rtype: bool
        """
        response = super().GetExecutionDiagnostics(project_id, execution_id)
        return EngineExecutionDiagnosticsOutputV2.from_dict(response.Body)

    def get_execution_inputs(self, project_id, execution_id) -> EngineExecutionInputOutputV2:
        """
        Get execution inputs
        
        :param project_id: ID of the project containing the execution
        :param execution_id: ID of the execution
        :return: Information about what data were used as input for a specific execution
        :rtype: EngineExecutionInputOutputV2
        """
        response = super().GetExecutionInputs(project_id, execution_id)
        return EngineExecutionInputOutputV2.from_dict(response.Body)

    
    def run_execution(self, project_id, input:EngineExecutionParametersV2, engine_message_handler:EngineSubscription) -> EngineRunOutputV2:
        """
        Run a new execution
        
        :param project_id: ID of the project for the project context
        :param input: input for the execution
        :return: Details about the executed execution
        :rtype: EngineRunOutputV2
        """
        response = super().RunExecution(project_id, input.to_dict())
        engine_run_output = EngineRunOutputV2.from_dict(response.Body)
        execution_id = engine_run_output.executionId
        if engine_message_handler:
            engine_message_handler.set_resource_id(execution_id)
        return engine_run_output
        
    
    def run_execution_with_platform_data(self, project_id, input:EngineExecutionInputParametersV2, engine_message_handler:EngineSubscription) -> EngineRunOutputV2:
        """
        Run a new execution with inputs stored in MIKE Cloud Platform
        
        :param project_id: ID of the project for the project context
        :param input: input for the execution
        :return: Details about the executed execution
        :rtype: EngineRunOutputV2
        """

        response = super().RunExecutionWithPlatformData(project_id, input.to_dict())
        engine_run_output = EngineRunOutputV2.from_dict(response.Body)
        execution_id = engine_run_output.executionId
        if engine_message_handler:
            engine_message_handler.set_resource_id(execution_id)
        return engine_run_output
    



if __name__ == '__main__':
    print(__file__)
    print(dir())
