 #
 # Based "Neon Spiky Slower" sketch.
 # see https://openprocessing.org/sketch/160305
 #
 
set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

package require Blend2d

set WIDTH 600
set HEIGHT $WIDTH

wm title . "TclTk binding for Blend2d - Sketch 160305"
set sfc [image create blend2d -format [list $HEIGHT $WIDTH]]
label .sfc -image $sfc ; pack .sfc
label .statusBar -anchor center; pack .statusBar -fill x

set PI [expr {acos(-1.0)}]

proc degToRad {deg} {
    global PI
    expr {$deg/180.0*$PI}
}


 #    beta is in degree
 # return a BLPath
proc newPetal { R beta } {
	set path [BL::Path new]
#puts -nonewline "beta $beta   "
	set beta [degToRad $beta]
	set x [expr {$R*cos($beta)}]
	set y [expr {$R*sin($beta)}]
#puts "beta $beta R $R  x,y $x  $y "	
	$path moveTo [list $x $y]
	$path cubicTo [list 0 [expr {2*$y}]]  [list 0 [expr {-2*$y}]] [list $x [expr {-$y}]]	
	$path cubicTo [list [expr {2*$R}] 0]  [list [expr {2*$R}] 0] [list $x $y]

	return $path	
}

proc newCrownOfPetals { R beta } {
	set crown [BL::Path new]
	set petal [newPetal $R $beta]
	set dTheta [expr {360/9}] ; # 9 petals
	for { set theta 0 } {$theta < 360} {incr theta $dTheta} {
		$crown add $petal -matrix [Mtx::rotation $theta degrees] 
	}
	$petal destroy
	return $crown
}

 #--------
set R [expr {$WIDTH/3.0-20}]
 
 # place the origin at the center of the surface
set M [Mtx::translation [expr {$WIDTH/2.0}] [expr {$HEIGHT/2.0}]]
$sfc configure -matrix $M

$sfc configure -stroke.style 0xFFD0FFD8 ; # pale green .. almost white

 # click to suspend/resume
.statusBar configure -text "Click to start"
set STATUS off
bind .sfc <ButtonPress-1> {
	set STATUS [expr {! $STATUS}] 
	if { $STATUS } {
		.statusBar configure -text "Click to suspend"
		Draw $sfc
	} else {
		after cancel $TASKID
		.statusBar configure -text "Click to resume"
	}
}

proc Draw {sfc} {
	global BETA
	global TASKID
	global R
     # background is black, with a low alpha.
     # In this way, instead of filling with pure black,
     # we get a "fade-to-black" effect
    $sfc clear -style 0x05000000
    
	set crown [newCrownOfPetals $R $BETA]
	$sfc stroke $crown
	$crown destroy

	set BETA [expr {$BETA + 0.5}]
	set TASKID [after 5 "Draw $sfc"]
}

set BETA 0.0
