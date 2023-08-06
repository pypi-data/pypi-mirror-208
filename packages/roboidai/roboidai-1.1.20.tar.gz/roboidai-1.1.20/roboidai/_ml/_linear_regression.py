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

import numpy as np #line:19
import matplotlib .pyplot as plt #line:20
from sklearn .linear_model import LinearRegression as Regression #line:21
class LinearRegression :#line:24
    def __init__ (O000000OOOOO00OOO ):#line:25
        O000000OOOOO00OOO ._regression =Regression ()#line:26
        O000000OOOOO00OOO ._clear ()#line:27
    def _clear (OOO0OOO0O00O0O0OO ):#line:29
        OOO0OOO0O00O0O0OO ._labels =None #line:30
        OOO0OOO0O00O0O0OO ._data =None #line:31
        OOO0OOO0O00O0O0OO ._columns ={}#line:32
        OOO0OOO0O00O0O0OO ._clear_result ()#line:33
    def _clear_result (OO0OOO0000OO00OOO ):#line:35
        OO0OOO0000OO00OOO ._result ={'xlabels':None ,'ylabels':None ,'weights':{}}#line:40
    def _to_label (O000OO00OOOO0000O ,O0O0OOOO000O0OO00 ):#line:42
        if O000OO00OOOO0000O ._labels is not None :#line:43
            if isinstance (O0O0OOOO000O0OO00 ,(int ,float )):#line:44
                O0O0OOOO000O0OO00 =int (O0O0OOOO000O0OO00 )#line:45
                if O0O0OOOO000O0OO00 >=0 and O0O0OOOO000O0OO00 <len (O000OO00OOOO0000O ._labels ):#line:46
                    return O000OO00OOOO0000O ._labels [O0O0OOOO000O0OO00 ]#line:47
            elif isinstance (O0O0OOOO000O0OO00 ,str ):#line:48
                if O0O0OOOO000O0OO00 in O000OO00OOOO0000O ._labels :#line:49
                    return O0O0OOOO000O0OO00 #line:50
        return None #line:51
    def load_data (OO0O0O000OOO00000 ,O0OOO00O000OO0000 ):#line:53
        OO0O0O000OOO00000 ._clear ()#line:54
        OO0O0O000OOO00000 ._labels =np .loadtxt (O0OOO00O000OO0000 ,dtype ='str',delimiter =',',max_rows =1 )#line:55
        OO0O0O000OOO00000 ._data =np .loadtxt (O0OOO00O000OO0000 ,delimiter =',',skiprows =1 )#line:56
        for O00OOOOOOOOO0000O ,OOOOO000O000O0000 in enumerate (OO0O0O000OOO00000 ._labels ):#line:57
            OO0O0O000OOO00000 ._columns [OOOOO000O000O0000 ]=OO0O0O000OOO00000 ._data [:,O00OOOOOOOOO0000O ]#line:58
        return OO0O0O000OOO00000 ._data #line:59
    def get_label (O0O0O00O0O0O00O0O ,index ='all'):#line:61
        if O0O0O00O0O0O00O0O ._labels is not None :#line:62
            if isinstance (index ,(int ,float )):#line:63
                index =int (index )#line:64
                if index >=0 and index <len (O0O0O00O0O0O00O0O ._labels ):#line:65
                    return O0O0O00O0O0O00O0O ._labels [index ]#line:66
            elif isinstance (index ,str ):#line:67
                if index .lower ()=='all':#line:68
                    return O0O0O00O0O0O00O0O ._labels #line:69
        return None #line:70
    def _get_data (OO000000O0O00OOOO ,OO000000000OO0000 ):#line:72
        if OO000000000OO0000 is not None and OO000000000OO0000 in OO000000O0O00OOOO ._columns :#line:73
            return OO000000O0O00OOOO ._columns [OO000000000OO0000 ]#line:74
        return None #line:75
    def get_data (O0O0OOOOO0000O00O ,label ='all'):#line:77
        if isinstance (label ,str )and label .lower ()=='all':#line:78
            return O0O0OOOOO0000O00O ._data #line:79
        label =O0O0OOOOO0000O00O ._to_label (label )#line:80
        return O0O0OOOOO0000O00O ._get_data (label )#line:81
    def fit (OOO000OOOO0OO00O0 ,OO00O0OO000OOOO0O ,O0O0OO00O0000O00O ):#line:83
        OOO000OOOO0OO00O0 ._clear_result ()#line:84
        if not isinstance (OO00O0OO000OOOO0O ,(list ,tuple )):#line:85
            OO00O0OO000OOOO0O =(OO00O0OO000OOOO0O ,)#line:86
        OO00O0OO000OOOO0O =[OOO000OOOO0OO00O0 ._to_label (O0OO0OOO00O000000 )for O0OO0OOO00O000000 in OO00O0OO000OOOO0O ]#line:87
        OO00O0OO000OOOO0O =[O0OO0OO0000OO000O for O0OO0OO0000OO000O in OO00O0OO000OOOO0O if O0OO0OO0000OO000O in OOO000OOOO0OO00O0 ._columns ]#line:88
        OO00O0000OO00OOO0 =np .transpose (np .array ([OOO000OOOO0OO00O0 ._columns [O0OOO0O000O0OOOOO ]for O0OOO0O000O0OOOOO in OO00O0OO000OOOO0O ]))#line:89
        if OO00O0000OO00OOO0 .shape [0 ]<=0 or (len (OO00O0000OO00OOO0 .shape )>1 and OO00O0000OO00OOO0 .shape [1 ]<=0 ):return False #line:90
        if not isinstance (O0O0OO00O0000O00O ,(list ,tuple )):#line:92
            O0O0OO00O0000O00O =(O0O0OO00O0000O00O ,)#line:93
        O0O0OO00O0000O00O =[OOO000OOOO0OO00O0 ._to_label (O0OOOOO0OOOO0OOOO )for O0OOOOO0OOOO0OOOO in O0O0OO00O0000O00O ]#line:94
        O0O0OO00O0000O00O =[OO0O0O000OOO00OO0 for OO0O0O000OOO00OO0 in O0O0OO00O0000O00O if OO0O0O000OOO00OO0 in OOO000OOOO0OO00O0 ._columns ]#line:95
        OO000OO000O000OO0 =np .transpose (np .array ([OOO000OOOO0OO00O0 ._columns [O0OO0OOOOO000OO0O ]for O0OO0OOOOO000OO0O in O0O0OO00O0000O00O ]))#line:96
        if OO000OO000O000OO0 .shape [0 ]<=0 or (len (OO000OO000O000OO0 .shape )>1 and OO000OO000O000OO0 .shape [1 ]<=0 ):return False #line:97
        OOO000OOOO0OO00O0 ._regression .fit (OO00O0000OO00OOO0 ,OO000OO000O000OO0 )#line:99
        O0OOO000O0OOO0O0O ={}#line:100
        for O0O0OOO0O0OOOO0OO ,O0O000O0O0OOOOO0O in enumerate (O0O0OO00O0000O00O ):#line:101
            O000O0OO00OOOOO00 =OOO000OOOO0OO00O0 ._regression .coef_ [O0O0OOO0O0OOOO0OO ]#line:102
            O00O0000OOOO0O0OO =OOO000OOOO0OO00O0 ._regression .intercept_ [O0O0OOO0O0OOOO0OO ]#line:103
            OO0O00O0OOOOO00O0 ='{} = '.format (O0O000O0O0OOOOO0O )#line:104
            for O0000OO00O00OOO00 ,OO00O0000OO0O0O00 in enumerate (OO00O0OO000OOOO0O ):#line:105
                OO0O00O0OOOOO00O0 +='{} * {} + '.format (O000O0OO00OOOOO00 [O0000OO00O00OOO00 ],OO00O0000OO0O0O00 )#line:106
            print (OO0O00O0OOOOO00O0 +str (O00O0000OOOO0O0OO ))#line:107
            O0OOO000O0OOO0O0O [O0O000O0O0OOOOO0O ]=tuple (np .append (O000O0OO00OOOOO00 ,O00O0000OOOO0O0OO ))#line:108
        OOO000OOOO0OO00O0 ._result ['xlabels']=OO00O0OO000OOOO0O #line:109
        OOO000OOOO0OO00O0 ._result ['ylabels']=O0O0OO00O0000O00O #line:110
        OOO000OOOO0OO00O0 ._result ['weights']=O0OOO000O0OOO0O0O #line:111
        return True #line:112
    def get_weight (OO0000OO0O00O0OO0 ,ylabel ='all'):#line:114
        OO0O000O0O0O00000 =OO0000OO0O00O0OO0 ._result ['weights']#line:115
        if isinstance (ylabel ,str )and ylabel .lower ()=='all':#line:116
            return OO0O000O0O0O00000 #line:117
        ylabel =OO0000OO0O00O0OO0 ._to_label (ylabel )#line:118
        if ylabel in OO0O000O0O0O00000 :#line:119
            return OO0O000O0O0O00000 [ylabel ]#line:120
        return None #line:121
    def print_labels (OO0O0OOO0OOOOO00O ):#line:123
        print (OO0O0OOO0OOOOO00O ._labels )#line:124
    def print_data (OOO0O0O0O0O0OO0O0 ):#line:126
        print (OOO0O0O0O0O0OO0O0 ._data )#line:127
    def _plot_data_2d (OOO0O0OO0OO0000O0 ,O0O0O000OOO00O000 ,OO0O00O0O00O00O0O ,O0O00O0OO0O00O00O ):#line:129
        OO0OO000OO00O00O0 =len (O0O0O000OOO00O000 )#line:130
        O0O0O000O0O00OO00 =len (OO0O00O0O00O00O0O )#line:131
        O0OO0O0000OO00O00 =plt .figure ()#line:132
        OOOOO00O0O0O00O0O =1 #line:133
        for O0O0O0O0O000OO00O in O0O0O000OOO00O000 :#line:134
            O0O0O0O0O000OO00O =OOO0O0OO0OO0000O0 ._to_label (O0O0O0O0O000OO00O )#line:135
            O0O0OO0OOO000OO0O =OOO0O0OO0OO0000O0 ._get_data (O0O0O0O0O000OO00O )#line:136
            if O0O0OO0OOO000OO0O is not None :#line:137
                for OOOO0O0OOO0000000 ,OOO000O00OO0OO0O0 in enumerate (OO0O00O0O00O00O0O ):#line:138
                    OOO000O00OO0OO0O0 =OOO0O0OO0OO0000O0 ._to_label (OOO000O00OO0OO0O0 )#line:139
                    O0OOOO00O00O0OOOO =OOO0O0OO0OO0000O0 ._get_data (OOO000O00OO0OO0O0 )#line:140
                    OO00O000O000O0000 =O0OO0O0000OO00O00 .add_subplot (OO0OO000OO00O00O0 ,O0O0O000O0O00OO00 ,OOOOO00O0O0O00O0O )#line:141
                    if O0OOOO00O00O0OOOO is not None :#line:142
                        OO00O000O000O0000 .scatter (O0O0OO0OOO000OO0O ,O0OOOO00O00O0OOOO ,c =O0O00O0OO0O00O00O [OOOO0O0OOO0000000 ])#line:143
                        OO00O000O000O0000 .set_xlabel (O0O0O0O0O000OO00O )#line:144
                        OO00O000O000O0000 .set_ylabel (OOO000O00OO0OO0O0 )#line:145
                        OOOOO00O0O0O00O0O +=1 #line:146
    def _plot_data_3d (OO0O0O0OO00O000OO ,OO0O00O0OO00O00O0 ,OO00OO00OOO0OO0OO ,O0O00O00OO00O0OOO ):#line:148
        O0OO0OO000OOO0OOO =OO0O0O0OO00O000OO ._to_label (OO0O00O0OO00O00O0 [0 ])#line:149
        O00OO00OOO0000O0O =OO0O0O0OO00O000OO ._to_label (OO0O00O0OO00O00O0 [1 ])#line:150
        O0OO000OO0OO0000O =OO0O0O0OO00O000OO ._get_data (O0OO0OO000OOO0OOO )#line:151
        O0O000OOOO0O00OO0 =OO0O0O0OO00O000OO ._get_data (O00OO00OOO0000O0O )#line:152
        if O0OO000OO0OO0000O is not None and O0O000OOOO0O00OO0 is not None :#line:153
            O00O0OO00000OOO0O =len (OO00OO00OOO0OO0OO )#line:154
            OOO0OOOO0O0O000OO =plt .figure ()#line:155
            O000000O0OOOO0O00 =1 #line:156
            for O000000O00OOO0O0O ,O000OO000000O0000 in enumerate (OO00OO00OOO0OO0OO ):#line:157
                O000OO000000O0000 =OO0O0O0OO00O000OO ._to_label (O000OO000000O0000 )#line:158
                O0O00O0OO00OOO00O =OO0O0O0OO00O000OO ._get_data (O000OO000000O0000 )#line:159
                O0OOO0O000O000OOO =OOO0OOOO0O0O000OO .add_subplot (1 ,O00O0OO00000OOO0O ,O000000O0OOOO0O00 ,projection ='3d')#line:160
                if O0O00O0OO00OOO00O is not None :#line:161
                    O0OOO0O000O000OOO .scatter (O0OO000OO0OO0000O ,O0O000OOOO0O00OO0 ,O0O00O0OO00OOO00O ,c =O0O00O00OO00O0OOO [O000000O00OOO0O0O ])#line:162
                    O0OOO0O000O000OOO .set_xlabel (O0OO0OO000OOO0OOO )#line:163
                    O0OOO0O000O000OOO .set_ylabel (O00OO00OOO0000O0O )#line:164
                    O0OOO0O000O000OOO .set_zlabel (O000OO000000O0000 )#line:165
                    O000000O0OOOO0O00 +=1 #line:166
    def plot_data (OO00OOOO0OOO00OOO ,OOOOOO0000O0OO0OO ,O00OO0000OOO000OO ,colors ='blue',block =True ):#line:168
        if OO00OOOO0OOO00OOO ._data is not None :#line:169
            if not isinstance (OOOOOO0000O0OO0OO ,(list ,tuple )):#line:170
                OOOOOO0000O0OO0OO =(OOOOOO0000O0OO0OO ,)#line:171
            if not isinstance (O00OO0000OOO000OO ,(list ,tuple )):#line:172
                O00OO0000OOO000OO =(O00OO0000OOO000OO ,)#line:173
            if not isinstance (colors ,(list ,tuple )):#line:174
                colors =(colors ,)#line:175
            O0OO0000OOOO0O0OO =len (O00OO0000OOO000OO )-len (colors )#line:176
            if O0OO0000OOOO0O0OO >0 :#line:177
                colors =[OO0000O0O0OOOO000 for OO0000O0O0OOOO000 in colors ]#line:178
                colors .extend ([colors [-1 ]]*O0OO0000OOOO0O0OO )#line:179
            if len (OOOOOO0000O0OO0OO )==2 :#line:180
                OO00OOOO0OOO00OOO ._plot_data_3d (OOOOOO0000O0OO0OO ,O00OO0000OOO000OO ,colors )#line:181
            else :#line:182
                OO00OOOO0OOO00OOO ._plot_data_2d (OOOOOO0000O0OO0OO ,O00OO0000OOO000OO ,colors )#line:183
            plt .show (block =block )#line:184
    def _get_prediction_range (OOO0O000O00OO0O00 ,OO00OOO0000O0OOOO ):#line:186
        O0OOO0O00O00O00OO =np .min (OO00OOO0000O0OOOO )#line:187
        O0OO00OOOO00O00OO =np .max (OO00OOO0000O0OOOO )#line:188
        if O0OOO0O00O00O00OO ==O0OO00OOOO00O00OO :#line:189
            return np .array ([0 ]*11 )#line:190
        else :#line:191
            OO0OOO0O000OOOO00 =(O0OO00OOOO00O00OO -O0OOO0O00O00O00OO )/10 #line:192
            return np .arange (O0OOO0O00O00O00OO ,O0OO00OOOO00O00OO +OO0OOO0O000OOOO00 ,OO0OOO0O000OOOO00 )#line:193
    def _plot_result_2d (O000O0O0OOO0O0O0O ,O0O0O00OO00O0O00O ,OO000OOOOO00OOO0O ,OOO00OO000OO000O0 ):#line:195
        O0OOO00OO0O0000OO =O000O0O0OOO0O0O0O ._to_label (O0O0O00OO00O0O00O [0 ])#line:196
        OOO00OO00O0O00O00 =O000O0O0OOO0O0O0O ._get_data (O0OOO00OO0O0000OO )#line:197
        if OOO00OO00O0O00O00 is not None :#line:198
            OOO0O00O000OOO0OO =O000O0O0OOO0O0O0O ._get_prediction_range (OOO00OO00O0O00O00 ).reshape (-1 ,1 )#line:199
            O0OOO000O000O0000 =O000O0O0OOO0O0O0O ._regression .predict (OOO0O00O000OOO0OO )#line:200
            OO00OO00O0000OO0O =len (OO000OOOOO00OOO0O )#line:202
            OO000O0O0OOOOO000 =plt .figure ()#line:203
            OOO0O000OO0OO0OO0 =1 #line:204
            for O0OO00O0O00OOOOOO ,OO0OO0OO00O00000O in enumerate (OO000OOOOO00OOO0O ):#line:205
                OO0OO0OO00O00000O =O000O0O0OOO0O0O0O ._to_label (OO0OO0OO00O00000O )#line:206
                O0O00O0OO00000O0O =O000O0O0OOO0O0O0O ._get_data (OO0OO0OO00O00000O )#line:207
                O000O00O0OO0O0O0O =O000O0O0OOO0O0O0O .get_weight (OO0OO0OO00O00000O )#line:208
                OOO000OO00OO000OO =OO000O0O0OOOOO000 .add_subplot (1 ,OO00OO00O0000OO0O ,OOO0O000OO0OO0OO0 )#line:209
                if O0O00O0OO00000O0O is not None and O000O00O0OO0O0O0O is not None :#line:210
                    OOO000OO00OO000OO .scatter (OOO00OO00O0O00O00 ,O0O00O0OO00000O0O ,c =OOO00OO000OO000O0 [O0OO00O0O00OOOOOO ])#line:211
                    OOO000OO00OO000OO .plot (OOO0O00O000OOO0OO ,O0OOO000O000O0000 [:,O0OO00O0O00OOOOOO ],c ='r')#line:212
                    OOO000OO00OO000OO .set_xlabel (O0OOO00OO0O0000OO )#line:213
                    OOO000OO00OO000OO .set_ylabel (OO0OO0OO00O00000O )#line:214
                    OOO0O000OO0OO0OO0 +=1 #line:215
    def _plot_result_3d (O00OO0OO0OOOOOO0O ,OOOOOOO0O0000O0O0 ,O0000OOOOOOO00OO0 ,O0000O0O00O0O0OOO ):#line:217
        OO00O00000O0000OO =O00OO0OO0OOOOOO0O ._to_label (OOOOOOO0O0000O0O0 [0 ])#line:218
        OOOOOO0O00OOO0000 =O00OO0OO0OOOOOO0O ._to_label (OOOOOOO0O0000O0O0 [1 ])#line:219
        O000O0O0O00O0OO00 =O00OO0OO0OOOOOO0O ._get_data (OO00O00000O0000OO )#line:220
        OO0O000O00O0O0O00 =O00OO0OO0OOOOOO0O ._get_data (OOOOOO0O00OOO0000 )#line:221
        if O000O0O0O00O0OO00 is not None and OO0O000O00O0O0O00 is not None :#line:222
            OO0OO0OOO000OO000 =O00OO0OO0OOOOOO0O ._get_prediction_range (O000O0O0O00O0OO00 )#line:223
            OOO0O0O0OO0OOO0O0 =O00OO0OO0OOOOOO0O ._get_prediction_range (OO0O000O00O0O0O00 )#line:224
            OOOOOO0O0O0O0O0OO =O00OO0OO0OOOOOO0O ._regression .predict (np .array ([(O0O00O0000000000O ,O0O0O0OOO000OO0O0 )for O0O0O0OOO000OO0O0 in OOO0O0O0OO0OOO0O0 for O0O00O0000000000O in OO0OO0OOO000OO000 ]))#line:225
            OO0OO0OOO000OO000 ,OOO0O0O0OO0OOO0O0 =np .meshgrid (OO0OO0OOO000OO000 ,OOO0O0O0OO0OOO0O0 )#line:226
            O000O00O0OOO00000 =len (O0000OOOOOOO00OO0 )#line:228
            OO0O000O0O0O0O00O =plt .figure ()#line:229
            O0OOO0O0O0O00O00O =1 #line:230
            for OO0O000OOOOOO0OOO ,OOO000OO0O0OOO00O in enumerate (O0000OOOOOOO00OO0 ):#line:231
                OOO000OO0O0OOO00O =O00OO0OO0OOOOOO0O ._to_label (OOO000OO0O0OOO00O )#line:232
                OO00OO0000O0OOO00 =O00OO0OO0OOOOOO0O ._get_data (OOO000OO0O0OOO00O )#line:233
                OO0OO0OOO0O00O0O0 =O00OO0OO0OOOOOO0O .get_weight (OOO000OO0O0OOO00O )#line:234
                O000OOOO0OO0OOOO0 =OO0O000O0O0O0O00O .add_subplot (1 ,O000O00O0OOO00000 ,O0OOO0O0O0O00O00O ,projection ='3d')#line:235
                if OO00OO0000O0OOO00 is not None and OO0OO0OOO0O00O0O0 is not None :#line:236
                    O000OOOO0OO0OOOO0 .scatter (O000O0O0O00O0OO00 ,OO0O000O00O0O0O00 ,OO00OO0000O0OOO00 ,c =O0000O0O00O0O0OOO [OO0O000OOOOOO0OOO ])#line:237
                    O000OOOO0OO0OOOO0 .plot_surface (OO0OO0OOO000OO000 ,OOO0O0O0OO0OOO0O0 ,OOOOOO0O0O0O0O0OO [:,OO0O000OOOOOO0OOO ].reshape (OO0OO0OOO000OO000 .shape ),color ='red')#line:238
                    O000OOOO0OO0OOOO0 .set_xlabel (OO00O00000O0000OO )#line:239
                    O000OOOO0OO0OOOO0 .set_ylabel (OOOOOO0O00OOO0000 )#line:240
                    O000OOOO0OO0OOOO0 .set_zlabel (OOO000OO0O0OOO00O )#line:241
                    O0OOO0O0O0O00O00O +=1 #line:242
    def plot_result (OO0O000000O00OO00 ,colors ='blue',block =True ):#line:244
        if OO0O000000O00OO00 ._data is not None :#line:245
            O0000OOO00O000000 =OO0O000000O00OO00 ._result ['xlabels']#line:246
            OOO00000OOO0O0O00 =OO0O000000O00OO00 ._result ['ylabels']#line:247
            if O0000OOO00O000000 is not None and OOO00000OOO0O0O00 is not None :#line:248
                if not isinstance (colors ,(list ,tuple )):#line:249
                    colors =(colors ,)#line:250
                OO00O0OO00O0OO000 =len (OOO00000OOO0O0O00 )-len (colors )#line:251
                if OO00O0OO00O0OO000 >0 :#line:252
                    colors =[OO0OO000O0OOOOOOO for OO0OO000O0OOOOOOO in colors ]#line:253
                    colors .extend ([colors [-1 ]]*OO00O0OO00O0OO000 )#line:254
                O00OO0OO0O0OOOO0O =len (O0000OOO00O000000 )#line:255
                if O00OO0OO0O0OOOO0O ==1 :#line:256
                    OO0O000000O00OO00 ._plot_result_2d (O0000OOO00O000000 ,OOO00000OOO0O0O00 ,colors )#line:257
                    plt .show (block =block )#line:258
                elif O00OO0OO0O0OOOO0O ==2 :#line:259
                    OO0O000000O00OO00 ._plot_result_3d (O0000OOO00O000000 ,OOO00000OOO0O0O00 ,colors )#line:260
                    plt .show (block =block )#line:261
    def _plot_weight_2d (O0O0O00O00OO00O00 ,O0O000OO000OO0000 ,OO00OO000O0000OOO ,OOOOO0O0OOOO00O0O ,OO0O0000OOO00OO0O ):#line:263
        OOO0000OO0O00000O =O0O0O00O00OO00O00 ._to_label (O0O000OO000OO0000 [0 ])#line:264
        OOO00O00000O0O000 =O0O0O00O00OO00O00 ._get_data (OOO0000OO0O00000O )#line:265
        if OOO00O00000O0O000 is not None :#line:266
            OO0O0O000O0OO000O =O0O0O00O00OO00O00 ._get_prediction_range (OOO00O00000O0O000 ).reshape (-1 ,1 )#line:267
            O0O0OO0O00O0OO0OO =len (OO00OO000O0000OOO )#line:268
            OOOOOO0000OOO0OO0 =plt .figure ()#line:269
            O0O000OO0O00OOO0O =1 #line:270
            for O00O0OOO0O00OO00O ,OOOO00O00OOO0O000 in enumerate (OO00OO000O0000OOO ):#line:271
                OOOO00O00OOO0O000 =O0O0O00O00OO00O00 ._to_label (OOOO00O00OOO0O000 )#line:272
                O00OOOO0OO0OOO0OO =O0O0O00O00OO00O00 ._get_data (OOOO00O00OOO0O000 )#line:273
                OOOOO0OOOO0O0O00O =OOOOO0O0OOOO00O0O [O00O0OOO0O00OO00O ]#line:274
                OOO0O00O0O0OOOOO0 =OOOOO0OOOO0O0O00O [0 ]*OO0O0O000O0OO000O +OOOOO0OOOO0O0O00O [1 ]#line:275
                OO000O00000OO00OO =OOOOOO0000OOO0OO0 .add_subplot (1 ,O0O0OO0O00O0OO0OO ,O0O000OO0O00OOO0O )#line:276
                if O00OOOO0OO0OOO0OO is not None :#line:277
                    OO000O00000OO00OO .scatter (OOO00O00000O0O000 ,O00OOOO0OO0OOO0OO ,c =OO0O0000OOO00OO0O [O00O0OOO0O00OO00O ])#line:278
                    OO000O00000OO00OO .plot (OO0O0O000O0OO000O ,OOO0O00O0O0OOOOO0 ,c ='r')#line:279
                    OO000O00000OO00OO .set_xlabel (OOO0000OO0O00000O )#line:280
                    OO000O00000OO00OO .set_ylabel (OOOO00O00OOO0O000 )#line:281
                    O0O000OO0O00OOO0O +=1 #line:282
    def _plot_weight_3d (OO00OOO00O0OOOOO0 ,OOOOOO0O00OO0OOO0 ,OOO0O0OO00OOO0OO0 ,O0OOO00OO00OOOOO0 ,OOOO00O00OOO000OO ):#line:284
        OOO0OOO00O000O0O0 =OO00OOO00O0OOOOO0 ._to_label (OOOOOO0O00OO0OOO0 [0 ])#line:285
        O00OOO0OO0O0000OO =OO00OOO00O0OOOOO0 ._to_label (OOOOOO0O00OO0OOO0 [1 ])#line:286
        OOO000O00OO000OOO =OO00OOO00O0OOOOO0 ._get_data (OOO0OOO00O000O0O0 )#line:287
        OOO000OO0OOO0OOO0 =OO00OOO00O0OOOOO0 ._get_data (O00OOO0OO0O0000OO )#line:288
        if OOO000O00OO000OOO is not None and OOO000OO0OOO0OOO0 is not None :#line:289
            O00O0O0O00OO0OO00 =OO00OOO00O0OOOOO0 ._get_prediction_range (OOO000O00OO000OOO )#line:290
            OOOO0000OOO00000O =OO00OOO00O0OOOOO0 ._get_prediction_range (OOO000OO0OOO0OOO0 )#line:291
            OO000OO0O00O00OO0 ,O0O0O00O0OO0O000O =np .meshgrid (O00O0O0O00OO0OO00 ,OOOO0000OOO00000O )#line:292
            OO00O0000O0000O0O =len (OOO0O0OO00OOO0OO0 )#line:294
            O0O0OOOOOO0O00O00 =plt .figure ()#line:295
            OOOO00O0O0O0OOO0O =1 #line:296
            for O000O0OOOOOO0O0OO ,OO0O0O00O00OOOOOO in enumerate (OOO0O0OO00OOO0OO0 ):#line:297
                OO0O0O00O00OOOOOO =OO00OOO00O0OOOOO0 ._to_label (OO0O0O00O00OOOOOO )#line:298
                OO0OOOOOOO0O0OO00 =OO00OOO00O0OOOOO0 ._get_data (OO0O0O00O00OOOOOO )#line:299
                OOOOOOO0O0OO00000 =O0OOO00OO00OOOOO0 [O000O0OOOOOO0O0OO ]#line:300
                O0OO000O0OOOOO0OO =np .array ([OOOOOOO0O0OO00000 [0 ]*O0OOOOO0O0000000O +OOOOOOO0O0OO00000 [1 ]*O00OO0OOO00000O00 +OOOOOOO0O0OO00000 [2 ]for O00OO0OOO00000O00 in OOOO0000OOO00000O for O0OOOOO0O0000000O in O00O0O0O00OO0OO00 ])#line:301
                O00OOOO000O0O0OOO =O0O0OOOOOO0O00O00 .add_subplot (1 ,OO00O0000O0000O0O ,OOOO00O0O0O0OOO0O ,projection ='3d')#line:302
                if OO0OOOOOOO0O0OO00 is not None :#line:303
                    O00OOOO000O0O0OOO .scatter (OOO000O00OO000OOO ,OOO000OO0OOO0OOO0 ,OO0OOOOOOO0O0OO00 ,c =OOOO00O00OOO000OO [O000O0OOOOOO0O0OO ])#line:304
                    O00OOOO000O0O0OOO .plot_surface (OO000OO0O00O00OO0 ,O0O0O00O0OO0O000O ,O0OO000O0OOOOO0OO .reshape (OO000OO0O00O00OO0 .shape ),color ='red')#line:305
                    O00OOOO000O0O0OOO .set_xlabel (OOO0OOO00O000O0O0 )#line:306
                    O00OOOO000O0O0OOO .set_ylabel (O00OOO0OO0O0000OO )#line:307
                    O00OOOO000O0O0OOO .set_zlabel (OO0O0O00O00OOOOOO )#line:308
                    OOOO00O0O0O0OOO0O +=1 #line:309
    def plot_weight (OO0OO00O0O0O00OO0 ,O00O0OO000000O0O0 ,OOO0OOOO0O0OO0OO0 ,O00O00OO0O0O000O0 ,colors ='blue',block =True ):#line:311
        if OO0OO00O0O0O00OO0 ._data is not None and isinstance (O00O00OO0O0O000O0 ,(list ,tuple ,dict )):#line:312
            if not isinstance (O00O0OO000000O0O0 ,(list ,tuple )):#line:313
                O00O0OO000000O0O0 =(O00O0OO000000O0O0 ,)#line:314
            if not isinstance (OOO0OOOO0O0OO0OO0 ,(list ,tuple )):#line:315
                OOO0OOOO0O0OO0OO0 =(OOO0OOOO0O0OO0OO0 ,)#line:316
            if isinstance (O00O00OO0O0O000O0 ,dict ):#line:317
                O00O00OO0O0O000O0 =[O00O00OO0O0O000O0 [O00OOOO000O0O00OO ]for O00OOOO000O0O00OO in OOO0OOOO0O0OO0OO0 ]#line:318
            elif not isinstance (O00O00OO0O0O000O0 [0 ],(list ,tuple )):#line:319
                O00O00OO0O0O000O0 =(O00O00OO0O0O000O0 ,)#line:320
            if not isinstance (colors ,(list ,tuple )):#line:321
                colors =(colors ,)#line:322
            O000OOOO00O0O000O =len (OOO0OOOO0O0OO0OO0 )-len (colors )#line:323
            if O000OOOO00O0O000O >0 :#line:324
                colors =[O000O0000OO0OOO00 for O000O0000OO0OOO00 in colors ]#line:325
                colors .extend ([colors [-1 ]]*O000OOOO00O0O000O )#line:326
            OOO0O00O00OOOOO0O =len (O00O0OO000000O0O0 )#line:327
            if OOO0O00O00OOOOO0O ==1 :#line:328
                OO0OO00O0O0O00OO0 ._plot_weight_2d (O00O0OO000000O0O0 ,OOO0OOOO0O0OO0OO0 ,O00O00OO0O0O000O0 ,colors )#line:329
                plt .show (block =block )#line:330
            elif OOO0O00O00OOOOO0O ==2 :#line:331
                OO0OO00O0O0O00OO0 ._plot_weight_3d (O00O0OO000000O0O0 ,OOO0OOOO0O0OO0OO0 ,O00O00OO0O0O000O0 ,colors )#line:332
                plt .show (block =block )#line:333
