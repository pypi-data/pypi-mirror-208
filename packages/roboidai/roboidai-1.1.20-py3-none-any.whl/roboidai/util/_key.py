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

from roboid import wait #line:19
from roboidai ._keyevent import KeyEvent #line:20
from pynput .keyboard import Key #line:21
_O0OOO000000OO0O00 ={'bs':Key .backspace ,'tab':Key .tab ,'enter':Key .enter ,'esc':Key .esc ,' ':Key .space }#line:30
def wait_until_key (key =None ):#line:33
    if isinstance (key ,str ):#line:34
        OO00OO00O00OO00OO =key .lower ()#line:35
        if OO00OO00O00OO00OO in _O0OOO000000OO0O00 :#line:36
            key =_O0OOO000000OO0O00 [OO00OO00O00OO00OO ]#line:37
    KeyEvent .start ()#line:38
    while True :#line:39
        if key is None :#line:40
            if KeyEvent .get_released_key ()is not None :#line:41
                break #line:42
        else :#line:43
            if KeyEvent .get_released_key ()==key :#line:44
                break #line:45
        wait (20 )#line:46
    KeyEvent .stop ()#line:47
