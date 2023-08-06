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

from pynput .keyboard import Listener ,Key #line:19
def _OO00OOO0O00O00OO0 (OO0O0O0O00000O000 ):#line:22
    if hasattr (OO0O0O0O00000O000 ,'char'):KeyEvent ._pressed_key =OO0O0O0O00000O000 .char #line:23
    else :KeyEvent ._pressed_key =OO0O0O0O00000O000 #line:24
def _OOO0O00OO0OO00O00 (OOOO0O0OO0O0O0O00 ):#line:26
    if hasattr (OOOO0O0OO0O0O0O00 ,'char'):KeyEvent ._released_key =OOOO0O0OO0O0O0O00 .char #line:27
    else :KeyEvent ._released_key =OOOO0O0OO0O0O0O00 #line:28
class KeyEvent :#line:31
    SPACE =Key .space #line:32
    ESC =Key .esc #line:33
    _listener =None #line:35
    _pressed_key =None #line:36
    _released_key =None #line:37
    @staticmethod #line:39
    def start ():#line:40
        KeyEvent .stop ()#line:41
        KeyEvent ._listener =Listener (on_press =_OO00OOO0O00O00OO0 ,on_release =_OOO0O00OO0OO00O00 )#line:42
        KeyEvent ._listener .start ()#line:43
    @staticmethod #line:45
    def stop ():#line:46
        OO0O0OOOO0O0O00OO =KeyEvent ._listener #line:47
        KeyEvent ._listener =None #line:48
        if OO0O0OOOO0O0O00OO is not None :#line:49
            OO0O0OOOO0O0O00OO .stop ()#line:50
    @staticmethod #line:52
    def get_pressed_key ():#line:53
        O0O00O0OOO0OOOO0O =KeyEvent ._pressed_key #line:54
        KeyEvent ._pressed_key =None #line:55
        return O0O00O0OOO0OOOO0O #line:56
    @staticmethod #line:58
    def get_released_key ():#line:59
        OOOOO00O00OOOO0O0 =KeyEvent ._released_key #line:60
        KeyEvent ._released_key =None #line:61
        return OOOOO00O00OOOO0O0 #line:62
