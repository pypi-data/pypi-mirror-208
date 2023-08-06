from tkfly.blend2d.demos import run_eval


run_eval("""
set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

set sfc [image create blend2d -format {480 480} ]
label .x -image $sfc ; pack .x
ttk::scale .sc -from 0 -to 360 -orient horizontal -command Paint
pack .sc

proc Paint {angle} {
	global sfc
	global pattern

	$sfc fill all -fill.style [BL::color orange] -compop SRC_COPY
	
	$sfc configure -matrix [Mtx::rotation $angle degrees {240 240}]
  
	$sfc fill [BL::roundrect 50 50 380 380 80.5] -fill.style $pattern  -compop SRC_OVER
}

proc PaintInit {} {
	global sfc

	$sfc fill all -fill.style 0xFF0000FF -compop SRC_COPY
}

set pattern [BL::pattern $thisDir/texture.jpeg]
PaintInit
Paint [.sc get]
""")
