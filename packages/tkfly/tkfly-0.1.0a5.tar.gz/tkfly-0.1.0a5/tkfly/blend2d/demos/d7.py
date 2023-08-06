from tkfly.blend2d.demos import run_eval


run_eval("""
set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

set sfc [image create blend2d -format {480 480} ]
label .x -image $sfc ; pack .x

$sfc clear
set fontFace [BL::FontFace new "$thisDir/Road_Rage.otf"]
set font [BL::Font new $fontFace 50.0]
$sfc configure -fill.style [BL::color gray90] 
$sfc fill [BL::text {60 80} $font "Hello Blend2D"]

$sfc fill [BL::text {150 80} $font "Rotated Text"] -matrix [Mtx::rotation 45 degrees]

set smallFont [BL::Font new $fontFace 12.0]
$sfc fill [BL::text {200 460} $smallFont {Font: "Road Rage" by Youssef Habchi}]

$font destroy
$smallFont destroy
$fontFace destroy
""")

