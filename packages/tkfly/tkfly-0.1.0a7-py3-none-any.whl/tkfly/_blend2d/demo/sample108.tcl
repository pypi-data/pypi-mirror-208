 #
 # Based on "Harmony (Circle)" sketch.
 # see https://openprocessing.org/sketch/1253474
 #
 
set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

set auto_path [linsert $auto_path 0 [file join $thisDir lib]]
tcl::tm::path add [file join $thisDir lib]

package require Spline
package require Blend2d

	#
	# -- some math functions -----------------------------------------
	#
	proc tcl::mathfunc::clamp {v a b} { expr {$v<$a ? $a : ($v<$b ? $v :$b)} }
	
	proc tcl::mathfunc::map {x a0 a1 b0 b1} { expr {(double($x)-$a0)*($b1-$b0)/($a1-$a0)+$b0} }
	
	proc tcl::mathfunc::random {a b} { expr {rand()*($b-$a)+$a} }

	proc tcl::mathfunc::random_item {items} { lindex $items [expr {int(rand()*[llength $items])}] }

	set PI [expr {acos(-1.0)}]


proc Draw {sfc R frameCount} {
	global Waves

	set frameLimit 400

	 # t goes from 0, 1/400 2/400 ... 400/400	
	set t [expr {($frameCount%$frameLimit)/double($frameLimit)}]
	
	 # every frameLimit frames, prepare new waves
	if { $t == 0.0 } {
		set COLORS {
			"#008cff" "#0099ff" "#00a5ff" "#00b2ff" "#00bfff" "#00cbff" "#00d8ff"
			"#00e5ff" "#00f2ff" "#00ffff" "#ff7b00" "#ff8800" "#ff9500" "#ffa200"
			"#ffaa00" "#ffb700" "#ffc300" "#ffd000" "#ffdd00" "#ffea00"}
		set Waves {}
		for {set i 0} {$i<6} {incr i} {
			lappend Waves [dict create \
				strokeWeight [expr {random(2,5)}] \
				strokeColor  [expr {random_item ($COLORS)}] \
				freq         [expr {floor(random(1,3))*random_item( {-1 +1} )}] \
				amplitude    [expr {random(10.0,$R/3.0)}] \
				phase        [expr {random_item( {-3 -2 -2 -1 -1 -1 1 1 1 2 2 3} )}] \
			]
		}
	}

	$sfc push
	$sfc configure -compop PLUS
	foreach wave $Waves {
		set wavePath [CreateWavePath $wave $t -$R $R]
		$sfc stroke $wavePath \
			-width [dict get $wave strokeWeight] \
			-style [BL::color [dict get $wave strokeColor]]
		$wavePath destroy
	}
	$sfc pop
	
	$sfc stroke [BL::circle {0 0} $R] -width 4 -style [BL::color white]
}

 #
 # return a new BL::Path representing a wave
 #
 # t goes from 0 to 1
 # 
 # we plot a wave as s sinusoid in the [b0 b1] interval whose amplitude 
 # is gracefully dampled to 0 near the limits of this interval.
 # Moreover the t parameter controls how the phase changes and how the resultin wave
 #  is dampled ( for t near 0 or t near 1, the resulting wave is pratically flattened to 0)
proc CreateWavePath { wave t b0 b1 } {
	global PI
	
	set L [expr {double($b1-$b0)}]

	set freq [dict get $wave freq]
	set Amplitude [dict get $wave amplitude]
	set Phase [dict get $wave phase]

	set controlPoints {}
	set dx [expr {max($L/$freq/50.0,5.0)}]
	for {set x $b0} {$x<=$b1} {set x [expr {$x+$dx}]} {
		 # damping function : it's back-flip parabolic function with zeros at b0 and b1
		 #   This function will be applied to the sinusoid for damping its amplitude
		 #   so that at b0 and b1 the resulting sinusoid goes gracefully to zero near b0 and b1
		set alpha [expr {-4.0*($x-$b0)*($x-$b1)/($L*$L)}]  ;# // attenuazione ... ricontrolla

		 # another damping function on t: is gooes to zero when t is 0 or 1
		set amplitude [expr {$Amplitude*(4*$t*(1-$t))}]
		 # by changing t from [0,1] , phase goes from [0,Phase]
		set phase [expr {$Phase*$t}]
	
		set y [expr {sin(2*$PI*($freq*($x-$b0)/$L+$phase))*$amplitude*$alpha}]
		
		lappend controlPoints [list $x $y]
	}

	set spline [Spline new $controlPoints]
	
	 # compute cubics
	set cubicsPoints [lassign [$spline extended_cubics] P1]
	$spline destroy
	
	set gSpline [BL::Path new]	
	$gSpline moveTo $P1
	foreach {P1 P2 P3} $cubicsPoints {
		$gSpline cubicTo $P1 $P2 $P3
	}
	return $gSpline
}


# ---  main -----

set WIDTH 600
set HEIGHT $WIDTH

wm title . "TclTk binding for Blend2d - Sketch 1253474"
set sfc [image create blend2d -format [list $HEIGHT $WIDTH]]
label .sfc -image $sfc ; pack .sfc
label .statusBar -anchor center; pack .statusBar -fill x
	
 # place the origin at the center of the surface
set M [Mtx::translation [expr {$WIDTH/2.0}] [expr {$HEIGHT/2.0}]]
$sfc configure -matrix $M

proc DrawLoop {sfc R {frameCount 0}} {
	$sfc clear -style [BL::color black]
	Draw $sfc $R $frameCount
	after 20 DrawLoop  $sfc $R [incr frameCount]
}

DrawLoop $sfc [expr $WIDTH/2.5]
 	