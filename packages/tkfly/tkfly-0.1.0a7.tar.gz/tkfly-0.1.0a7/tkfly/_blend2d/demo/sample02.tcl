set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

# --sample02 - demo

package require Blend2d

set sfc [image create blend2d -format {480 480} ]
label .x -image $sfc ; pack .x

$sfc clear

set gradient [BL::gradient LINEAR {0 0 0 480} {0.0 0xFFFFFFFF   0.5 0xFF5FAFDF  1.0  0xFF2F5FDF}]
$sfc fill [BL::roundrect 40 40 400 400 45.5] -fill.style $gradient  -compop SRC_OVER
