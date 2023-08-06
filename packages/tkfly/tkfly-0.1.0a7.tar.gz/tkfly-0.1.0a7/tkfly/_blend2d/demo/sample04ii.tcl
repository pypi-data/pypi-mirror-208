set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

# --sample04ii - demo

package require Blend2d

 # Note that we are going to paint the surface-image only;
 # all the attached widget will be repainted 
proc SfcPaint {sfc dummy} {
	global ANGLE
	global ZOOM	
	global pattern

	$sfc clear -style 0xFF000000  -compop SRC_COPY
	
   # Rotate and zoom around a point at [240, 240].
	set C {240 240}
	set M [Mtx::rotation $ANGLE degrees $C]  
	set M [Mtx::MxM [Mtx::scale $ZOOM $ZOOM  $C] $M ]	
	
	 # BE CAREFUL with blend2d 0.0.1:  the order of options is important
	 # You should set -matrix before setting -style,
	 #  or the texture won't be rotated!
	$sfc fill [BL::roundrect 50 50 380 380 80.5] -matrix $M -style $pattern -compop SRC_OVER
}

# ===  setup the GUI ==========================================================

set sfc [image create blend2d -format {480 480}]
set pattern [BL::pattern $thisDir/texture.jpeg]

 # create a label-widget embedding this blend2d image
label .sfc -image $sfc
pack .sfc

set ANGLE 0.0
set ZOOM 1.0
scale .srot -from 0 -to 360 -orient horizontal -label Rotate -variable ANGLE -command [list SfcPaint $sfc]
scale .szoom -from 0.1 -to 4.0 -resolution 0.1 -orient horizontal -label Zoom -variable ZOOM -command [list SfcPaint $sfc]
pack .srot .szoom -side left -expand 1

 # create another window with a label-widget using the same blend2d image
toplevel .dup; label .dup.sfc -image $sfc
pack .dup.sfc

 #arrange the toplevels side by side
update
set X 200
set Y 50
wm geometry . +$X+$Y
incr X [winfo width .]
wm geometry .dup +$X+$Y

SfcPaint $sfc dummy
 