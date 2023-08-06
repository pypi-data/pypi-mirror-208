from tkfly.blend2d.demos import run_eval


run_eval("""
set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

set sfc [image create blend2d -format {480 480} ]
label .x -image $sfc ; pack .x


$sfc clear

set grad1 [BL::gradient RADIAL {180 180 180 180 180} {0.0 0xFFFFFFFF  1.0 0xFFFF6f3F}]
$sfc fill [BL::circle {180 180} 160] -style $grad1 -compop SRC_OVER

set grad2 [BL::gradient LINEAR {195 195 470 470} {0.0 0xFFFFFFFF  1.0 0xFF3F9FFF}]
$sfc fill [BL::roundrect 195 195 270 270 25] -style $grad2 -compop DIFFERENCE
""")
