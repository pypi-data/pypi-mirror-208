set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]
# --sample01 - demo

package require Blend2d
set sfc [image create blend2d -format {480 480} ]
label .x -image $sfc ; pack .x

$sfc clear

set gpath [BL::Path new]
$gpath moveTo {26 31}
$gpath cubicTo {642  132}  {587  -136}  {25  464}
$gpath cubicTo {882  404}  {144  267}  {27  31}

$sfc fill $gpath -fill.style 0xFFFFFFFF

$gpath destroy

