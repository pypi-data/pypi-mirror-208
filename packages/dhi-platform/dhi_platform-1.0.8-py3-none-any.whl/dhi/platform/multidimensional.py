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

from datetime import datetime
import struct
import array
from typing import List, Tuple

from dhi.platform.base.exceptions import MikeCloudException
from dhi.platform.commonmodels import ItemId, UnitId, SpatialFilter, TemporalFilter, VerticalFilter
from dhi.platform.protobufparser import decoder
from dhi.platform.protobufparser.decoderdatetime import DateListDecoder
from dhi.platform.protobufparser.enums import DataBlockIndex, SectionTag, SpatialTags
from .generated.multidimensionalgen import BinaryOptionsV2, BinaryQueryInputV2, ItemFilterV2, MultidimensionalGenClientV2, MultidimensionalGenClientV3, QueryInputV2, SpatialFilterV2, TemporalDomainOutputGetDatasetOutputV3, VerticalFilterV2

class BinaryOptions(BinaryOptionsV2):

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

    def get_spatial_rounding_ratio(self):
        if self.coordinatePrecision is None:
            raise MikeCloudException("Cannot get spatial rounding ratio when coordinate precision is None")
        return int(10**self.coordinatePrecision)

    @property
    def encodeCoordinates(self):
        return self.coordinatePrecision is not None
    

class BinaryDataBlock:
    
    def __init__(self, indexes:dict, data) -> None:
        self._indexes = indexes
        self._data = data

    @property
    def indexes(self):
        return self._indexes
    
    def get_data_raw(self):
        return self._data

    def get_data_byte(self):
        return struct.unpack(str(len(self._data)) + 'b', self._data)
    
    def get_data_short_int(self):
        return array.array('h', self._data)

    def get_data_int(self):
        return array.array('l', self._data)

    def get_data_float(self):
        return array.array('f', self._data)

    def get_data_double(self):
        return array.array('d', self._data)
    
    def __repr__(self) -> str:
        return str(self._indexes) + str(self._data[:min(5, len(self._data))]) + ('...' if len(self._data) > 6 else '')


class BinaryMeshPage:
    def __init__(self, nodes, elements, fixed_node_count) -> None:
        self._nodes = nodes
        self._elements = elements
        self._fixed_node_count = fixed_node_count
    
    @property
    def nodes(self) -> Tuple[tuple]:
        """Tuple of nodes in the mesh page"""
        return self._nodes
    
    @property
    def elements(self) -> Tuple[int]:
        """Tuple of elements in the mesh page"""
        return self._elements


class BinaryQueryOutput:

    def __init__(self) -> None:
        self._data_blocks = []
        self._mesh_reader = MeshBinaryReader()
        self._elements = []
        self._mesh_pages = []
        self._time_steps = []
        self._binary_protocol_version = None
        self._srid = None
    
    @property
    def mesh_pages(self) -> Tuple[BinaryMeshPage]:
        return self._mesh_pages

    @property
    def elements(self) -> Tuple[int]:
        return self._elements

    @property
    def srid(self) -> int:
        """Spatial reference id"""
        return self._srid

    @property
    def data_blocks(self) -> Tuple[BinaryDataBlock]:
        return self._data_blocks

    @property
    def binary_protocol_version(self) -> Tuple:
        return self._binary_protocol_version

    @property
    def time_steps(self) -> Tuple[datetime]:
        return self._time_steps

    def add_mesh_page(self, mesh_page):
        self._mesh_pages.append(mesh_page)

    def _parse_header(self, header) -> Tuple:
        return tuple([i for i in header])

    def _read_spatial_block(self, body, pos) -> int:
        tag, pos = decoder.ReadByte(body, pos)

        if tag == SpatialTags.GRID_INDEXES.value:
            output_elements, pos = decoder.ReadArrayInt(body, pos)
            self._elements = output_elements
        elif tag == SpatialTags.MESH_PAGES.value:
            count, pos = decoder._DecodeVarint32(body, pos)
            for i in range(count):
                mesh_page, pos = self._mesh_reader.ReadMeshPage(body, pos, self._binary_options)
                self.add_mesh_page(mesh_page)
        else:
            raise MikeCloudException(f"Invalid spatial tag {tag} while parsing spatial block.")
        
        return pos
    
    def _read_timesteps(self, body, pos) -> int:
        datetimedecoder = DateListDecoder()
        times, pos = datetimedecoder.read_dates(body, pos)
        self._time_steps = times
        return pos
    
    def _read_block_index(self, body, indexes:dict, pos) -> int:
        tag, pos = decoder.ReadByte(body, pos)
        val, pos = decoder._DecodeSignedVarint32(body, pos)
        indexes[DataBlockIndex.from_value(tag)] = val
        return pos

    def _read_data_block(self, body, pos) -> int:
        indexes = {}
        pos = self._read_block_index(body, indexes, pos)
        pos = self._read_block_index(body, indexes, pos)
        pos = self._read_block_index(body, indexes, pos)

        length, pos = decoder._DecodeVarint32(body, pos)
        data = body[pos:pos+length]
        pos = pos+length

        data_block = BinaryDataBlock(indexes, data)

        self._data_blocks.append(data_block)
        return pos
    
    def from_body(self, body, binary_options:BinaryOptions):
        self._binary_options = binary_options
        self._binary_protocol_version = self._parse_header(body[:4])
        
        srid, position = decoder._DecodeVarint32(body, 4)
        self._srid = srid
        
        tag, position = decoder.ReadByte(body, position)
        
        while (position < len(body)) and (tag != SectionTag.CLOSETAG):
            if tag == SectionTag.SPATIAL.value:
                position = self._read_spatial_block(body, position)
            elif tag == SectionTag.TEMPORAL.value:
                position = self._read_timesteps(body, position)
            elif tag == SectionTag.DATABLOCK.value:
                position = self._read_data_block(body, position)
            else:
                raise Exception(f"Unexpected section tag {tag} at {position}")
            
            tag, position = decoder.ReadByte(body, position)
        
        return self

class BinaryMeshElement:
    def __init__(self, id:int, nodes:Tuple[Tuple], ids:Tuple[int]) -> None:
        self._id = id
        self._nodes = nodes
        self._ids = ids

    @property
    def id(self):
        return self._id

    @property
    def nodes(self):
        return self._nodes

    @property
    def ids(self):
        return self._ids


class MeshBinaryReader:
    
    def __init__(self) -> None:
        pass

    def _read_mesh_nodes_encoded(self, body, pos, node_count, spatial_rounding_ratio):
        nodes = []
        x_encoded = decoder.DoubleDecoderWithPrecision(body, pos, spatial_rounding_ratio)
        pos = x_encoded.get_position()
        y_encoded = decoder.DoubleDecoderWithPrecision(body, pos, spatial_rounding_ratio)
        pos = y_encoded.get_position()
        nodes.append((x_encoded.start_value, y_encoded.start_value, 0.0))
        for i in range(node_count - 1):
            x = x_encoded.get_next_value(body, pos)
            pos = x_encoded.get_position()
            y = y_encoded.get_next_value(body, pos)
            pos = y_encoded.get_position()
            node = (x, y, 0.0)
            nodes.append(node)
        return nodes, pos

    def _read_mesh_nodes_as_doubles(self, body, pos, node_count):
        nodes = []
        for i in range(node_count):
            x, pos = decoder.DecodeDouble(body, pos)
            y, pos = decoder.DecodeDouble(body, pos)
            nodes.append((x, y, 0.0))
        return nodes, pos

    def _read_elements(self, nodes, include_mesh_element_id, fixed_node_count, body, pos):
        count, pos = decoder._DecodeVarint32(body, pos)

        elements = []
        id = 0
        for i in range(count):
            
            if include_mesh_element_id:
                delta, pos = decoder.DecodeSInt32(body, pos)
                id = delta if id == 0 else id + delta
            
            if fixed_node_count == 0:
                node_count, pos = decoder.ReadByte(body, pos)
            else:
                node_count = fixed_node_count
            
            ids = []
            for j in range(node_count):
                idj, pos = decoder.ReadByte(body, pos)
                ids.append(idj)
            
            el = BinaryMeshElement(id, nodes, ids)
            elements.append(el)

        return elements, pos

    def ReadMeshPage(self, body, pos, options:BinaryOptions):
        fixed_node_count, pos = decoder.ReadByte(body, pos)
        node_count, pos = decoder._DecodeSignedVarint32(body, pos)
        if options.encodeCoordinates:
            nodes, pos = self._read_mesh_nodes_encoded(body, pos, node_count, options.get_spatial_rounding_ratio())
        else:
            nodes, pos = self._read_mesh_nodes_as_doubles(body, pos, node_count)
        elements, pos = self._read_elements(nodes, options.includeMeshElementId, fixed_node_count, body, pos)
        return BinaryMeshPage(nodes, elements, fixed_node_count), pos


class TemporalDomainOutputGetDatasetOutput(TemporalDomainOutputGetDatasetOutputV3):
    pass


class BinaryQueryInput(BinaryQueryInputV2):
    pass


class MultidimensionalClientV2(MultidimensionalGenClientV2):
    def __init__(self, inspectFnc=MultidimensionalGenClientV2.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)


class MultidimensionalClientV3(MultidimensionalGenClientV3):
    def __init__(self, inspectFnc=MultidimensionalGenClientV3.DefaultInspectFnc, **kwargs):
        super().__init__(inspectFnc, **kwargs)


class MultidimensionalClient():
    
    def __init__(self, inspectFnc=MultidimensionalClientV3.DefaultInspectFnc, **kwargs):
        self._md2 = kwargs.get("MultidimensionalClientV2", MultidimensionalClientV2(inspectFnc, **kwargs))
        self._md3 = kwargs.get("MultidimensionalClientV3", MultidimensionalClientV3(inspectFnc, **kwargs))

    def get_dataset(self, project_id, dataset_id) -> TemporalDomainOutputGetDatasetOutput:
        """
        Get multidimensional dataset details
        
        :param project_id: ID of the project where the dataset is located
        :param dataset_id: ID of the dataset
        :return: multidimensional datset details
        :rtype: TemporalDomainOutputGetDatasetOutput
        """
        response = self._md3.GetDatasetV3(project_id, dataset_id)
        return TemporalDomainOutputGetDatasetOutput.from_dict(response.Body)

    def update_item(self, project_id, dataset_id, item_index:int, name:str, unit:UnitId, item:ItemId) -> TemporalDomainOutputGetDatasetOutput:
        """
        Update a spefific item in a multidimensional dataset
        
        :param project_id: ID of the project where the dataset is located
        :param dataset_id: ID of the dataset
        :param item_index: Index of the item to update
        :param name: Name of the item, you must include the original name if you don't want to update the item
        :param unit: ID of the unit, you must include the original unit if you don't want to update the unit
        :param item: ID of the item, you must include the original item if you don't want to update the item
        :return: multidimensional datset details
        :rtype: TemporalDomainOutputGetDatasetOutput
        """
        input = {
            "name": name,
            "unit": unit,
            "item": item
        }
        response = self._md3.UpdateItemDefinition(project_id, input, dataset_id, item_index)
        return TemporalDomainOutputGetDatasetOutput.from_dict(response.Body)

    def delete_timestep(self, project_id, dataset_id, timestep_index:int) -> bool:
        """
        Delete a timestep from a multidimensional dataset
        
        :param project_id: ID of the project where the dataset is located
        :param dataset_id: ID of the dataset
        :param timestep_index: Index of the timestep to delete
        :return: True if removal was successful, otherwise False
        :rtype: bool
        """
        response = self._md3.DeleteTimestep(project_id, dataset_id, timestepindex=timestep_index)
        return response.IsOk

    def query_timesteps(
        self,
        project_id, dataset_id, 
        spatial_filter:SpatialFilter,
        temporal_filter:TemporalFilter,
        vertical_filter:VerticalFilter=None,
        item_indices:Tuple[int]=(),
        options = BinaryOptions(
            majorVersion=1,
            minorVersion=1,
            coordinatePrecision=5,
            includeMeshElementId=True
        ), 
        include_geometries=True,
        include_values=True,
        output_srid=None
    ) -> BinaryQueryOutput:
        """
        Query multidimensional dataset for a set of time steps
        - POST ​/api​/md​/dataset​/{id}​/binary-query-timesteps

        :param project_id: ID of the project where the dataset resides in 
        :param dataset_id: ID of the dataset to query
        :param spatial_filter: Filter to limit the spatial extent of the query
        :param temporal_filter: Filter to limit the temporal extent of the query
        :param vertical_filter: Filter to limit vertical extent of the query, optional, default is None for full vertical extent
        :param item_indices: Indices of ites to include in the response, optional, default is empty tuple for all items
        :param options: Binary query options
        :param include_geometries: Should the response include element geometries? Optional, default is True
        :param include_values: Should the response include element values? Optional, default is True
        :param output_srid: For meshes, it is possible to specify output srid as the desired coordinate system id of the resulting geometries.
        """
        item_filter = None if not item_indices else ItemFilterV2(item_indices)

        query = QueryInputV2(
            itemFilter = item_filter,
            spatialFilter = spatial_filter,
            temporalFilter = temporal_filter,
            verticalFilter = vertical_filter,
            includeGeometries = include_geometries,
            includeValues = include_values,
            outputSRID = output_srid
        )

        input = BinaryQueryInput(
            query = query,
            options = options
        ).to_dict()

        response = self._md2.GetQueryTimestepResultAsBinaryStream(project_id, input, dataset_id)
        return BinaryQueryOutput().from_body(response.Body, options)
        

    def query_timeseries(self, 
        project_id, dataset_id, 
        spatial_filter:SpatialFilter,
        temporal_filter:TemporalFilter,
        vertical_filter:VerticalFilter=None,
        item_indices:Tuple[int]=(),
        options = BinaryOptions(
            majorVersion=1,
            minorVersion=1,
            coordinatePrecision=5,
            includeMeshElementId=True
        ), 
        include_geometries=True,
        include_values=True,
        output_srid=None
    ) -> BinaryQueryOutput:
        """
        Query multidimensional dataset for a set of time series
        - POST ​/api​/md​/dataset​/{id}​/binary-query-timeseries

        :param project_id: ID of the project where the dataset resides in 
        :param dataset_id: ID of the dataset to query
        :param spatial_filter: Filter to limit the spatial extent of the query
        :param temporal_filter: Filter to limit the temporal extent of the query
        :param vertical_filter: Filter to limit vertical extent of the query, optional, default is None for full vertical extent
        :param item_indices: Indices of ites to include in the response, optional, default is empty tuple for all items
        :param options: Binary query options
        :param include_geometries: Should the response include element geometries? Optional, default is True
        :param include_values: Should the response include element values? Optional, default is True
        :param output_srid: For meshes, it is possible to specify output srid as the desired coordinate system id of the resulting geometries.
        """
        item_filter = None if not item_indices else ItemFilterV2(item_indices)

        query = QueryInputV2(
            itemFilter = item_filter,
            spatialFilter = spatial_filter,
            temporalFilter = temporal_filter,
            verticalFilter = vertical_filter,
            includeGeometries = include_geometries,
            includeValues = include_values,
            outputSRID = output_srid
        )

        input = BinaryQueryInput(
            query = query,
            options = options
        ).to_dict()

        response = self._md2.GetQueryTimeseriesResultAsBinaryStream(project_id, input, dataset_id)
        return BinaryQueryOutput().from_body(response.Body, options)


if __name__ == '__main__':
    print(__file__)
    print(dir())
