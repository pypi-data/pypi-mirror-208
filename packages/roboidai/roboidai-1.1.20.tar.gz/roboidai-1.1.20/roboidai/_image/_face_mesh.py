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
import numpy as np #line:20
import mediapipe as mp #line:21
from ._util import Util #line:22
from timeit import default_timer as timer #line:23
_OO0000OOO00000OOO =(127 ,34 ,139 ,11 ,0 ,37 ,232 ,231 ,120 ,72 ,37 ,39 ,128 ,121 ,47 ,232 ,121 ,128 ,104 ,69 ,67 ,175 ,171 ,148 ,157 ,154 ,155 ,118 ,50 ,101 ,73 ,39 ,40 ,9 ,151 ,108 ,48 ,115 ,131 ,194 ,204 ,211 ,74 ,40 ,185 ,80 ,42 ,183 ,40 ,92 ,186 ,230 ,229 ,118 ,202 ,212 ,214 ,83 ,18 ,17 ,76 ,61 ,146 ,160 ,29 ,30 ,56 ,157 ,173 ,106 ,204 ,194 ,135 ,214 ,192 ,203 ,165 ,98 ,21 ,71 ,68 ,51 ,45 ,4 ,144 ,24 ,23 ,77 ,146 ,91 ,205 ,50 ,187 ,201 ,200 ,18 ,91 ,106 ,182 ,90 ,91 ,181 ,85 ,84 ,17 ,206 ,203 ,36 ,148 ,171 ,140 ,92 ,40 ,39 ,193 ,189 ,244 ,159 ,158 ,28 ,247 ,246 ,161 ,236 ,3 ,196 ,54 ,68 ,104 ,193 ,168 ,8 ,117 ,228 ,31 ,189 ,193 ,55 ,98 ,97 ,99 ,126 ,47 ,100 ,166 ,79 ,218 ,155 ,154 ,26 ,209 ,49 ,131 ,135 ,136 ,150 ,47 ,126 ,217 ,223 ,52 ,53 ,45 ,51 ,134 ,211 ,170 ,140 ,67 ,69 ,108 ,43 ,106 ,91 ,230 ,119 ,120 ,226 ,130 ,247 ,63 ,53 ,52 ,238 ,20 ,242 ,46 ,70 ,156 ,78 ,62 ,96 ,46 ,53 ,63 ,143 ,34 ,227 ,173 ,155 ,133 ,123 ,117 ,111 ,44 ,125 ,19 ,236 ,134 ,51 ,216 ,206 ,205 ,154 ,153 ,22 ,39 ,37 ,167 ,200 ,201 ,208 ,36 ,142 ,100 ,57 ,212 ,202 ,20 ,60 ,99 ,28 ,158 ,157 ,35 ,226 ,113 ,160 ,159 ,27 ,204 ,202 ,210 ,113 ,225 ,46 ,43 ,202 ,204 ,62 ,76 ,77 ,137 ,123 ,116 ,41 ,38 ,72 ,203 ,129 ,142 ,64 ,98 ,240 ,49 ,102 ,64 ,41 ,73 ,74 ,212 ,216 ,207 ,42 ,74 ,184 ,169 ,170 ,211 ,170 ,149 ,176 ,105 ,66 ,69 ,122 ,6 ,168 ,123 ,147 ,187 ,96 ,77 ,90 ,65 ,55 ,107 ,89 ,90 ,180 ,101 ,100 ,120 ,63 ,105 ,104 ,93 ,137 ,227 ,15 ,86 ,85 ,129 ,102 ,49 ,14 ,87 ,86 ,55 ,8 ,9 ,100 ,47 ,121 ,145 ,23 ,22 ,88 ,89 ,179 ,6 ,122 ,196 ,88 ,95 ,96 ,138 ,172 ,136 ,215 ,58 ,172 ,115 ,48 ,219 ,42 ,80 ,81 ,195 ,3 ,51 ,43 ,146 ,61 ,171 ,175 ,199 ,81 ,82 ,38 ,53 ,46 ,225 ,144 ,163 ,110 ,246 ,33 ,7 ,52 ,65 ,66 ,229 ,228 ,117 ,34 ,127 ,234 ,107 ,108 ,69 ,109 ,108 ,151 ,48 ,64 ,235 ,62 ,78 ,191 ,129 ,209 ,126 ,111 ,35 ,143 ,163 ,161 ,246 ,117 ,123 ,50 ,222 ,65 ,52 ,19 ,125 ,141 ,221 ,55 ,65 ,3 ,195 ,197 ,25 ,7 ,33 ,220 ,237 ,44 ,70 ,71 ,139 ,122 ,193 ,245 ,247 ,130 ,33 ,71 ,21 ,162 ,153 ,158 ,159 ,170 ,169 ,150 ,188 ,174 ,196 ,216 ,186 ,92 ,144 ,160 ,161 ,2 ,97 ,167 ,141 ,125 ,241 ,164 ,167 ,37 ,72 ,38 ,12 ,145 ,159 ,160 ,38 ,82 ,13 ,63 ,68 ,71 ,226 ,35 ,111 ,158 ,153 ,154 ,101 ,50 ,205 ,206 ,92 ,165 ,209 ,198 ,217 ,165 ,167 ,97 ,220 ,115 ,218 ,133 ,112 ,243 ,239 ,238 ,241 ,214 ,135 ,169 ,190 ,173 ,133 ,171 ,208 ,32 ,125 ,44 ,237 ,86 ,87 ,178 ,85 ,86 ,179 ,84 ,85 ,180 ,83 ,84 ,181 ,201 ,83 ,182 ,137 ,93 ,132 ,76 ,62 ,183 ,61 ,76 ,184 ,57 ,61 ,185 ,212 ,57 ,186 ,214 ,207 ,187 ,34 ,143 ,156 ,79 ,239 ,237 ,123 ,137 ,177 ,44 ,1 ,4 ,201 ,194 ,32 ,64 ,102 ,129 ,213 ,215 ,138 ,59 ,166 ,219 ,242 ,99 ,97 ,2 ,94 ,141 ,75 ,59 ,235 ,24 ,110 ,228 ,25 ,130 ,226 ,23 ,24 ,229 ,22 ,23 ,230 ,26 ,22 ,231 ,112 ,26 ,232 ,189 ,190 ,243 ,221 ,56 ,190 ,28 ,56 ,221 ,27 ,28 ,222 ,29 ,27 ,223 ,30 ,29 ,224 ,247 ,30 ,225 ,238 ,79 ,20 ,166 ,59 ,75 ,60 ,75 ,240 ,147 ,177 ,215 ,20 ,79 ,166 ,187 ,147 ,213 ,112 ,233 ,244 ,233 ,128 ,245 ,128 ,114 ,188 ,114 ,217 ,174 ,131 ,115 ,220 ,217 ,198 ,236 ,198 ,131 ,134 ,177 ,132 ,58 ,143 ,35 ,124 ,110 ,163 ,7 ,228 ,110 ,25 ,356 ,389 ,368 ,11 ,302 ,267 ,452 ,350 ,349 ,302 ,303 ,269 ,357 ,343 ,277 ,452 ,453 ,357 ,333 ,332 ,297 ,175 ,152 ,377 ,384 ,398 ,382 ,347 ,348 ,330 ,303 ,304 ,270 ,9 ,336 ,337 ,278 ,279 ,360 ,418 ,262 ,431 ,304 ,408 ,409 ,310 ,415 ,407 ,270 ,409 ,410 ,450 ,348 ,347 ,422 ,430 ,434 ,313 ,314 ,17 ,306 ,307 ,375 ,387 ,388 ,260 ,286 ,414 ,398 ,335 ,406 ,418 ,364 ,367 ,416 ,423 ,358 ,327 ,251 ,284 ,298 ,281 ,5 ,4 ,373 ,374 ,253 ,307 ,320 ,321 ,425 ,427 ,411 ,421 ,313 ,18 ,321 ,405 ,406 ,320 ,404 ,405 ,315 ,16 ,17 ,426 ,425 ,266 ,377 ,400 ,369 ,322 ,391 ,269 ,417 ,465 ,464 ,386 ,257 ,258 ,466 ,260 ,388 ,456 ,399 ,419 ,284 ,332 ,333 ,417 ,285 ,8 ,346 ,340 ,261 ,413 ,441 ,285 ,327 ,460 ,328 ,355 ,371 ,329 ,392 ,439 ,438 ,382 ,341 ,256 ,429 ,420 ,360 ,364 ,394 ,379 ,277 ,343 ,437 ,443 ,444 ,283 ,275 ,440 ,363 ,431 ,262 ,369 ,297 ,338 ,337 ,273 ,375 ,321 ,450 ,451 ,349 ,446 ,342 ,467 ,293 ,334 ,282 ,458 ,461 ,462 ,276 ,353 ,383 ,308 ,324 ,325 ,276 ,300 ,293 ,372 ,345 ,447 ,382 ,398 ,362 ,352 ,345 ,340 ,274 ,1 ,19 ,456 ,248 ,281 ,436 ,427 ,425 ,381 ,256 ,252 ,269 ,391 ,393 ,200 ,199 ,428 ,266 ,330 ,329 ,287 ,273 ,422 ,250 ,462 ,328 ,258 ,286 ,384 ,265 ,353 ,342 ,387 ,259 ,257 ,424 ,431 ,430 ,342 ,353 ,276 ,273 ,335 ,424 ,292 ,325 ,307 ,366 ,447 ,345 ,271 ,303 ,302 ,423 ,266 ,371 ,294 ,455 ,460 ,279 ,278 ,294 ,271 ,272 ,304 ,432 ,434 ,427 ,272 ,407 ,408 ,394 ,430 ,431 ,395 ,369 ,400 ,334 ,333 ,299 ,351 ,417 ,168 ,352 ,280 ,411 ,325 ,319 ,320 ,295 ,296 ,336 ,319 ,403 ,404 ,330 ,348 ,349 ,293 ,298 ,333 ,323 ,454 ,447 ,15 ,16 ,315 ,358 ,429 ,279 ,14 ,15 ,316 ,285 ,336 ,9 ,329 ,349 ,350 ,374 ,380 ,252 ,318 ,402 ,403 ,6 ,197 ,419 ,318 ,319 ,325 ,367 ,364 ,365 ,435 ,367 ,397 ,344 ,438 ,439 ,272 ,271 ,311 ,195 ,5 ,281 ,273 ,287 ,291 ,396 ,428 ,199 ,311 ,271 ,268 ,283 ,444 ,445 ,373 ,254 ,339 ,263 ,466 ,249 ,282 ,334 ,296 ,449 ,347 ,346 ,264 ,447 ,454 ,336 ,296 ,299 ,338 ,10 ,151 ,278 ,439 ,455 ,292 ,407 ,415 ,358 ,371 ,355 ,340 ,345 ,372 ,390 ,249 ,466 ,346 ,347 ,280 ,442 ,443 ,282 ,19 ,94 ,370 ,441 ,442 ,295 ,248 ,419 ,197 ,263 ,255 ,359 ,440 ,275 ,274 ,300 ,383 ,368 ,351 ,412 ,465 ,263 ,467 ,466 ,301 ,368 ,389 ,380 ,374 ,386 ,395 ,378 ,379 ,412 ,351 ,419 ,436 ,426 ,322 ,373 ,390 ,388 ,2 ,164 ,393 ,370 ,462 ,461 ,164 ,0 ,267 ,302 ,11 ,12 ,374 ,373 ,387 ,268 ,12 ,13 ,293 ,300 ,301 ,446 ,261 ,340 ,385 ,384 ,381 ,330 ,266 ,425 ,426 ,423 ,391 ,429 ,355 ,437 ,391 ,327 ,326 ,440 ,457 ,438 ,341 ,382 ,362 ,459 ,457 ,461 ,434 ,430 ,394 ,414 ,463 ,362 ,396 ,369 ,262 ,354 ,461 ,457 ,316 ,403 ,402 ,315 ,404 ,403 ,314 ,405 ,404 ,313 ,406 ,405 ,421 ,418 ,406 ,366 ,401 ,361 ,306 ,408 ,407 ,291 ,409 ,408 ,287 ,410 ,409 ,432 ,436 ,410 ,434 ,416 ,411 ,264 ,368 ,383 ,309 ,438 ,457 ,352 ,376 ,401 ,274 ,275 ,4 ,421 ,428 ,262 ,294 ,327 ,358 ,433 ,416 ,367 ,289 ,455 ,439 ,462 ,370 ,326 ,2 ,326 ,370 ,305 ,460 ,455 ,254 ,449 ,448 ,255 ,261 ,446 ,253 ,450 ,449 ,252 ,451 ,450 ,256 ,452 ,451 ,341 ,453 ,452 ,413 ,464 ,463 ,441 ,413 ,414 ,258 ,442 ,441 ,257 ,443 ,442 ,259 ,444 ,443 ,260 ,445 ,444 ,467 ,342 ,445 ,459 ,458 ,250 ,289 ,392 ,290 ,290 ,328 ,460 ,376 ,433 ,435 ,250 ,290 ,392 ,411 ,416 ,433 ,341 ,463 ,464 ,453 ,464 ,465 ,357 ,465 ,412 ,343 ,412 ,399 ,360 ,363 ,440 ,437 ,399 ,456 ,420 ,456 ,363 ,401 ,435 ,288 ,372 ,383 ,353 ,339 ,255 ,249 ,448 ,261 ,255 ,133 ,243 ,190 ,133 ,155 ,112 ,33 ,246 ,247 ,33 ,130 ,25 ,398 ,384 ,286 ,362 ,398 ,414 ,362 ,463 ,341 ,263 ,359 ,467 ,263 ,249 ,255 ,466 ,467 ,260 ,75 ,60 ,166 ,238 ,239 ,79 ,162 ,127 ,139 ,72 ,11 ,37 ,121 ,232 ,120 ,73 ,72 ,39 ,114 ,128 ,47 ,233 ,232 ,128 ,103 ,104 ,67 ,152 ,175 ,148 ,173 ,157 ,155 ,119 ,118 ,101 ,74 ,73 ,40 ,107 ,9 ,108 ,49 ,48 ,131 ,32 ,194 ,211 ,184 ,74 ,185 ,191 ,80 ,183 ,185 ,40 ,186 ,119 ,230 ,118 ,210 ,202 ,214 ,84 ,83 ,17 ,77 ,76 ,146 ,161 ,160 ,30 ,190 ,56 ,173 ,182 ,106 ,194 ,138 ,135 ,192 ,129 ,203 ,98 ,54 ,21 ,68 ,5 ,51 ,4 ,145 ,144 ,23 ,90 ,77 ,91 ,207 ,205 ,187 ,83 ,201 ,18 ,181 ,91 ,182 ,180 ,90 ,181 ,16 ,85 ,17 ,205 ,206 ,36 ,176 ,148 ,140 ,165 ,92 ,39 ,245 ,193 ,244 ,27 ,159 ,28 ,30 ,247 ,161 ,174 ,236 ,196 ,103 ,54 ,104 ,55 ,193 ,8 ,111 ,117 ,31 ,221 ,189 ,55 ,240 ,98 ,99 ,142 ,126 ,100 ,219 ,166 ,218 ,112 ,155 ,26 ,198 ,209 ,131 ,169 ,135 ,150 ,114 ,47 ,217 ,224 ,223 ,53 ,220 ,45 ,134 ,32 ,211 ,140 ,109 ,67 ,108 ,146 ,43 ,91 ,231 ,230 ,120 ,113 ,226 ,247 ,105 ,63 ,52 ,241 ,238 ,242 ,124 ,46 ,156 ,95 ,78 ,96 ,70 ,46 ,63 ,116 ,143 ,227 ,116 ,123 ,111 ,1 ,44 ,19 ,3 ,236 ,51 ,207 ,216 ,205 ,26 ,154 ,22 ,165 ,39 ,167 ,199 ,200 ,208 ,101 ,36 ,100 ,43 ,57 ,202 ,242 ,20 ,99 ,56 ,28 ,157 ,124 ,35 ,113 ,29 ,160 ,27 ,211 ,204 ,210 ,124 ,113 ,46 ,106 ,43 ,204 ,96 ,62 ,77 ,227 ,137 ,116 ,73 ,41 ,72 ,36 ,203 ,142 ,235 ,64 ,240 ,48 ,49 ,64 ,42 ,41 ,74 ,214 ,212 ,207 ,183 ,42 ,184 ,210 ,169 ,211 ,140 ,170 ,176 ,104 ,105 ,69 ,193 ,122 ,168 ,50 ,123 ,187 ,89 ,96 ,90 ,66 ,65 ,107 ,179 ,89 ,180 ,119 ,101 ,120 ,68 ,63 ,104 ,234 ,93 ,227 ,16 ,15 ,85 ,209 ,129 ,49 ,15 ,14 ,86 ,107 ,55 ,9 ,120 ,100 ,121 ,153 ,145 ,22 ,178 ,88 ,179 ,197 ,6 ,196 ,89 ,88 ,96 ,135 ,138 ,136 ,138 ,215 ,172 ,218 ,115 ,219 ,41 ,42 ,81 ,5 ,195 ,51 ,57 ,43 ,61 ,208 ,171 ,199 ,41 ,81 ,38 ,224 ,53 ,225 ,24 ,144 ,110 ,105 ,52 ,66 ,118 ,229 ,117 ,227 ,34 ,234 ,66 ,107 ,69 ,10 ,109 ,151 ,219 ,48 ,235 ,183 ,62 ,191 ,142 ,129 ,126 ,116 ,111 ,143 ,7 ,163 ,246 ,118 ,117 ,50 ,223 ,222 ,52 ,94 ,19 ,141 ,222 ,221 ,65 ,196 ,3 ,197 ,45 ,220 ,44 ,156 ,70 ,139 ,188 ,122 ,245 ,139 ,71 ,162 ,145 ,153 ,159 ,149 ,170 ,150 ,122 ,188 ,196 ,206 ,216 ,92 ,163 ,144 ,161 ,164 ,2 ,167 ,242 ,141 ,241 ,0 ,164 ,37 ,11 ,72 ,12 ,144 ,145 ,160 ,12 ,38 ,13 ,70 ,63 ,71 ,31 ,226 ,111 ,157 ,158 ,154 ,36 ,101 ,205 ,203 ,206 ,165 ,126 ,209 ,217 ,98 ,165 ,97 ,237 ,220 ,218 ,237 ,239 ,241 ,210 ,214 ,169 ,140 ,171 ,32 ,241 ,125 ,237 ,179 ,86 ,178 ,180 ,85 ,179 ,181 ,84 ,180 ,182 ,83 ,181 ,194 ,201 ,182 ,177 ,137 ,132 ,184 ,76 ,183 ,185 ,61 ,184 ,186 ,57 ,185 ,216 ,212 ,186 ,192 ,214 ,187 ,139 ,34 ,156 ,218 ,79 ,237 ,147 ,123 ,177 ,45 ,44 ,4 ,208 ,201 ,32 ,98 ,64 ,129 ,192 ,213 ,138 ,235 ,59 ,219 ,141 ,242 ,97 ,97 ,2 ,141 ,240 ,75 ,235 ,229 ,24 ,228 ,31 ,25 ,226 ,230 ,23 ,229 ,231 ,22 ,230 ,232 ,26 ,231 ,233 ,112 ,232 ,244 ,189 ,243 ,189 ,221 ,190 ,222 ,28 ,221 ,223 ,27 ,222 ,224 ,29 ,223 ,225 ,30 ,224 ,113 ,247 ,225 ,99 ,60 ,240 ,213 ,147 ,215 ,60 ,20 ,166 ,192 ,187 ,213 ,243 ,112 ,244 ,244 ,233 ,245 ,245 ,128 ,188 ,188 ,114 ,174 ,134 ,131 ,220 ,174 ,217 ,236 ,236 ,198 ,134 ,215 ,177 ,58 ,156 ,143 ,124 ,25 ,110 ,7 ,31 ,228 ,25 ,264 ,356 ,368 ,0 ,11 ,267 ,451 ,452 ,349 ,267 ,302 ,269 ,350 ,357 ,277 ,350 ,452 ,357 ,299 ,333 ,297 ,396 ,175 ,377 ,381 ,384 ,382 ,280 ,347 ,330 ,269 ,303 ,270 ,151 ,9 ,337 ,344 ,278 ,360 ,424 ,418 ,431 ,270 ,304 ,409 ,272 ,310 ,407 ,322 ,270 ,410 ,449 ,450 ,347 ,432 ,422 ,434 ,18 ,313 ,17 ,291 ,306 ,375 ,259 ,387 ,260 ,424 ,335 ,418 ,434 ,364 ,416 ,391 ,423 ,327 ,301 ,251 ,298 ,275 ,281 ,4 ,254 ,373 ,253 ,375 ,307 ,321 ,280 ,425 ,411 ,200 ,421 ,18 ,335 ,321 ,406 ,321 ,320 ,405 ,314 ,315 ,17 ,423 ,426 ,266 ,396 ,377 ,369 ,270 ,322 ,269 ,413 ,417 ,464 ,385 ,386 ,258 ,248 ,456 ,419 ,298 ,284 ,333 ,168 ,417 ,8 ,448 ,346 ,261 ,417 ,413 ,285 ,326 ,327 ,328 ,277 ,355 ,329 ,309 ,392 ,438 ,381 ,382 ,256 ,279 ,429 ,360 ,365 ,364 ,379 ,355 ,277 ,437 ,282 ,443 ,283 ,281 ,275 ,363 ,395 ,431 ,369 ,299 ,297 ,337 ,335 ,273 ,321 ,348 ,450 ,349 ,359 ,446 ,467 ,283 ,293 ,282 ,250 ,458 ,462 ,300 ,276 ,383 ,292 ,308 ,325 ,283 ,276 ,293 ,264 ,372 ,447 ,346 ,352 ,340 ,354 ,274 ,19 ,363 ,456 ,281 ,426 ,436 ,425 ,380 ,381 ,252 ,267 ,269 ,393 ,421 ,200 ,428 ,371 ,266 ,329 ,432 ,287 ,422 ,290 ,250 ,328 ,385 ,258 ,384 ,446 ,265 ,342 ,386 ,387 ,257 ,422 ,424 ,430 ,445 ,342 ,276 ,422 ,273 ,424 ,306 ,292 ,307 ,352 ,366 ,345 ,268 ,271 ,302 ,358 ,423 ,371 ,327 ,294 ,460 ,331 ,279 ,294 ,303 ,271 ,304 ,436 ,432 ,427 ,304 ,272 ,408 ,395 ,394 ,431 ,378 ,395 ,400 ,296 ,334 ,299 ,6 ,351 ,168 ,376 ,352 ,411 ,307 ,325 ,320 ,285 ,295 ,336 ,320 ,319 ,404 ,329 ,330 ,349 ,334 ,293 ,333 ,366 ,323 ,447 ,316 ,15 ,315 ,331 ,358 ,279 ,317 ,14 ,316 ,8 ,285 ,9 ,277 ,329 ,350 ,253 ,374 ,252 ,319 ,318 ,403 ,351 ,6 ,419 ,324 ,318 ,325 ,397 ,367 ,365 ,288 ,435 ,397 ,278 ,344 ,439 ,310 ,272 ,311 ,248 ,195 ,281 ,375 ,273 ,291 ,175 ,396 ,199 ,312 ,311 ,268 ,276 ,283 ,445 ,390 ,373 ,339 ,295 ,282 ,296 ,448 ,449 ,346 ,356 ,264 ,454 ,337 ,336 ,299 ,337 ,338 ,151 ,294 ,278 ,455 ,308 ,292 ,415 ,429 ,358 ,355 ,265 ,340 ,372 ,388 ,390 ,466 ,352 ,346 ,280 ,295 ,442 ,282 ,354 ,19 ,370 ,285 ,441 ,295 ,195 ,248 ,197 ,457 ,440 ,274 ,301 ,300 ,368 ,417 ,351 ,465 ,251 ,301 ,389 ,385 ,380 ,386 ,394 ,395 ,379 ,399 ,412 ,419 ,410 ,436 ,322 ,387 ,373 ,388 ,326 ,2 ,393 ,354 ,370 ,461 ,393 ,164 ,267 ,268 ,302 ,12 ,386 ,374 ,387 ,312 ,268 ,13 ,298 ,293 ,301 ,265 ,446 ,340 ,380 ,385 ,381 ,280 ,330 ,425 ,322 ,426 ,391 ,420 ,429 ,437 ,393 ,391 ,326 ,344 ,440 ,438 ,458 ,459 ,461 ,364 ,434 ,394 ,428 ,396 ,262 ,274 ,354 ,457 ,317 ,316 ,402 ,316 ,315 ,403 ,315 ,314 ,404 ,314 ,313 ,405 ,313 ,421 ,406 ,323 ,366 ,361 ,292 ,306 ,407 ,306 ,291 ,408 ,291 ,287 ,409 ,287 ,432 ,410 ,427 ,434 ,411 ,372 ,264 ,383 ,459 ,309 ,457 ,366 ,352 ,401 ,1 ,274 ,4 ,418 ,421 ,262 ,331 ,294 ,358 ,435 ,433 ,367 ,392 ,289 ,439 ,328 ,462 ,326 ,94 ,2 ,370 ,289 ,305 ,455 ,339 ,254 ,448 ,359 ,255 ,446 ,254 ,253 ,449 ,253 ,252 ,450 ,252 ,256 ,451 ,256 ,341 ,452 ,414 ,413 ,463 ,286 ,441 ,414 ,286 ,258 ,441 ,258 ,257 ,442 ,257 ,259 ,443 ,259 ,260 ,444 ,260 ,467 ,445 ,309 ,459 ,250 ,305 ,289 ,290 ,305 ,290 ,460 ,401 ,376 ,435 ,309 ,250 ,392 ,376 ,411 ,433 ,453 ,341 ,464 ,357 ,453 ,465 ,343 ,357 ,412 ,437 ,343 ,399 ,344 ,360 ,440 ,420 ,437 ,456 ,360 ,420 ,363 ,361 ,401 ,288 ,265 ,372 ,353 ,390 ,339 ,249 ,339 ,448 ,255 )#line:194
_OO00OOO0OO0O0OOOO =(10 ,338 ,297 ,332 ,284 ,251 ,389 ,356 ,454 ,323 ,361 ,288 ,397 ,365 ,379 ,378 ,400 ,377 ,152 ,148 ,176 ,149 ,150 ,136 ,172 ,58 ,132 ,93 ,234 ,127 ,162 ,21 ,54 ,103 ,67 ,109 )#line:198
_OO0OO0O0O0OO0O00O =(33 ,7 ,163 ,144 ,145 ,153 ,154 ,155 ,133 ,173 ,157 ,158 ,159 ,160 ,161 ,246 )#line:199
_OO00000OO00OOOO0O =(70 ,63 ,105 ,66 ,107 )#line:200
_OOO00O0O0O0O0O0O0 =(46 ,53 ,52 ,65 ,55 )#line:201
_O0000OOO0OOO0O0O0 =(263 ,249 ,390 ,373 ,374 ,380 ,381 ,382 ,362 ,398 ,384 ,385 ,386 ,387 ,388 ,466 )#line:202
_OOOOOO0OOOO0O00OO =(300 ,293 ,334 ,296 ,336 )#line:203
_O00O0OOOO00OO0000 =(276 ,283 ,282 ,295 ,285 )#line:204
_OOOOO0O00OO0O00O0 =(61 ,185 ,40 ,39 ,37 ,0 ,267 ,269 ,270 ,409 ,291 ,375 ,321 ,405 ,314 ,17 ,84 ,181 ,91 ,146 )#line:205
_OO0OO0O0O0O000000 =(78 ,191 ,80 ,81 ,82 ,13 ,312 ,311 ,310 ,415 ,308 ,324 ,318 ,402 ,317 ,14 ,87 ,178 ,88 ,95 )#line:206
_OOO0OOOO000O0OOO0 ={'left eye':[14 ,15 ,66 ,67 ,266 ,267 ,288 ,289 ,290 ,291 ,306 ,307 ,308 ,309 ,310 ,311 ,314 ,315 ,316 ,317 ,318 ,319 ,320 ,321 ,322 ,323 ,326 ,327 ,346 ,347 ,492 ,493 ],'right eye':[498 ,499 ,526 ,527 ,724 ,725 ,746 ,747 ,748 ,749 ,760 ,761 ,762 ,763 ,764 ,765 ,768 ,769 ,770 ,771 ,772 ,773 ,774 ,775 ,776 ,777 ,780 ,781 ,796 ,797 ,932 ,933 ],'left eyebrow':[92 ,93 ,104 ,105 ,106 ,107 ,110 ,111 ,126 ,127 ,130 ,131 ,132 ,133 ,140 ,141 ,210 ,211 ,214 ,215 ],'right eyebrow':[552 ,553 ,564 ,565 ,566 ,567 ,570 ,571 ,586 ,587 ,590 ,591 ,592 ,593 ,600 ,601 ,668 ,669 ,672 ,673 ],'left cheek':[72 ,73 ,100 ,101 ,202 ,203 ,232 ,233 ,234 ,235 ,236 ,237 ,246 ,247 ,274 ,275 ,294 ,295 ,354 ,355 ,374 ,375 ,384 ,385 ,410 ,411 ,412 ,413 ,414 ,415 ,426 ,427 ,428 ,429 ,432 ,433 ,454 ,455 ],'right cheek':[532 ,533 ,560 ,561 ,660 ,661 ,690 ,691 ,692 ,693 ,694 ,695 ,704 ,705 ,732 ,733 ,752 ,753 ,802 ,803 ,822 ,823 ,832 ,833 ,850 ,851 ,852 ,853 ,854 ,855 ,866 ,867 ,868 ,869 ,872 ,873 ,894 ,895 ],'forehead':[18 ,19 ,20 ,21 ,42 ,43 ,108 ,109 ,134 ,135 ,136 ,137 ,138 ,139 ,142 ,143 ,206 ,207 ,208 ,209 ,216 ,217 ,218 ,219 ,302 ,303 ,502 ,503 ,568 ,569 ,594 ,595 ,596 ,597 ,598 ,599 ,602 ,603 ,664 ,665 ,666 ,667 ,674 ,675 ,676 ,677 ],'nose':[2 ,3 ,4 ,5 ,12 ,13 ,98 ,99 ,128 ,129 ,194 ,195 ,258 ,259 ,392 ,393 ,396 ,397 ,472 ,473 ,480 ,481 ,558 ,559 ,588 ,589 ,652 ,653 ,716 ,717 ,838 ,839 ,840 ,841 ,912 ,913 ,920 ,921 ],'mouth':[0 ,1 ,26 ,27 ,28 ,29 ,34 ,35 ,74 ,75 ,78 ,79 ,80 ,81 ,122 ,123 ,156 ,157 ,160 ,161 ,162 ,163 ,164 ,165 ,168 ,169 ,174 ,175 ,176 ,177 ,182 ,183 ,190 ,191 ,292 ,293 ,356 ,357 ,362 ,363 ,370 ,371 ,382 ,383 ,534 ,535 ,538 ,539 ,540 ,541 ,582 ,583 ,616 ,617 ,620 ,621 ,622 ,623 ,624 ,625 ,628 ,629 ,634 ,635 ,636 ,637 ,642 ,643 ,648 ,649 ,750 ,751 ,804 ,805 ,810 ,811 ,818 ,819 ,830 ,831 ],'others':[3 ,4 ,5 ,8 ,11 ,12 ,15 ,16 ,18 ,19 ,20 ,22 ,23 ,24 ,25 ,26 ,27 ,28 ,29 ,30 ,31 ,32 ,34 ,35 ,38 ,41 ,42 ,43 ,44 ,45 ,47 ,48 ,51 ,56 ,57 ,58 ,59 ,60 ,62 ,72 ,73 ,74 ,75 ,76 ,77 ,79 ,83 ,85 ,86 ,89 ,90 ,92 ,93 ,94 ,96 ,98 ,99 ,100 ,102 ,106 ,110 ,111 ,112 ,113 ,114 ,115 ,119 ,120 ,121 ,122 ,124 ,125 ,126 ,127 ,128 ,130 ,131 ,132 ,134 ,135 ,136 ,138 ,139 ,140 ,141 ,142 ,143 ,148 ,149 ,150 ,152 ,156 ,162 ,164 ,165 ,166 ,167 ,168 ,169 ,170 ,171 ,172 ,174 ,175 ,176 ,179 ,180 ,182 ,183 ,184 ,186 ,188 ,189 ,190 ,193 ,194 ,195 ,197 ,199 ,200 ,201 ,202 ,203 ,204 ,208 ,209 ,210 ,211 ,212 ,215 ,217 ,218 ,219 ,220 ,221 ,222 ,223 ,224 ,225 ,226 ,228 ,229 ,230 ,231 ,232 ,233 ,234 ,235 ,237 ,238 ,239 ,241 ,242 ,243 ,244 ,245 ,247 ,248 ,250 ,252 ,253 ,254 ,255 ,256 ,257 ,258 ,259 ,260 ,261 ,262 ,264 ,265 ,268 ,271 ,272 ,273 ,274 ,275 ,277 ,278 ,281 ,286 ,287 ,288 ,289 ,290 ,292 ,302 ,303 ,304 ,305 ,306 ,307 ,309 ,313 ,315 ,316 ,319 ,320 ,322 ,323 ,325 ,327 ,328 ,329 ,331 ,335 ,339 ,340 ,341 ,342 ,343 ,344 ,348 ,349 ,350 ,351 ,353 ,354 ,355 ,356 ,357 ,359 ,360 ,361 ,363 ,364 ,365 ,367 ,368 ,369 ,370 ,371 ,372 ,377 ,378 ,379 ,383 ,389 ,391 ,392 ,393 ,394 ,395 ,396 ,397 ,399 ,400 ,403 ,404 ,406 ,407 ,408 ,410 ,412 ,413 ,414 ,417 ,418 ,421 ,422 ,423 ,424 ,428 ,429 ,430 ,431 ,432 ,435 ,437 ,438 ,439 ,440 ,441 ,442 ,443 ,444 ,445 ,446 ,448 ,449 ,450 ,451 ,452 ,453 ,454 ,455 ,457 ,458 ,459 ,461 ,462 ,463 ,464 ,465 ,467 ]}#line:218
class FaceMesh :#line:221
    def __init__ (O0OOO000OOOOO0OO0 ):#line:222
        O0OOO000OOOOO0OO0 ._loaded =False #line:223
        O0OOO000OOOOO0OO0 ._clear ()#line:224
    def _clear (OO0OO0OOO000OOOOO ):#line:226
        OO0OO0OOO000OOOOO ._points ={}#line:227
        OO0OO0OOO000OOOOO ._boxes ={}#line:228
        OO0OO0OOO000OOOOO ._widths ={}#line:229
        OO0OO0OOO000OOOOO ._heights ={}#line:230
        OO0OO0OOO000OOOOO ._areas ={}#line:231
        OO0OO0OOO000OOOOO ._landmarks =None #line:232
        OO0OO0OOO000OOOOO ._drawings =None #line:233
    def load_model (O00O00OO0000O0000 ,threshold =0.5 ):#line:235
        try :#line:236
            O00O00OO0000O0000 ._mesh =mp .solutions .face_mesh .FaceMesh (max_num_faces =1 ,min_detection_confidence =threshold ,min_tracking_confidence =0.5 )#line:237
            O00O00OO0000O0000 ._loaded =True #line:238
            return True #line:239
        except :#line:240
            return False #line:241
    def _calc_xyz (O0O0O00OO0O0O0000 ,O00O0O0000O0000OO ,OO0O000O0OO00OO00 ,indices =None ):#line:243
        if indices is None :#line:244
            O0O0O00OO0O0O0000 ._points [O00O0O0000O0000OO ]=np .around (np .mean (OO0O000O0OO00OO00 ,axis =0 )).astype (np .int32 )#line:245
        else :#line:246
            O0O0O00OO0O0O0000 ._points [O00O0O0000O0000OO ]=np .around (np .mean ([OO0O000O0OO00OO00 [OOO00OOO0O0OO0O00 ]for OOO00OOO0O0OO0O00 in indices ],axis =0 )).astype (np .int32 )#line:247
    def _calc_box (OO0OO00000000O00O ,O0OO000O0OO00000O ,O0O000O0OOO0O00OO ,indices =None ):#line:249
        if indices is None :#line:250
            O0O0OO000O00000O0 =np .min (O0O000O0OOO0O00OO ,axis =0 )#line:251
            O0OO00OO0OO000000 =np .max (O0O000O0OOO0O00OO ,axis =0 )#line:252
        else :#line:253
            O000O0O00OO0O00O0 =[O0O000O0OOO0O00OO [O0OOO0O000O00OO00 ]for O0OOO0O000O00OO00 in indices ]#line:254
            O0O0OO000O00000O0 =np .min (O000O0O00OO0O00O0 ,axis =0 )#line:255
            O0OO00OO0OO000000 =np .max (O000O0O00OO0O00O0 ,axis =0 )#line:256
        OO0OO00000000O00O ._boxes [O0OO000O0OO00000O ]=[O0O0OO000O00000O0 [0 ],O0O0OO000O00000O0 [1 ],O0OO00OO0OO000000 [0 ],O0OO00OO0OO000000 [1 ]]#line:257
        OOOO0O0O000OO00O0 =abs (O0OO00OO0OO000000 [0 ]-O0O0OO000O00000O0 [0 ])#line:258
        OO0OO000O00O0O00O =abs (O0OO00OO0OO000000 [1 ]-O0O0OO000O00000O0 [1 ])#line:259
        OO0OO00000000O00O ._widths [O0OO000O0OO00000O ]=OOOO0O0O000OO00O0 #line:260
        OO0OO00000000O00O ._heights [O0OO000O0OO00000O ]=OO0OO000O00O0O00O #line:261
        OO0OO00000000O00O ._areas [O0OO000O0OO00000O ]=OOOO0O0O000OO00O0 *OO0OO000O00O0O00O #line:262
    def detect (OO0OOO000OO000OO0 ,O00OO000OOOO0O000 ):#line:264
        if O00OO000OOOO0O000 is not None and OO0OOO000OO000OO0 ._loaded :#line:265
            O00OO000OOOO0O000 =cv2 .cvtColor (O00OO000OOOO0O000 ,cv2 .COLOR_BGR2RGB )#line:266
            O00OO000OOOO0O000 .flags .writeable =False #line:267
            O00O000O0OOO0OOOO =OO0OOO000OO000OO0 ._mesh .process (O00OO000OOOO0O000 )#line:268
            if O00O000O0OOO0OOOO and O00O000O0OOO0OOOO .multi_face_landmarks and len (O00O000O0OOO0OOOO .multi_face_landmarks )>0 :#line:269
                O0O0OO000O00OOOO0 =O00O000O0OOO0OOOO .multi_face_landmarks [0 ]#line:270
                if len (O0O0OO000O00OOOO0 .landmark )==468 :#line:271
                    O0O0O00O00000O0OO =O00OO000OOOO0O000 .shape [1 ]#line:272
                    O0O0O0OOOOO000OO0 =O00OO000OOOO0O000 .shape [0 ]#line:273
                    OO00000000OOOO000 =[OOO00O00000O0OOOO .x for OOO00O00000O0OOOO in O0O0OO000O00OOOO0 .landmark ]#line:274
                    OOO0O0OOO0OOOO00O =[OOOOO00O0000OOO0O .y for OOOOO00O0000OOO0O in O0O0OO000O00OOOO0 .landmark ]#line:275
                    OO00O0O0OO0O0OO00 =[O0OOO0O0O0OO00000 .z for O0OOO0O0O0OO00000 in O0O0OO000O00OOOO0 .landmark ]#line:276
                    O00OO0OO0OOOO0000 =np .transpose (np .stack ((OO00000000OOOO000 ,OOO0O0OOO0OOOO00O ,OO00O0O0OO0O0OO00 )))*(O0O0O00O00000O0OO ,O0O0O0OOOOO000OO0 ,O0O0O00O00000O0OO )#line:277
                    O00OO0OO0OOOO0000 =O00OO0OO0OOOO0000 .astype (np .int32 )#line:278
                    OO0OOO000OO000OO0 ._landmarks =O00OO0OO0OOOO0000 #line:279
                    OO0OOO000OO000OO0 ._calc_box ('face',O00OO0OO0OOOO0000 )#line:280
                    OO0OOO000OO000OO0 ._calc_box ('left eye',O00OO0OO0OOOO0000 ,_OO0OO0O0O0OO0O00O )#line:281
                    OO0OOO000OO000OO0 ._calc_box ('right eye',O00OO0OO0OOOO0000 ,_O0000OOO0OOO0O0O0 )#line:282
                    OO0OOO000OO000OO0 ._calc_box ('mouth',O00OO0OO0OOOO0000 ,_OOOOO0O00OO0O00O0 )#line:283
                    OO0OOO000OO000OO0 ._calc_xyz ('face',O00OO0OO0OOOO0000 )#line:284
                    OO0OOO000OO000OO0 ._calc_xyz ('left eye',O00OO0OO0OOOO0000 ,_OO0OO0O0O0OO0O00O )#line:285
                    OO0OOO000OO000OO0 ._calc_xyz ('right eye',O00OO0OO0OOOO0000 ,_O0000OOO0OOO0O0O0 )#line:286
                    OO0OOO000OO000OO0 ._calc_xyz ('mouth',O00OO0OO0OOOO0000 ,_OOOOO0O00OO0O00O0 )#line:287
                    O00O00O00O0000OOO =OO0OOO000OO000OO0 ._points #line:288
                    O00O00O00O0000OOO ['nose']=O00OO0OO0OOOO0000 [1 ]#line:289
                    O00O00O00O0000OOO ['lip left']=O00OO0OO0OOOO0000 [61 ]#line:290
                    O00O00O00O0000OOO ['lip right']=O00OO0OO0OOOO0000 [291 ]#line:291
                    O00O00O00O0000OOO ['lip top']=O00OO0OO0OOOO0000 [0 ]#line:292
                    O00O00O00O0000OOO ['lip bottom']=O00OO0OO0OOOO0000 [17 ]#line:293
                    OO0OOO000OO000OO0 ._drawings =O00OO0OO0OOOO0000 [:,:2 ]#line:294
                    return True #line:295
        OO0OOO000OO000OO0 ._clear ()#line:296
        return False #line:297
    def draw_result (OO0O0O0O0OO00O0OO ,O0O000O0O0O00OOOO ,clone =False ):#line:299
        if O0O000O0O0O00OOOO is not None and OO0O0O0O0OO00O0OO ._drawings is not None and OO0O0O0O0OO00O0OO ._drawings .size >0 :#line:300
            if clone :#line:301
                O0O000O0O0O00OOOO =O0O000O0O0O00OOOO .copy ()#line:302
            OO0000O00000O0OOO =OO0O0O0O0OO00O0OO ._drawings #line:303
            OOO0OOOO00OO0O000 =np .array ([[OO0000O00000O0OOO [_OO0000OOO00000OOO [OO000O0OO00OOOOOO *3 ]],OO0000O00000O0OOO [_OO0000OOO00000OOO [OO000O0OO00OOOOOO *3 +1 ]],OO0000O00000O0OOO [_OO0000OOO00000OOO [OO000O0OO00OOOOOO *3 +2 ]]]for OO000O0OO00OOOOOO in range (len (_OO0000OOO00000OOO )//3 )],np .int32 )#line:310
            cv2 .polylines (O0O000O0O0O00OOOO ,OOO0OOOO00OO0O000 ,True ,(192 ,192 ,192 ),1 )#line:311
            OOO0OOOO00OO0O000 =np .array ([OO0000O00000O0OOO [O0O0O000OO00O00OO ]for O0O0O000OO00O00OO in _OO00OOO0OO0O0OOOO ],np .int32 )#line:312
            cv2 .polylines (O0O000O0O0O00OOOO ,[OOO0OOOO00OO0O000 ],True ,(177 ,206 ,251 ),2 )#line:313
            O00OOO00OOO000OO0 =(0 ,255 ,0 )#line:314
            OOO0OOOO00OO0O000 =np .array ([OO0000O00000O0OOO [OO000O0OO0OOOO00O ]for OO000O0OO0OOOO00O in _OO0OO0O0O0OO0O00O ],np .int32 )#line:315
            cv2 .polylines (O0O000O0O0O00OOOO ,[OOO0OOOO00OO0O000 ],True ,O00OOO00OOO000OO0 ,2 )#line:316
            OOO0OOOO00OO0O000 =np .array ([OO0000O00000O0OOO [O00OO000OOOOOO00O ]for O00OO000OOOOOO00O in _OO00000OO00OOOO0O ],np .int32 )#line:317
            cv2 .polylines (O0O000O0O0O00OOOO ,[OOO0OOOO00OO0O000 ],False ,O00OOO00OOO000OO0 ,2 )#line:318
            OOO0OOOO00OO0O000 =np .array ([OO0000O00000O0OOO [OO00OOO00OO00OOOO ]for OO00OOO00OO00OOOO in _OOO00O0O0O0O0O0O0 ],np .int32 )#line:319
            cv2 .polylines (O0O000O0O0O00OOOO ,[OOO0OOOO00OO0O000 ],False ,O00OOO00OOO000OO0 ,2 )#line:320
            O00OOO00OOO000OO0 =(255 ,0 ,0 )#line:321
            OOO0OOOO00OO0O000 =np .array ([OO0000O00000O0OOO [OO0OO00O00O000000 ]for OO0OO00O00O000000 in _O0000OOO0OOO0O0O0 ],np .int32 )#line:322
            cv2 .polylines (O0O000O0O0O00OOOO ,[OOO0OOOO00OO0O000 ],True ,O00OOO00OOO000OO0 ,2 )#line:323
            OOO0OOOO00OO0O000 =np .array ([OO0000O00000O0OOO [O0000OO0OO000OO0O ]for O0000OO0OO000OO0O in _OOOOOO0OOOO0O00OO ],np .int32 )#line:324
            cv2 .polylines (O0O000O0O0O00OOOO ,[OOO0OOOO00OO0O000 ],False ,O00OOO00OOO000OO0 ,2 )#line:325
            OOO0OOOO00OO0O000 =np .array ([OO0000O00000O0OOO [OOOOOOOO0OO0OO000 ]for OOOOOOOO0OO0OO000 in _O00O0OOOO00OO0000 ],np .int32 )#line:326
            cv2 .polylines (O0O000O0O0O00OOOO ,[OOO0OOOO00OO0O000 ],False ,O00OOO00OOO000OO0 ,2 )#line:327
            O00OOO00OOO000OO0 =(0 ,0 ,255 )#line:328
            OOO0OOOO00OO0O000 =np .array ([OO0000O00000O0OOO [O0OOO000OOO0OOO0O ]for O0OOO000OOO0OOO0O in _OOOOO0O00OO0O00O0 ],np .int32 )#line:329
            cv2 .polylines (O0O000O0O0O00OOOO ,[OOO0OOOO00OO0O000 ],True ,O00OOO00OOO000OO0 ,2 )#line:330
            OOO0OOOO00OO0O000 =np .array ([OO0000O00000O0OOO [OO0O0OOOO0OOO0O0O ]for OO0O0OOOO0OOO0O0O in _OO0OO0O0O0O000000 ],np .int32 )#line:331
            cv2 .polylines (O0O000O0O0O00OOOO ,[OOO0OOOO00OO0O000 ],True ,O00OOO00OOO000OO0 ,2 )#line:332
        return O0O000O0O0O00OOOO #line:333
    def get_xy (O000000O0O0OO0OOO ,id ='all'):#line:335
        O00O0O000000O0000 =O000000O0O0OO0OOO .get_xyz (id )#line:336
        if O00O0O000000O0000 is None :return None #line:337
        if O00O0O000000O0000 .ndim ==1 :#line:338
            return O00O0O000000O0000 [:2 ]#line:339
        elif O00O0O000000O0000 .ndim ==2 :#line:340
            return O00O0O000000O0000 [:,:2 ]#line:341
        return None #line:342
    def get_xyz (O0O00OO00O0O000O0 ,id ='all'):#line:344
        if isinstance (id ,(int ,float )):#line:345
            id =int (id )#line:346
            if id <0 or id >467 :return None #line:347
            if O0O00OO00O0O000O0 ._landmarks is None :return None #line:348
            return O0O00OO00O0O000O0 ._landmarks [id ]#line:349
        elif isinstance (id ,str ):#line:350
            id =id .lower ()#line:351
            if id =='all':#line:352
                return O0O00OO00O0O000O0 ._landmarks #line:353
            elif id in O0O00OO00O0O000O0 ._points :#line:354
                return O0O00OO00O0O000O0 ._points [id ]#line:355
        return None #line:356
    def get_box (O00O0OOO00OO0OO0O ,id ='all'):#line:358
        if isinstance (id ,str ):#line:359
            id =id .lower ()#line:360
            if id =='all':#line:361
                return O00O0OOO00OO0OO0O ._boxes #line:362
            elif id in O00O0OOO00OO0OO0O ._boxes :#line:363
                return O00O0OOO00OO0OO0O ._boxes [id ]#line:364
        return None #line:365
    def get_width (OOO00OOOO0OOO00O0 ,id ='all'):#line:367
        if isinstance (id ,str ):#line:368
            id =id .lower ()#line:369
            if id =='all':#line:370
                return OOO00OOOO0OOO00O0 ._widths #line:371
            elif id in OOO00OOOO0OOO00O0 ._widths :#line:372
                return OOO00OOOO0OOO00O0 ._widths [id ]#line:373
        return 0 #line:374
    def get_height (OOO0O0O00000OO0O0 ,id ='all'):#line:376
        if isinstance (id ,str ):#line:377
            id =id .lower ()#line:378
            if id =='all':#line:379
                return OOO0O0O00000OO0O0 ._heights #line:380
            elif id in OOO0O0O00000OO0O0 ._heights :#line:381
                return OOO0O0O00000OO0O0 ._heights [id ]#line:382
        return 0 #line:383
    def get_area (OOO0OOO000O0OOO00 ,id ='all'):#line:385
        if isinstance (id ,str ):#line:386
            id =id .lower ()#line:387
            if id =='all':#line:388
                return OOO0OOO000O0OOO00 ._areas #line:389
            elif id in OOO0OOO000O0OOO00 ._areas :#line:390
                return OOO0OOO000O0OOO00 ._areas [id ]#line:391
        return 0 #line:392
    def get_orientation (OO00OOO0OO00O0O0O ,degree =False ):#line:394
        OOOO00OO00O0000OO =OO00OOO0OO00O0O0O .get_xyz ('left eye')#line:395
        OOOOO000000OO0OO0 =OO00OOO0OO00O0O0O .get_xyz ('right eye')#line:396
        if degree :#line:397
            return Util .degree (OOOO00OO00O0000OO ,OOOOO000000OO0OO0 )#line:398
        else :#line:399
            return Util .radian (OOOO00OO00O0000OO ,OOOOO000000OO0OO0 )#line:400
    def get_feature (OOO0000OOO0O0OOO0 ,filter ='all'):#line:402
        OO00O0O000OO00OO0 =OOO0000OOO0O0OOO0 .get_width ('face')#line:403
        OO0O00000O0O0OOO0 =OOO0000OOO0O0OOO0 .get_height ('face')#line:404
        O00OO0OOO00O0O000 =[OO00O0O000OO00OO0 ,OO0O00000O0O0OOO0 ]#line:405
        if OO00O0O000OO00OO0 >0 and OO0O00000O0O0OOO0 >0 :#line:406
            O000OOO0O00OO0O0O =OOO0000OOO0O0OOO0 ._landmarks #line:407
            if O000OOO0O00OO0O0O is not None :#line:408
                O0O000O00O0O0O000 =OOO0000OOO0O0OOO0 .get_xy ('face')#line:409
                O000OOO0O00OO0O0O =(O000OOO0O00OO0O0O [:,:2 ]-O0O000O00O0O0O000 )/O00OO0OOO00O0O000 #line:410
                O0000O00O00OO00OO =O000OOO0O00OO0O0O .reshape (-1 )#line:411
                if isinstance (filter ,str ):#line:412
                    filter =filter .lower ()#line:413
                    if filter =='all':#line:414
                        return O0000O00O00OO00OO #line:415
                    elif filter in _OOO0OOOO000O0OOO0 :#line:416
                        O00000OO0000OOO00 =_OOO0OOOO000O0OOO0 [filter ]#line:417
                        return np .array ([O0000O00O00OO00OO [OO00000OOO0OO0O00 ]for OO00000OOO0OO0O00 in O00000OO0000OOO00 ])#line:418
                elif isinstance (filter ,(list ,tuple )):#line:419
                    O00000OO0000OOO00 =[]#line:420
                    for O0OO0O00000OOO000 in filter :#line:421
                        if O0OO0O00000OOO000 in _OOO0OOOO000O0OOO0 :#line:422
                            O00000OO0000OOO00 .extend (_OOO0OOOO000O0OOO0 [O0OO0O00000OOO000 ])#line:423
                    return np .array ([O0000O00O00OO00OO [OOOOO0OO0O0OOOOOO ]for OOOOO0OO0O0OOOOOO in O00000OO0000OOO00 ])#line:424
        return None #line:425
    def _get_feature_label (O0000OO0OO000OOO0 ,filter ='all'):#line:427
        if isinstance (filter ,str ):#line:428
            filter =filter .lower ()#line:429
            if filter =='all':#line:430
                return ['f'+str (OOO000OOO0O0OO000 )for OOO000OOO0O0OO000 in range (468 )]#line:431
            elif filter in _OOO0OOOO000O0OOO0 :#line:432
                O0O0O00OOO00O0OO0 =_OOO0OOOO000O0OOO0 [filter ]#line:433
                return ['f'+str (OOOOOOO0O0OOO0O00 )for OOOOOOO0O0OOO0O00 in O0O0O00OOO00O0OO0 ]#line:434
        elif isinstance (filter ,(list ,tuple )):#line:435
            O0O0O00OOO00O0OO0 =[]#line:436
            for O0OOO00O0O00O0O00 in filter :#line:437
                if O0OOO00O0O00O0O00 in _OOO0OOOO000O0OOO0 :#line:438
                    O0O0O00OOO00O0OO0 .extend (_OOO0OOOO000O0OOO0 [O0OOO00O0O00O0O00 ])#line:439
            return ['f'+str (O0OOO000000OOO00O )for O0OOO000000OOO00O in O0O0O00OOO00O0OO0 ]#line:440
    def record_feature (O00O0O0O0O0OO0OOO ,OOOOO0OOO00OOOO0O ,OO00O0000000O0OOO ,filter ='all',interval_msec =100 ,frames =20 ,countdown =3 ):#line:442
        if countdown >0 :#line:443
            OOOOO0OOO00OOOO0O .count_down (countdown )#line:444
        O000O0O0O0OOOO0OO =0 #line:445
        O0OOOOOO0O0OO0O00 =timer ()#line:446
        O000O0O0OO0O00O0O =','.join (O00O0O0O0O0OO0OOO ._get_feature_label (filter ))#line:447
        O0O000O00OOO0O00O =[]#line:448
        while True :#line:449
            if O000O0O0O0OOOO0OO >=frames :break #line:450
            O0OOO0O0O0O000OO0 =OOOOO0OOO00OOOO0O .read ()#line:451
            if O00O0O0O0O0OO0OOO .detect (O0OOO0O0O0O000OO0 ):#line:452
                O0OOO0O0O0O000OO0 =O00O0O0O0O0OO0OOO .draw_result (O0OOO0O0O0O000OO0 )#line:453
                if timer ()>O0OOOOOO0O0OO0O00 :#line:454
                    O0O000O00OOO0O00O .append (O00O0O0O0O0OO0OOO .get_feature (filter ))#line:455
                    O000O0O0O0OOOO0OO +=1 #line:456
                    print ('saved',O000O0O0O0OOOO0OO )#line:457
                    O0OOOOOO0O0OO0O00 +=interval_msec /1000.0 #line:458
                if OOOOO0OOO00OOOO0O .check_key ()=='esc':#line:459
                    return #line:460
            OOOOO0OOO00OOOO0O .show (O0OOO0O0O0O000OO0 )#line:461
        if OO00O0000000O0OOO is not None :#line:462
            Util .realize_filepath (OO00O0000000O0OOO )#line:463
            np .savetxt (OO00O0000000O0OOO ,O0O000O00OOO0O00O ,fmt ='%f',delimiter =',',header =O000O0O0OO0O00O0O ,comments ='')#line:464
    @staticmethod #line:466
    def distance (O00OOOOO00O00OO0O ,O0OO0O0O00000OO00 ):#line:467
        return Util .distance (O00OOOOO00O00OO0O ,O0OO0O0O00000OO00 )#line:468
    @staticmethod #line:470
    def degree (O000O0O000O0OOOO0 ,OOO0O0O00OOO0000O ):#line:471
        return Util .degree (O000O0O000O0OOOO0 ,OOO0O0O00OOO0000O )#line:472
    @staticmethod #line:474
    def radian (OO0O0O0O00O0OOO0O ,O0OOO0O0O0O00OO0O ):#line:475
        return Util .radian (OO0O0O0O00O0OOO0O ,O0OOO0O0O0O00OO0O )#line:476
