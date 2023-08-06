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

from roboid import Runner #line:19
import cv2 #line:20
_O00OO00O00O0O0O00 ={8 :'bs',9 :'tab',13 :'enter',27 :'esc'}#line:28
_OO0O0O0000OOO00OO ={'bs':8 ,'tab':9 ,'enter':13 ,'esc':27 }#line:34
class Window :#line:37
    @staticmethod #line:38
    def check_key (timeout_msec =1 ):#line:39
        OOOOO0O0OO00000OO =cv2 .waitKey (timeout_msec )#line:40
        if OOOOO0O0OO00000OO >=32 and OOOOO0O0OO00000OO <=126 :return chr (OOOOO0O0OO00000OO )#line:41
        elif OOOOO0O0OO00000OO in _O00OO00O00O0O0O00 :return _O00OO00O00O0O0O00 [OOOOO0O0OO00000OO ]#line:42
        return None #line:43
    @staticmethod #line:45
    def wait_until_key (key =None ):#line:46
        if isinstance (key ,str ):#line:47
            O000O000OO0OO00O0 =key .lower ()#line:48
            if O000O000OO0OO00O0 in _OO0O0O0000OOO00OO :#line:49
                key =_OO0O0O0000OOO00OO [O000O000OO0OO00O0 ]#line:50
            elif len (key )==1 :#line:51
                key =ord (key [0 ])#line:52
        while True :#line:53
            if key is None :#line:54
                if cv2 .waitKey (10 )!=-1 :#line:55
                    break #line:56
            elif cv2 .waitKey (10 )==key :#line:57
                break #line:58
    def __init__ (O00000O000OOOO0OO ,id =0 ):#line:60
        O00000O000OOOO0OO ._title ='window {}'.format (id )#line:61
        Runner .register_component (O00000O000OOOO0OO )#line:62
    def dispose (OO0O00O0O000O0000 ):#line:64
        cv2 .destroyWindow (OO0O00O0O000O0000 ._title )#line:65
        Runner .unregister_component (OO0O00O0O000O0000 )#line:66
    def show (OO00OO0O0000000OO ,OOOO000OO000O0O0O ):#line:68
        if OOOO000OO000O0O0O is not None and OOOO000OO000O0O0O .shape [0 ]>0 and OOOO000OO000O0O0O .shape [1 ]>0 :#line:69
            cv2 .imshow (OO00OO0O0000000OO ._title ,OOOO000OO000O0O0O )#line:70
    def hide (OOOOO0O00O0O0O000 ):#line:72
        cv2 .destroyWindow (OOOOO0O00O0O0O000 ._title )#line:73
