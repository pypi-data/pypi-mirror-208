import time
from typing import Tuple
import unittest
import datetime
import pandas as pd
import uuid
import random

from .testcredentials import TEST_IDENTITY
from dhi.platform import metadata, transfer, timeseries
from dhi.platform.authentication import ApiKeyIdentity
from dhi.platform.base.exceptions import MikeCloudRestApiException
from dhi.platform.commonmodels import AttributeDataType, AttributeOperator, ItemDefinition, PropertyDataType, PropertyDefinition, QueryCondition, TimeSeriesDataType
import os

class TestTransferTest(unittest.TestCase):

    _verbosity = 0
    _project_id = None
    _identity = None
    _test_data_dir = None
    
    def setUp(self) -> None:
        if not self._identity:
            self._identity = TEST_IDENTITY
        
        self._tsclient = timeseries.TimeSeriesClient(
            verbose=self._verbosity, 
            identity=self._identity
        )

        self._metadataclient = metadata.MetadataClient(verbose=self._verbosity, identity=TEST_IDENTITY)

        self._test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self._stamp = stamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        if not self._project_id:
            name = 'Python test ' + self._stamp
            projectInput = metadata.CreateProjectInput(name, 'Project created by Python SDK test')
            project = self._metadataclient.create_project(projectInput)
            self._project_id = project.id

    def tearDown(self) -> None:
        super().tearDown()
        if self._project_id:
            self._metadataclient.delete_project(self._project_id, permanently=True)
        

    def _assert_item_definition(self, expected:ItemDefinition, actual:ItemDefinition):
        self.assertIsNotNone(actual)
        self.assertEqual(expected.name, actual.name)
        self.assertEqual(expected.data_type, actual.data_type)
        self.assertEqual(expected.item, actual.item)
        self.assertEqual(expected.unit, actual.unit)
        self.assertEqual(expected.timeseries_data_type, actual.timeseries_data_type)

    def _assert_equal_ts_properties(self, expected:Tuple[PropertyDefinition], actual:Tuple[PropertyDefinition]):
        expected = [p.body() for p in expected]
        actual = [p.body() for p in actual]
        self.assertEqual(expected, actual)
    
    def _assert_equal_ts_datafields(self, expected:Tuple[timeseries.DataFieldDefinition], actual:Tuple[timeseries.DataFieldDefinition]):
        expected = [f.body() for f in expected]
        actual = [f.body() for f in actual]
        self.assertEqual(expected, actual)

    def _assert_time_equal_to_seconds(self, a:datetime.datetime, b:datetime.datetime):
        are_equal = a.date() == b.date() and a.hour == b.hour and a.minute == b.minute and a.second == b.second
        self.assertTrue(are_equal)
    
    def test_create_timeseries_dataset_with_properties_is_ok(self):
        
        ts_schema = (PropertyDefinition("propertydefinitionname", PropertyDataType.TEXT),)
        name = f"Py TS {self._stamp}"
        description = "TimeSeries dataset created from Python"
        metadata = {"metadatakey1": "metadataentry1"}
        properties = {"propertykey1": "propertyentry1"}
        
        input = timeseries.TimeSeriesDatasetInput(
            name,
            description,
            ts_schema,
            metadata,
            properties
        )

        ts_dataset = self._tsclient.create_timeseries_dataset(self._project_id, input)
        self.assertIsNotNone(ts_dataset)
        self.assertTrue(ts_dataset.id)
        self._assert_equal_ts_properties(ts_dataset.timeseries_properties, ts_schema)
        self.assertEqual(ts_dataset.metadata, metadata)
        self.assertIsNotNone(ts_dataset.items)
        self.assertFalse(ts_dataset.items)

        tsd = self._tsclient.get_timeseries_dataset(self._project_id, ts_dataset.id)
        self.assertIsNotNone(tsd)
        self.assertEqual(tsd.id, ts_dataset.id)
        self._assert_equal_ts_properties(tsd.timeseries_properties, ts_schema)
        self.assertEqual(tsd.metadata, metadata)
        self.assertIsNotNone(tsd.items)
        self.assertFalse(tsd.items)
    
    def test_create_timeseries_dataset_with_properties_from_schema_is_ok(self):
        
        ts_schema = (PropertyDefinition("propertydefinitionname", PropertyDataType.TEXT),)
        name = f"Py TS {self._stamp}"
        description = "TimeSeries dataset created from Python"

        ts_dataset = self._tsclient.create_timeseries_dataset_from_schema(self._project_id, name, description, ts_schema)
        self.assertIsNotNone(ts_dataset)
        self.assertTrue(ts_dataset.id)
        self._assert_equal_ts_properties(ts_dataset.timeseries_properties, ts_schema)
        self.assertEqual(ts_dataset.metadata, {})
        self.assertIsNotNone(ts_dataset.items)
        self.assertFalse(ts_dataset.items)

        tsd = self._tsclient.get_timeseries_dataset(self._project_id, ts_dataset.id)
        self.assertIsNotNone(tsd)
        self.assertEqual(tsd.id, ts_dataset.id)
        self._assert_equal_ts_properties(tsd.timeseries_properties, ts_schema)
        self.assertEqual(tsd.metadata, {})
        self.assertIsNotNone(tsd.items)
        self.assertFalse(tsd.items)

    def test_create_dataset_with_data_is_ok(self):
        ts_dataset = self._tsclient.create_timeseries_dataset_from_schema(self._project_id, "Py TS with data")
        
        self.assertIsNotNone(ts_dataset)
        self.assertTrue(ts_dataset.id)

        time.sleep(2) # let events propagate in local development

        tds = self._tsclient.get_timeseries_dataset(self._project_id, ts_dataset.id)

        self.assertIsNotNone(tds)
        self.assertEqual(ts_dataset.id, tds.id)

        item = ItemDefinition(
            "Temperature", 
            metadata.UnitId.EUMUDEGREECELSIUS,
            metadata.ItemId.EUMITEMPERATURE,
            AttributeDataType.SINGLE,
            TimeSeriesDataType.MEAN_STEP_BACKWARD
        )

        ts = self._tsclient.add_timeseries(self._project_id, tds.id, item)

        self.assertIsNotNone(ts)
        self.assertTrue(ts.id)
        self._assert_item_definition(item, ts.item)

        ts2 = self._tsclient.get_timeseries(self._project_id, tds.id, ts.id)
        
        self.assertIsNotNone(ts2)
        self.assertEqual(ts2.id, ts.id)
        self._assert_item_definition(ts.item, ts2.item)

        today = datetime.datetime.today()
        # add time series values
        data = pd.DataFrame([float(12.34)], index=[today])
        success = self._tsclient.add_timeseries_values(self._project_id, tds.id, ts.id, data)
        self.assertTrue(success)

        # get time series values
        tsv = self._tsclient.get_timeseries_values(self._project_id, tds.id, ts.id)

        self.assertIsNotNone(tsv)
        self.assertEqual(data.shape, tsv.shape)
        self._assert_time_equal_to_seconds(data.index[0], tsv.index[0])
        self.assertEqual(data[0][0], tsv["values"][0])

        # add more time series values
        data2 = pd.DataFrame([float(13.45)], index=[today - datetime.timedelta(hours=-1)])
        success = self._tsclient.add_timeseries_values(self._project_id, tds.id, ts.id, data2)

        self.assertTrue(success)

        # get timeseries values again
        tsv2 = self._tsclient.get_timeseries_values(self._project_id, tds.id, ts.id)

        self.assertIsNotNone(tsv2)
        self.assertEqual((2, 1), tsv2.shape)
        self._assert_time_equal_to_seconds(data.index[0], tsv2.index[0])
        self.assertEqual(data[0][0], tsv2["values"][0])
        self.assertEqual(data2[0][0], tsv2["values"][1])

        # list time series
        time_series_list = [*self._tsclient.list_timeseries(self._project_id, tds.id)]

        self.assertEqual(len(time_series_list), 1)
        self.assertTrue(time_series_list[0].id, ts.id)

    def test_query_time_series_is_ok(self):
        tds = self._tsclient.create_timeseries_dataset_from_schema(self._project_id, "Py Query TS")
        self.assertIsNotNone(tds)
        self.assertTrue(tds.id)

        # add time series
        item1 = ItemDefinition(
            "Temperature",
            metadata.UnitId.EUMUDEGREECELSIUS,
            metadata.ItemId.EUMITEMPERATURE,
            data_type=AttributeDataType.SINGLE
        )

        ts1 = self._tsclient.add_timeseries(self._project_id, tds.id, item1)

        self.assertIsNotNone(item1)
        self._assert_item_definition(item1, ts1.item)

        # add timeseries values
        data1 = pd.DataFrame([float(12.34)], index=[datetime.datetime.utcnow()])
        self._tsclient.add_timeseries_values(self._project_id, tds.id, ts1.id, data1)
        data2 = pd.DataFrame([float(16.8)], index=[datetime.datetime.utcnow() + datetime.timedelta(minutes=1)])
        self._tsclient.add_timeseries_values(self._project_id, tds.id, ts1.id, data2)

        # add time series
        item2 = ItemDefinition(
            "Rainfall",
            metadata.UnitId.EUMUPERMILLILITER,
            metadata.ItemId.EUMIRAINFALL,
            data_type=AttributeDataType.SINGLE
        )

        ts2 = self._tsclient.add_timeseries(self._project_id, tds.id, item2)

        self.assertIsNotNone(ts2)
        self._assert_item_definition(item2, ts2.item)

        # add timeseries values
        data1 = pd.DataFrame([float(6.9)], index=[datetime.datetime.utcnow()])
        self._tsclient.add_timeseries_values(self._project_id, tds.id, ts1.id, data1)
        data2 = pd.DataFrame([float(7.6)], index=[datetime.datetime.utcnow() + datetime.timedelta(minutes=1)])
        self._tsclient.add_timeseries_values(self._project_id, tds.id, ts1.id, data2)

        # query rainfall
        conditions1 = (
            QueryCondition.create_attribute_query_condition("Item", AttributeOperator.EQUAL, "Rainfall"),
        )
        result1 = [*self._tsclient.query_timeseries(self._project_id, tds.id, conditions1)]

        self.assertIsNotNone(result1)
        self.assertTrue(result1[0].id)
        self._assert_item_definition(item2, result1[0].item)
    
        # query temperature
        conditions2 = [
            QueryCondition.create_attribute_query_condition("Item", AttributeOperator.EQUAL, "Temperature")
        ]
        result2 = [*self._tsclient.query_timeseries(self._project_id, tds.id, conditions2)]
        
        self.assertIsNotNone(result2)
        self.assertTrue(result2[0].id)
        self._assert_item_definition(item1, result2[0].item)

        # query airpressure
        conditions3 = [
            QueryCondition.create_attribute_query_condition("Item", AttributeOperator.EQUAL, "AirPressure")
        ]
        result3 = [*self._tsclient.query_timeseries(self._project_id, tds.id, conditions3)]
        
        self.assertIsNotNone(result3)
        self.assertFalse(result3)

        ids = (result1[0].id, result2[0].id)
        values = [*self._tsclient.get_multiple_timeseries_values(self._project_id, tds.id, ids)]
        
        self.assertEqual(2, len(values))


    def test_add_remove_timeseries_and_timeseries_values_is_ok(self):
        
        dataset = self._tsclient.create_timeseries_dataset(self._project_id, timeseries.TimeSeriesDatasetInput("Py TS with data"))
        
        self.assertIsNotNone(dataset)
        self.assertTrue(dataset.id)

        timeseries_id = f"testTS-{uuid.uuid4()}"

        item = ItemDefinition(
            "Temperature",
            metadata.UnitId.EUMUDEGREECELSIUS,
            metadata.ItemId.EUMITEMPERATURE,
            AttributeDataType.SINGLE
        )

        ts = self._tsclient.add_timeseries_with_id(self._project_id, dataset.id, timeseries_id, item)
        
        self.assertIsNotNone(ts)
        self._assert_item_definition(item, ts.item)

        ts_result = self._tsclient.get_timeseries(self._project_id, dataset.id, ts.id)

        self.assertIsNotNone(ts_result)
        self.assertEqual(ts.id, ts_result.id)
        self._assert_item_definition(ts.item, ts_result.item)

        data = pd.DataFrame([float(12.34)], index=[datetime.datetime.utcnow()])
        self._tsclient.add_timeseries_values(self._project_id, dataset.id, ts.id, data)

        tsv_result = self._tsclient.get_timeseries_values(self._project_id, dataset.id, ts.id)

        self.assertIsNotNone(tsv_result)
        self.assertEqual(data[0][0], tsv_result["values"][0])

        deleted = self._tsclient.delete_timeseries_values(self._project_id, dataset.id, ts.id)

        self.assertTrue(deleted)

        tsv_result2 = self._tsclient.get_timeseries_values(self._project_id, dataset.id, ts.id)
        self.assertIsNotNone(tsv_result2)
        self.assertTrue(tsv_result2.empty)

        deleted_timeseries = self._tsclient.delete_timeseries(self._project_id, dataset.id, ts.id)
        self.assertTrue(deleted_timeseries)

        with self.assertRaises(MikeCloudRestApiException) as context:
            self._tsclient.get_timeseries(self._project_id, dataset.id, ts.id)

    def test_update_timeseries_properties_is_ok(self):
        prop_definition_name = "property1key"
        prop_definition_name2 = "property2key"

        input = timeseries.TimeSeriesDatasetInput(
            name="Py Test TS update properties",
            timeseries_schema = (
                PropertyDefinition(prop_definition_name, PropertyDataType.TEXT),
                PropertyDefinition(prop_definition_name2, PropertyDataType.BOOLEAN)
            )
        )

        dataset = self._tsclient.create_timeseries_dataset(self._project_id, input)

        self.assertIsNotNone(dataset)
        self.assertTrue(dataset.id)

        # add timeseries with properties
        item1 = ItemDefinition(
            "Temperature", 
            metadata.UnitId.EUMUDEGREECELSIUS, 
            metadata.ItemId.EUMITEMPERATURE, 
            AttributeDataType.SINGLE
        )

        properties1 = { prop_definition_name: "property1value"}

        data_fields1 = (
            timeseries.DataFieldDefinition("datafieldname", timeseries.DataFieldDataType.FLAG, flags=(
                timeseries.FlagDefinition(1,"flagdefinitionname", 1947, "flagdefinitiondescription"),
            )),
        )

        ts1 = self._tsclient.add_timeseries(self._project_id, dataset.id, item1, properties1, data_fields1)

        self.assertIsNotNone(ts1)
        self._assert_item_definition(item1, ts1.item)
        self.assertEqual(properties1, ts1.properties)
        self._assert_equal_ts_datafields(data_fields1, ts1.data_fields)

        ts_result = self._tsclient.get_timeseries(self._project_id, dataset.id, ts1.id)
        self.assertIsNotNone(ts_result)
        self.assertEqual(ts1.id, ts_result.id)
        self._assert_item_definition(ts1.item, ts_result.item)
        self.assertEqual(properties1, ts_result.properties)
        self._assert_equal_ts_datafields(data_fields1, ts_result.data_fields)

        # update timeseries property value
        prop_input_value2 = "property1valueupdated"
        prop2_intput_value2 = True
        prop_input = { 
            prop_definition_name: prop_input_value2,
            prop_definition_name2: prop2_intput_value2
        }
        self._tsclient.update_timeseries_properties(self._project_id, dataset.id, ts1.id, prop_input)

        ts_result2 = self._tsclient.get_timeseries(self._project_id, dataset.id, ts1.id)

        self.assertIsNotNone(ts_result2)
        self.assertEqual(ts1.id, ts_result2.id)
        self._assert_item_definition(ts1.item, ts_result2.item)
        self.assertEqual(prop_input, ts_result2.properties)
        self._assert_equal_ts_datafields(data_fields1, ts_result2.data_fields)


    def test_update_timeseries_property_is_ok(self):
        prop_definition_name = "property1key"
        input = timeseries.TimeSeriesDatasetInput(
            name = "Py Test TS update property",
            timeseries_schema=[PropertyDefinition(prop_definition_name, PropertyDataType.TEXT)]
        )

        dataset = self._tsclient.create_timeseries_dataset(self._project_id, input)

        self.assertIsNotNone(dataset)
        self.assertTrue(dataset.id)

        item1 = ItemDefinition(
            "Temperature",
            metadata.UnitId.EUMUDEGREECELSIUS,
            metadata.ItemId.EUMITEMPERATURE,
            AttributeDataType.SINGLE
        )

        properties1 = { prop_definition_name: "property1value" }

        data_fields1 = (
            timeseries.DataFieldDefinition(
                "datafieldname",
                timeseries.DataFieldDataType.FLAG,
                flags=(timeseries.FlagDefinition(1, "flagdefinitionname", 1947, "flagdefinitiondescription"),)
                ),
        )

        ts1 = self._tsclient.add_timeseries(self._project_id, dataset.id, item1, properties1, data_fields1)

        self.assertIsNotNone(ts1)
        self.assertTrue(ts1.id)
        self._assert_item_definition(item1, ts1.item)
        self.assertEqual(properties1, ts1.properties)
        self._assert_equal_ts_datafields(data_fields1, ts1.data_fields)

        ts_result = self._tsclient.get_timeseries(self._project_id, dataset.id, ts1.id)
        self.assertIsNotNone(ts_result)
        self.assertEqual(ts1.id, ts_result.id)
        self._assert_item_definition(ts1.item, ts_result.item)
        self.assertEqual(properties1, ts_result.properties)
        self._assert_equal_ts_datafields(data_fields1, ts_result.data_fields)

        # update timeseries property value
        prop_input_value2 = "property1valueupdated"
        self._tsclient.update_timeseries_property(self._project_id, dataset.id, ts1.id, prop_definition_name, prop_input_value2)

        ts_result2 = self._tsclient.get_timeseries(self._project_id, dataset.id, ts1.id)
        self.assertIsNotNone(ts_result2)
        self.assertEqual(ts1.id, ts_result2.id)
        self._assert_item_definition(ts1.item, ts_result2.item)
        properties1.update({prop_definition_name: prop_input_value2})
        self.assertEqual(properties1, ts_result2.properties)
        self._assert_equal_ts_datafields(data_fields1, ts_result2.data_fields)

    def test_remove_timeseries_and_timeseries_values_with_interval_is_ok(self):
        dataset = self._tsclient.create_timeseries_dataset(self._project_id, timeseries.TimeSeriesDatasetInput("Py Test TS With Data"))

        time.sleep(2) # let events propagate in local development

        self.assertIsNotNone(dataset)
        self.assertTrue(dataset.id)

        item = ItemDefinition(
            "Temperature",
            metadata.UnitId.EUMUDEGREECELSIUS,
            metadata.ItemId.EUMITEMPERATURE,
            AttributeDataType.SINGLE
        )

        ts = self._tsclient.add_timeseries(self._project_id, dataset.id, item)
        
        self.assertIsNotNone(ts)
        self.assertTrue(ts.id)
        self._assert_item_definition(item, ts.item)

        start_time = datetime.datetime.utcnow()
        dates = []
        values = []
        for i in range(0, 230):
            dates.append(start_time + datetime.timedelta(minutes=i))
            values.append(random.uniform(0.0, 1000.0))
        data = pd.DataFrame(values, index=dates)

        self._tsclient.add_timeseries_values(self._project_id, dataset.id, ts.id, data)

        from_ = start_time + datetime.timedelta(minutes=15)
        to = start_time + datetime.timedelta(minutes=30)
        tsv_result = self._tsclient.get_timeseries_values(self._project_id, dataset.id, ts.id, from_, to)

        self.assertIsNotNone(tsv_result)
        self.assertEqual(tsv_result.shape, (16, 1))
        self.assertTrue(tsv_result["values"].values.tolist(), values)
        self.assertTrue(tsv_result.index.tolist(), dates)

        deleted = self._tsclient.delete_timeseries_values(self._project_id, dataset.id, ts.id, from_, to)

        self.assertTrue(deleted)

        tsv_result2 = self._tsclient.get_timeseries_values(self._project_id, dataset.id, ts.id, from_, to)
        self.assertIsNotNone(tsv_result2)
        self.assertTrue(tsv_result2.empty)


if __name__ == "__main__":
    unittest.main()