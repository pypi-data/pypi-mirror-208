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
from datetime import datetime, timedelta
from . import decoder

class DateListDecoder:

    _TickToSecondsOver10Ratio = 1000000
    
    def _from_ticks(self, timestamp) -> datetime:
        return datetime(1, 1, 1) + timedelta(microseconds=(timestamp * self._TickToSecondsOver10Ratio))
    
    def read_dates(self, body, pos):
        times = []
        stamp, pos = decoder._DecodeVarint(body, pos)
        times.append(self._from_ticks(stamp))
        delta, pos = decoder._DecodeVarint32(body, pos)
        while delta > 0:
            count, pos = decoder._DecodeVarint32(body, pos)
            for i in range(count):
                stamp = stamp + delta
                times.append(self._from_ticks(stamp))
            delta, pos = decoder._DecodeVarint32(body, pos)
        
        return times, pos
 