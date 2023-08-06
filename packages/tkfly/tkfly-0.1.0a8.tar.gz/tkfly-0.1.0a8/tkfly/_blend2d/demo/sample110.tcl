 #
 # Based on "748916" sketch.
 # see https://openprocessing.org/sketch/748916
 #     based on: https://observablehq.com/@rreusser/instanced-webgl-circles
 #
 
catch { console show }

set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

set auto_path [linsert $auto_path 0 [file join $thisDir lib]]
tcl::tm::path add [file join $thisDir lib]

package require Blend2d
package require IKscale

	#
	# -- some math functions -----------------------------------------
	#
	proc tcl::mathfunc::map {x a0 a1 b0 b1} { expr {(double($x)-$a0)*($b1-$b0)/($a1-$a0)+$b0} }	
	set PI [expr {acos(-1.0)}]
	set TWO_PI [expr {2*$PI}]

proc getColorByTheta {theta shapeCnt time} {
	global PI
	global G
# strange armonic distortion ...
	set th [expr {8.0 * $theta + $time * 2.0}]
	
	set r [expr {int(255*(0.6 + 0.4 * cos($th)))}] 
    set g [expr {int(255*(0.6 + 0.4 * cos($th - $PI / 3)))}] 
    set b [expr {int(255*(0.6 + 0.4 * cos($th - $PI * 2.0 / 3.0)))}] 
    set a [expr {int(map($shapeCnt, $G(MIN_SHAPE_CNT), $G(MAX_SHAPE_CNT), 150, 30))}]
	return [format "0x%02x%02x%02x%02x" $a $r $g $b]
}

 # rebuild G(shape) as a polygon with n sides inscribed in a circle of radius 1
 #  if n > 8  then build a circle.
proc rebuildShape	{n} {
	global TWO_PI
	global G		
	$G(shape) reset
	if {$n > 8} {
		 # create a circle (radius 1.0)
		$G(shape) add [BL::circle {0 0} 1.0]
	} else {
		 # create o polygon with n sides (within a circle with radius 1.0)
		set dTheta [expr {$TWO_PI/$n}]
		set theta 0.0
		$G(shape) moveTo {1.0 0.0}
		for {set i 1} {$i<$n} {incr i} {
			set theta [expr {$theta+$dTheta}]
			$G(shape) lineTo [list [expr {cos($theta)}] [expr {sin($theta)}]]
		}
		$G(shape) close
	}
} 

proc Draw {sfc shape shapeCnt frameCount} {
	global TWO_PI
	
	set time [expr {$frameCount/20.0}]
		set scale 300
			
	set dTheta [expr {$TWO_PI/$shapeCnt}]
	set theta 0.0
$sfc push	
	for {set ci 0; set theta 0.0} {$ci<$shapeCnt} {incr ci; set theta [expr {$theta+$dTheta}]} {
		 #
		 # shape is placed centered at  (r0*cos(theta), r0*sin(theta))
		 #  it is scaled zoom times		 
		 #
		 # r0   (based on theta and time)     0.6 +/- 0.2
		 # zoom (based on theta and time)     0.2 +/- 0.12
		set r0 [expr {0.6+0.2*cos($theta * 6.0 + cos($theta * 8.0 + $time))}]
		set r0 [expr {$scale*$r0}]
		set zoom [expr {0.2 + 0.12 * cos($theta * 9.0 - $time * 2.0)}]
		set zoom [expr {$scale*$zoom}]
		set hexColor [getColorByTheta $theta $shapeCnt $time]	

		 # ugly .. you should get the original matrix and then add the (xc,yc) translation and zoom
		set xc [expr {$::G(WIDTH)/2 +$r0*cos($theta)}]		
		set yc [expr {$::G(HEIGHT)/2+$r0*sin($theta)}]

		$sfc configure \
			-matrix [list $zoom 0 0 $zoom $xc $yc] \
			-stroke.style $hexColor	
		$sfc stroke $shape
	}
$sfc pop
}

# ---  main -----

set G(WIDTH) 700
set G(HEIGHT) $G(WIDTH)

set G(MAX_SHAPE_CNT)  2000
set G(MIN_SHAPE_CNT)   200 
set G(MAX_VERTEX_CNT)   10
set G(MIN_VERTEX_CNT)    3


wm title . "TclTk binding for Blend2d - Sketch 748916"
set sfc [image create blend2d -format [list $G(HEIGHT) $G(WIDTH)]]
label .sfc -image $sfc ; pack .sfc
label .statusBar -anchor center; pack .statusBar -fill x

IKscale .vertexControl -from $G(MIN_VERTEX_CNT) -to $G(MAX_VERTEX_CNT) \
	-labelside right \
	-command rebuildShape

IKscale .nOfShapes -from $G(MIN_SHAPE_CNT) -to $G(MAX_SHAPE_CNT) \
	-labelside right \
	-variable G(shapeCnt)
set G(shapeCnt) $G(MIN_SHAPE_CNT)

pack .vertexControl .nOfShapes
	
 # place the origin at the center of the surface
set M [Mtx::translation [expr {$G(WIDTH)/2.0}] [expr {$G(HEIGHT)/2.0}]]
$sfc configure -matrix $M

 # this is required for NOT scaling the stroke-width. 
$sfc configure -stroke.transformorder BEFORE

proc DrawLoop {sfc shape shapeCnt {frameCount 0}} {
	global G
	$sfc clear
	Draw $sfc $shape $shapeCnt $frameCount
	after 1 DrawLoop  $sfc $G(shape) $G(shapeCnt) [incr frameCount]
}

set G(shape) [BL::Path new]
rebuildShape [.nOfShapes get]
DrawLoop $sfc $G(shape) $G(shapeCnt)
