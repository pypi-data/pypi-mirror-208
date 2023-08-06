 #
 # Based on "191227" sketch.
 # see https://openprocessing.org/sketch/816453
 #
 
catch {console show}

set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

set auto_path [linsert $auto_path 0 [file join $thisDir lib]]
tcl::tm::path add [file join $thisDir lib]

package require Spline
package require perlin
  
package require Blend2d

	#
	# -- some math functions -----------------------------------------
	#
	proc tcl::mathfunc::clamp {v a b} { expr {$v<$a ? $a : ($v<$b ? $v :$b)} }
	
	proc tcl::mathfunc::map {x a0 a1 b0 b1} { expr {(double($x)-$a0)*($b1-$b0)/($a1-$a0)+$b0} }
	
	proc tcl::mathfunc::random {a b} { expr {rand()*($b-$a)+$a} }

	proc tcl::mathfunc::random_item {items} { lindex $items [expr {int(rand()*[llength $items])}] }

# occho il mio perlin e' -1 1 va mappato
	proc tcl::mathfunc::noise {x} { expr {map([perlin $x 0.1 0.1],-1,1,0,1)} }

	set PI [expr {acos(-1.0)}]


proc Draw {sfc W H frameCount} {
$sfc push
	$sfc clear -compop SRC_OVER -style 0xFFFFFFFF
	
	$sfc configure -compop MULTIPLY

	$sfc configure -fill.style 0xFF0960F0	
	DrawLiquidBlob $sfc $frameCount $W $H 18 50 20 100

	$sfc configure -fill.style 0xFFF0F000		
	DrawLiquidBlob $sfc $frameCount $W $H 15 60 25 120

	$sfc configure -fill.style 0xFFF000F0		
	DrawLiquidBlob $sfc $frameCount $W $H 12 45 15 150
$sfc pop
}

# vNim il numrero di 'vertici'
# fcm  da' la velocita' di rotazione ( puo' anche essere negativa)?
proc DrawLiquidBlob { sfc frameCount W H vNum nm sm fcm } {
	global PI
	
$sfc push
	set M [$sfc cget -matrix]
	set frameCount [expr {double($frameCount)}]
	$sfc configure -matrix [Mtx::rotate $M [expr {$frameCount/$fcm}] radians]
	
	set controlPoints {}
	set dr [expr {2*$PI/$vNum}]
	for {set i 0} {$i<$vNum} {incr i} {
		set beta [expr {$dr*$i}]
		set r [expr {$H*(0.3 + noise($frameCount/$nm+$i)*0.1 + sin($frameCount/$sm+$i)*0.05) }]

		lappend controlPoints [list [expr {$r*cos($beta)}] [expr {$r*sin($beta)}]]
	}

	set spline [Spline new $controlPoints]
	$spline loop true	
	 # compute cubics
	set cubicsPoints [lassign [$spline extended_cubics] P1]
	$spline destroy
	
	set gSpline [BL::Path new]	
	$gSpline moveTo $P1
	foreach {P1 P2 P3} $cubicsPoints {
		$gSpline cubicTo $P1 $P2 $P3
	}
	
	$sfc fill $gSpline
	$gSpline destroy
$sfc pop
}


# ---  main -----

set WIDTH 600
set HEIGHT $WIDTH

wm title . "TclTk binding for Blend2d - Sketch 816453"
set sfc [image create blend2d -format [list $HEIGHT $WIDTH]]
label .sfc -image $sfc ; pack .sfc
label .statusBar -anchor center; pack .statusBar -fill x
	
 # place the origin at the center of the surface
set M [Mtx::translation [expr {$WIDTH/2.0}] [expr {$HEIGHT/2.0}]]
$sfc configure -matrix $M

proc DrawLoop {sfc W H {frameCount 0}} {
	Draw $sfc $W $H $frameCount
	after 20 DrawLoop  $sfc $W $H [incr frameCount]
}

DrawLoop $sfc $WIDTH $HEIGHT
