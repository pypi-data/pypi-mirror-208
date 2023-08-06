from tkfly.blend2d.demos import run_eval


run_eval("""
set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

set sfc [image create blend2d -format {480 480} ]
label .x -image $sfc ; pack .x

$sfc clear

set glinear [BL::gradient LINEAR {0 0 0 480} {0.0 0xFFFFFFFF  1.0 0xFF1F7FFF}]

set gpath [BL::Path new]
$gpath moveTo {119 49}
$gpath cubicTo {259 29} {99 279} {275 267}
$gpath cubicTo {537 245} {300 -170} {274 430}


$sfc configure -stroke.style $glinear \
    -stroke.width 15 \
    -stroke.cap {ROUND BUTT}
$sfc stroke $gpath -compop SRC_OVER
$gpath destroy
""")
