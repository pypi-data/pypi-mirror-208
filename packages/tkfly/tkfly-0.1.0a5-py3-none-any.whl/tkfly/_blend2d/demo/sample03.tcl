set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

# --sample03 - demo

package require Blend2d

set sfc [image create blend2d -format {480 480} ]
label .x -image $sfc ; pack .x

$sfc clear

set pattern [BL::pattern $thisDir/texture.jpeg]
$sfc fill [BL::roundrect 40 40 400 400 45.5]  -fill.style $pattern -compop SRC_OVER
