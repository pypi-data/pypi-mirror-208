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

# Usage of this function is discouraged. Clients shouldn't care which
# implementation of the API is in use. Note that there is no guarantee
# that differences between APIs will be maintained.
# Please don't use this function if possible.


from enum import Enum


class SectionTag(Enum):
  SPATIAL = 10
  TEMPORAL = 20
  ITEM = 30
  LAYER = 40
  DATABLOCK = 99
  CLOSETAG = 255


class SpatialTags(Enum):
  GRID_INDEXES = 10
  MESH_ELEMENTS = 20
  MESH_PAGES = 30


class DataBlockIndex(Enum):
  ITEM = 10
  SPATIAL = 20
  TEMPORAL = 30
  LAYER = 40

  @classmethod
  def from_value(cls, v):
    return {
      10: DataBlockIndex.ITEM,
      20: DataBlockIndex.SPATIAL,
      30: DataBlockIndex.TEMPORAL,
      40: DataBlockIndex.LAYER,
    }[v]