set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname [file dirname $thisDir]]]

#
# Blend2d - Tiger demo
#

package require Blend2d 

 # load the tiger-data - result is a big list named TigetData
set thisDir [file dirname [file normalize [info script]]]
source $thisDir/tiger-data.tcl
             
 # precompute paths:
 # for each path, change the geom attribute from a (simplyfied) SVG spec, to BL::Path objects.
 proc precomputePaths {data} {
	set newData {}
	foreach path $data {
		set geom [dict get $path geom]
		set blPath [BL::Path new]
		foreach {cmd coords} $geom {			
			switch -- $cmd {
			 "M" -
			 "L" { 
				lassign $coords x y
				if { $cmd eq "M" } { 
			 		$blPath moveTo $coords
				} else {
			 		$blPath lineTo $coords				
				} 
			 }
			 "C" {
			 	set PP {}
			 	foreach {x y} $coords {
					lappend PP [list $x $y] 
				 }
			 	$blPath cubicTo {*}$PP 
				}
			 "Z" { $blPath close }		 
			}
		}
		$blPath shrink
		dict set path geom $blPath
	
		lappend newData $path
	}
	return $newData
}

 # return the box as {x y dx dy}
 # data should be a list of 'paths' with the "geom" attribute alread coverted to a BL::Path
proc precomputeBbox {data} {
	set xmin 1e20
	set xmax -1e20
	set ymin 1e20
	set ymax -1e20

	foreach path $data {
		set blPath [dict get $path geom]
		lassign [$blPath bbox] x0 y0 x1 y1
		if { $x0 < $xmin } { set xmin $x0 }
		if { $x1 > $xmax } { set xmax $x1 }			
		if { $y0 < $ymin } { set ymin $y0 }
		if { $y1 > $ymax } { set ymax $y1 }			
	}
	return [list $xmin $ymin [expr {$xmax-$xmin}] [expr {$ymax-$ymin}]]
}

# Paint
# parameters:
#   data : the precomputed .. paths ..
#   dataRect : the bounding box of all geometries in data ( as {x y dx dy}  )
#   SFC      : the BL::Surface
#   WIDTH HEIGHT : the window size (i.e. the Surface size)
#   ZOOM        ZOOM is relative to the window (i.e. ZOOM 0.5 -> half window size)
#   ANGLE        ANGLE in degrees
proc Paint {data dataRect SFC WIDTH HEIGHT ZOOM ANGLE} {	
	$SFC clear -style 0xFF00007F
	
	lassign $dataRect tx ty tdx tdy	   
	
	set s [expr {min( $WIDTH/$tdx , $HEIGHT/$tdy) * $ZOOM}]    

	# collimate the center of the tiger with the center of the window
	set tcx [expr {$tx+$tdx/2.0}]
	set tcy [expr {$ty+$tdy/2.0}]
	set wcx [expr {$WIDTH/2.0}]
	set wcy [expr {$HEIGHT/2.0}]
	set M [Mtx::translation [expr {$wcx-$tcx}] [expr {$wcy-$tcy}]]

	set M [Mtx::MxM $M [Mtx::scale $s $s [list $wcx $wcy]]]
	set M [Mtx::MxM $M [Mtx::rotation $ANGLE degrees [list $wcx $wcy]]]

	$SFC push

		 # NOTE: set the transform matrix *before* setting the fill.style / stroke.style
	$SFC configure -matrix $M
	foreach path $data {
		set fillrule [dict get $path "fill"]
		if { $fillrule ne "NONE" } {
			$SFC fill [dict get $path "geom"] \
				-fill.rule $fillrule \
				-fill.style [dict get $path "fillColor"] 
		}

		if { [dict get $path "stroke"] } {
		   # currently a cached strokedpath is not supported ...
		   # a strokedpath is a countour that will be FILLED (instead of STROKED)
		   $SFC configure \
		   	-stroke.style [dict get $path "strokeColor"] \
		   	-stroke.cap [dict get $path "strokeCap"] \
			-stroke.join [dict get $path "strokeJoin"] \
			-stroke.miterlimit [dict get $path "strokeMiterLimit"] \
			-stroke.width [dict get $path "strokeWidth"] 	
		   $SFC stroke [dict get $path "geom"]
		}
	}		
	$SFC pop
}	

proc ttkScaleWithLabel {w -label labelTxt args} {
	frame $w
	label $w.label -text $labelTxt
	ttk::scale $w.scale {*}$args
	pack $w.label $w.scale
}



# == MAIN =====
wm title . "\"Blend2d\" high performance 2D vector graphics engine - TclTk bindings"

set TigerData [precomputePaths $TigerData]
set TigerRect [precomputeBbox $TigerData]

set ANGLE 0.0  ;# degrees
set ZOOM 1.0

set WIDTH  500
set HEIGHT 500


set SFC [image create blend2d -format [list $WIDTH $HEIGHT]]

             
proc doPaint {args} {
	 # ignore any arg  (added by trace or by widgets callbacks..)
	global TigerData
	global TigerRect
	global SFC
	global WIDTH
	global HEIGHT
	global ZOOM
	global ANGLE
	Paint $TigerData $TigerRect $SFC $WIDTH $HEIGHT $ZOOM $ANGLE
}

 # WARNING: remove any decoration from the container, or the <Configure> handler will resize the image indefinitely !
label .cvs -image $SFC -borderwidth 0 -padx 0 -pady 0
frame .controls

.controls configure  -width 200 -pady 20 -padx 10
pack .controls -side left -expand 0 -fill y
pack propagate .controls false

pack .cvs -expand 1 -fill both


 # these scale-widgets simply the global vars ANGLE and ZOOM;
 # These variable are traced, so that each change will trigger a doPaint
ttkScaleWithLabel .controls.rotate -label Rotate -from 0 -to 360 -orient horizontal -variable ANGLE
ttkScaleWithLabel .controls.zoom   -label Zoom   -from 0.1 -to 8.0 -orient horizontal -variable ZOOM
foreach w [winfo children .controls] {
	pack $w
}

trace variable ANGLE w doPaint
trace variable ZOOM  w doPaint

doPaint

bind .cvs <Configure> {
	set w %w
	set h %h
	if { $w != $WIDTH || $h != $HEIGHT } {
		set WIDTH $w
		set HEIGHT $h
		$SFC configure -format [list $WIDTH $HEIGHT]
		doPaint
	}
}
