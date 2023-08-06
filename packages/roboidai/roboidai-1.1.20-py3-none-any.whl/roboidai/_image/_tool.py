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

import cv2 #line:19
import os #line:20
import sys #line:21
from urllib import request #line:22
from datetime import datetime #line:23
class ImageTool :#line:26
    @staticmethod #line:27
    def to_square (O000OO0O0O0O0OOO0 ,clone =False ):#line:28
        if O000OO0O0O0O0OOO0 is not None :#line:29
            if clone :#line:30
                O000OO0O0O0O0OOO0 =O000OO0O0O0O0OOO0 .copy ()#line:31
            O0OOO000OOO000000 =O000OO0O0O0O0OOO0 .shape [1 ]#line:32
            O0000OOO0OOO0OO0O =O000OO0O0O0O0OOO0 .shape [0 ]#line:33
            if O0000OOO0OOO0OO0O >O0OOO000OOO000000 :#line:34
                O0OOO0O0O0O0O0O0O =(O0000OOO0OOO0OO0O -O0OOO000OOO000000 )//2 #line:35
                O000OO0O0O0O0OOO0 =O000OO0O0O0O0OOO0 [O0OOO0O0O0O0O0O0O :O0OOO0O0O0O0O0O0O +O0OOO000OOO000000 ,:]#line:36
            else :#line:37
                O0OOO0O0O0O0O0O0O =(O0OOO000OOO000000 -O0000OOO0OOO0OO0O )//2 #line:38
                O000OO0O0O0O0OOO0 =O000OO0O0O0O0OOO0 [:,O0OOO0O0O0O0O0O0O :O0OOO0O0O0O0O0O0O +O0000OOO0OOO0OO0O ]#line:39
        return O000OO0O0O0O0OOO0 #line:40
    @staticmethod #line:42
    def resize (O00OOO0OO00000O0O ,OO00O00O0OOO0000O ,O000000OO0O0O00O0 ):#line:43
        if O00OOO0OO00000O0O is not None :#line:44
            O00OOO0OO00000O0O =cv2 .resize (O00OOO0OO00000O0O ,dsize =(OO00O00O0OOO0000O ,O000000OO0O0O00O0 ))#line:45
        return O00OOO0OO00000O0O #line:46
    @staticmethod #line:48
    def save (O00O0O0000OOOO0OO ,O0O000000000O0000 ,filename =None ):#line:49
        if O00O0O0000OOOO0OO is not None and O0O000000000O0000 is not None :#line:50
            if not os .path .isdir (O0O000000000O0000 ):#line:51
                os .makedirs (O0O000000000O0000 )#line:52
            if filename is None :#line:53
                filename =datetime .now ().strftime ("%Y%m%d_%H%M%S_%f")+'.png'#line:54
            if cv2 .imwrite (os .path .join (O0O000000000O0000 ,filename ),O00O0O0000OOOO0OO ):#line:55
                return True #line:56
            try :#line:57
                O0O00OOOO0OO00O00 =os .path .splitext (filename )[1 ]#line:58
                O0OO0O0O00O00O0OO ,OO0OOO0000OOO000O =cv2 .imencode (O0O00OOOO0OO00O00 ,O00O0O0000OOOO0OO )#line:59
                if O0OO0O0O00O00O0OO :#line:60
                    with open (os .path .join (O0O000000000O0000 ,filename ),mode ='w+b')as O0OOOO00000O00O0O :#line:61
                        OO0OOO0000OOO000O .tofile (O0OOOO00000O00O0O )#line:62
                    return True #line:63
                else :#line:64
                    return False #line:65
            except :#line:66
                return False #line:67
        return False #line:68
class DownloadTool :#line:71
    @staticmethod #line:72
    def _print_perc (OO0O0000O00000OOO ,OOO00OO00OO000000 ,OOOOO00O0OOOOOO0O ):#line:73
        if OO0O0000O00000OOO >OOO00OO00OO000000 :OO0O0000O00000OOO =OOO00OO00OO000000 #line:74
        OO00OO00OOO0000O0 =OO0O0000O00000OOO /OOO00OO00OO000000 #line:75
        OO0000OOO00OOO0O0 =round (OO00OO00OOO0000O0 *OOOOO00O0OOOOOO0O )#line:76
        if OOO00OO00OO000000 >(1024 **2 ):#line:77
            OO00OOOO0O0O00OOO =str (round (OOO00OO00OO000000 /1024 /1024 ,2 ))+'MB'#line:78
        elif OOO00OO00OO000000 >1024 :#line:79
            OO00OOOO0O0O00OOO =str (round (OOO00OO00OO000000 /1024 ,2 ))+'KB'#line:80
        else :#line:81
            OO00OOOO0O0O00OOO =str (OOO00OO00OO000000 )+'B'#line:82
        print ('\r',DownloadTool ._download_title ,OO00OOOO0O0O00OOO ,'#'*OO0000OOO00OOO0O0 +'-'*(OOOOO00O0OOOOOO0O -OO0000OOO00OOO0O0 ),'[{:>7.2%}]'.format (OO00OO00OOO0000O0 ),end ='')#line:83
        sys .stdout .flush ()#line:84
    @staticmethod #line:86
    def _download_callback (OO00O00O0O000OOOO ,O0000O0OO0O0OO0OO ,OO00O0000OO00000O ):#line:87
        DownloadTool ._print_perc (OO00O00O0O000OOOO *O0000O0OO0O0OO0OO ,OO00O0000OO00000O ,20 )#line:88
    @staticmethod #line:90
    def download_model (O0O00O000O00000O0 ,O0OOO000O0O0O00O0 ,overwrite =False ):#line:91
        OOO00O00OOO0O000O =os .path .join (O0O00O000O00000O0 ,O0OOO000O0O0O00O0 )#line:92
        if overwrite or not os .path .exists (OOO00O00OOO0O000O ):#line:93
            DownloadTool ._download_title =O0OOO000O0O0O00O0 +':'#line:94
            request .urlretrieve ('http://www.smartrobotmarket.com/hamster/tutorial/class/model/'+O0OOO000O0O0O00O0 ,OOO00O00OOO0O000O ,DownloadTool ._download_callback )#line:95
            print ()#line:96
        else :#line:97
            print (O0OOO000O0O0O00O0 ,'already exists.')#line:98
