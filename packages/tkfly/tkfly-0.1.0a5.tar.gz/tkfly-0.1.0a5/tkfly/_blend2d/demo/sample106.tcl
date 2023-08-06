 #
 # Porting of the "Electric Sphere" sketch.
 # see https://openprocessing.org/sketch/432335
 #
  
set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

package require Blend2d

package require math::statistics
namespace import math::statistics::random-normal
set PI [expr {acos(-1.0)}]


 # return two points on a circle of radius R.
 # First point is placed 'around' beta=0   (with a stddev of PI/4)
 # Second point is placed at the same angle PLUS a random beta (with stddev of PI/3)  
 # These two values are the magic generationg the illumination effect
 # and the illusion of the curvature of the sphere ! 
proc circlePoints {R} {
	variable PI
	set th1 [random-normal 0 [expr {$PI/4.0}] 1]
	set th2 [expr {$th1 + [random-normal 0 [expr {$PI/3.0}] 1]}]
	return [list \
		[list [expr {$R*cos($th1)}] [expr {$R*sin($th1)}]] \
		[list [expr {$R*cos($th2)}] [expr {$R*sin($th2)}]] \
	]
}


proc midPoint {A B} {
	set M {}
	foreach a $A b $B {
		lappend M [expr {($a+$b)/2.0}]
	}
	return $M
}

proc distance {A B} {
	set d2 0.0
	foreach a $A b $B {
		set d2 [expr {$d2 + ($a-$b)*($a-$b)}]
	}
	return [expr {sqrt($d2)}]
}

 # returns a new Path (a list of points) from the old one by adding
 # new points inbetween the old points  
proc complexifyPath {Points} {
	 # Points is a list of N>=2 points	
	set P0 [lindex $Points 0]
	foreach P1 [lrange $Points 1 end] {	
		lassign [midPoint $P0 $P1] Mx My
				
		set stddev [expr {0.125*[distance $P0 $P1]}]
		set newP [list [random-normal $Mx $stddev 1] [random-normal $My $stddev 1]]
		lappend newPoints $P0
		lappend newPoints $newP
		
		set P0 $P1		
	}
	 # append the last point
	lappend newPoints $P1
	return $newPoints
}


proc randomPath {A B} {
	set Points [list $A $B]
	for {set i 0} {$i<6} {incr i} {
		set Points [complexifyPath $Points]
	}
	return $Points
}

proc draw {sfc R} {
	set Points [randomPath {*}[circlePoints $R]]
	$sfc stroke  [BL::polyline {*}$Points]
}

 #--- MAIN -------------------------------------------------------------------

set WIDTH 800
set HEIGHT $WIDTH

wm title . "TclTk binding for Blend2d - Sketch 432335"
set sfc [image create blend2d -format [list $HEIGHT $WIDTH]]
. configure -background black
label .image -image $sfc -borderwidth 0 ; pack .image -expand 1

label .countdown \
	-background black -foreground lightgreen
place .countdown -in .image -relx 0.9 -rely 0.1 -anchor e


set R [expr {$WIDTH/2.5}]
 
 # place the origin at the center of the surface
set M [Mtx::translation [expr {$WIDTH/2.0}] [expr {$HEIGHT/2.0}]]
$sfc configure -matrix $M

 # strokes a white with a very low alpha (5.9%)
$sfc configure -stroke.style [BL::color white 0.059]

proc asyncCountDown {sfc R N} {
	if { $N > 0 } {
		 # draw 13 times in a refresh loop
		for {set i 0} {$i<13} {incr i} {
			draw $sfc $R
		}
		incr N -13
		.countdown configure -text $N 
		after idle "asyncCountDown $sfc $R $N"
		
	} else {
		.countdown configure -text "Electric Sphere" ;# done
		event generate . <<Ready>>
	}
}

bind . <<Ready>> {
	bind . <ButtonPress-1> {
		bind . <ButtonPress-1> {}
		$sfc fill all -style [BL::color black]
		asyncCountDown $sfc $R 8000
	}
}

update

event generate . <<Ready>>
event generate . <ButtonPress-1>

