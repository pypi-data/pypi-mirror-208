# Part of the ROBOID project - http://hamster.school
# Copyright (C) 2016 Kwang-Hyun Park (akaii@kw.ac.kr)
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General
# Public License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA  02111-1307  USA

from roboidai ._image ._object_detector import ObjectDetector #line:19
_O000000O0O0O0O0OO =None #line:21
def wait_until_fruit (O00OO0OO00OO0O0OO ,O0OOO0OO000000OO0 ,interval_msec =1 ,lang ='en'):#line:24
    global _O000000O0O0O0O0OO #line:25
    if _O000000O0O0O0O0OO is None :#line:27
        _O000000O0O0O0O0OO =ObjectDetector (True ,lang )#line:28
        _O000000O0O0O0O0OO .download_model ()#line:29
        _O000000O0O0O0O0OO .load_model ()#line:30
    if not isinstance (O0OOO0OO000000OO0 ,(list ,tuple )):#line:31
        O0OOO0OO000000OO0 =(O0OOO0OO000000OO0 ,)#line:32
    OOOOO0OOO00OO000O =None #line:34
    while OOOOO0OOO00OO000O is None :#line:35
        O00OO0O00O00OO0OO =O00OO0OO00OO0O0OO .read ()#line:36
        if _O000000O0O0O0O0OO .detect (O00OO0O00O00OO0OO ):#line:37
            O00OO0O00O00OO0OO =_O000000O0O0O0O0OO .draw_result (O00OO0O00O00OO0OO )#line:38
            for OO0O0OOO00OOO00O0 in O0OOO0OO000000OO0 :#line:39
                if OO0O0OOO00OOO00O0 in _O000000O0O0O0O0OO .get_label ():#line:40
                    OOOOO0OOO00OO000O =OO0O0OOO00OOO00O0 #line:41
                    break #line:42
        O00OO0OO00OO0O0OO .show (O00OO0O00O00OO0OO )#line:43
        if O00OO0OO00OO0O0OO .check_key (interval_msec )=='esc':break #line:44
    O00OO0OO00OO0O0OO .hide ()#line:45
    return OOOOO0OOO00OO000O #line:46
