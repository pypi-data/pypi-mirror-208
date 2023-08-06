#  SKETCH
#   experimental algorithms for drawing pseudo hand-draw lines.
#
#   2020 -Irrational Numbers


namespace eval sketch {

     # ---------------------------------------------
     # the following procs for matrix multiplication 
     # are borrowed from the Mtx package.
     # ---------------------------------------------

     # affine matrix multiplication 
    proc MxM {M1 M2} {
    	lassign $M1 a00 a01 a10 a11 a20 a21
    	lassign $M2 b00 b01 b10 b11 b20 b21
    	list \
    		[expr {$a00*$b00+$a01*$b10}]      [expr {$a00*$b01+$a01*$b11}] \
    		[expr {$a10*$b00+$a11*$b10}]      [expr {$a10*$b01+$a11*$b11}] \
    		[expr {$a20*$b00+$a21*$b10+$b20}] [expr {$a20*$b01+$a21*$b11+$b21}]
    } 

    proc Mtranslation { dx dy } {
        list 1 0 0 1 $dx $dy
    }
     
     # map a list of Points
    proc multiPxM {Points M} {
    	lassign $M m00 m01 m10 m11 m20 m21
    
    	set L {}
    	foreach P $Points {
    		lassign $P px py	
    		lappend L [list [expr {$px*$m00+$py*$m10+$m20}] [expr {$px*$m01+$py*$m11+$m21}]]
    	}
    	return $L
    }


     # Based on the paper 
     #  "Automatically Mimicking Unique Hand-Drawn Pencil Lines"
     #  by AlMeraj et al.
     #
     # the primary control points on the x-axis should not be distributed
     #  at equal distance, but they should be more dense at the extremities
     # 
     # NOTE: this is arbitrary ...
     #  a simpler and very close equation is a quad-easeIn-easeOut
     #   if t<0.5 -> 2*t^2
     #            else ((2t+2)^2)/2
     
    proc x_distrib {t} {
        expr {-(15*$t**4-6*$t**5-10*$t**3)}
    }

}

proc tcl::mathfunc::random {a b} {
    expr {$a+rand()*($b-$a)}
}


 # -splits    : numero of splits
 # -amplitude: percentage coefficient of maximum perturbation (kA)
 #             i.e a line of length $length will have some randomly perturbated
 #             points at a distance of kA/100*length.
 # -tension  : coefficient for smooting the curves at the control points.
 #             k = 0 means that the resulting curve interpolating the random
 #             control points tends to a sequence of straight segments.
 #             Must be < 1
proc sketch::normalizeParameters {params length} {
    # -- get params; set defaults if some keys are missing ..
 
    foreach key {-splits -amplitude -tension} {
        if { ![dict exists $params $key] } {
            switch -- $key {
                -splits { 
                    if { $length < 100 } { 
                        set value 2 
                    } elseif { $length < 300 } { 
                        set value 4 
                    } else {
                        set value 7
                    }
                }
                -amplitude {
                    set value 0.8 
                }
                -tension {
                    set value 0.45
                }
                -width {
                    set value 7.0
                }
                -sigmawidth {
                    set value 0.4
                }
            }
            dict set params $key $value
        }       
    }
    return $params
}


 # This is the basic algorithm for creating an horizontal hand-made line.
 #
 # This algoritm computes a random 'sketched line' from (0,0) to (length,0)
 # returning a list of points {x y} denoting a 
 # sequence of smooth connects cubic curves
 #
 #  see handmade_line for the meaning of params dictionary
 #
proc sketch::_horizontal_handmade_line {params length} {
    
    # -- get params; set defaults if some keys are missing ..
    set params [normalizeParameters $params $length]
    set splits [dict get $params -splits]
    set kA [dict get $params -amplitude]
    set kT [dict get $params -tension]
    
# ? should we add some random noise to the extremities ??    
    set Path [list]
    lappend Path {0 0}

    set xp 0.0
    set yp 0.0

      # versor on (xp,yp)
    set vxp 1.0
    set vyp 0.0

    set t 0.0
    set ttp [expr {[x_distrib 0.0]}]
     # first controlpoint is fixed ; start from the next control point    

    set dt [expr {1.0/($splits+1)}]

    for { set n 0 ; set t $dt } { $n < $splits } { incr n ; set t [expr {$t+$dt}] } {

        # calculate x  ..
        #  more control points near the extremities 
        set tt [x_distrib $t]
        set x [expr {$tt*$length}]

        # add a random dx displacement to x
        # ----------------------------------
        # Note: since the x points are not equally distributed,
        #  you should take care to add a small random displacement that WON'T
        # subvert the order given by x_distrib.
        set k 0.5 ; # any coeff between [0..1)
        set low  [expr {($xp+$x)*$k}]            ;# midpoint between xp and x
        set tnext [x_distrib [expr {$t+$dt}]]
        set high [expr {($x+$tnext*$length)*$k}] ;# midpoint between x and xnext
        set x [expr {random($low,$high)}]


        # add a random dy perturbation (central points have greater perturbation)
        # ----------------------------------------------------------------------
         ## get the midpoint between ttp and tt
        set ttt [expr {($tt+$ttp)/2.0}]
         # "A" (max amplitude) depends on x ( or better, on tt ) so that central points
         #  may have a larger y-variation.
         # Use a Gaussian centered on 1/2
        set A [expr {$kA*$length/100.0*exp(-((($ttt-0.5)/0.3)**2))}]
         # then extract a random y between low and high
        set high [expr {min($yp+$A,$A)}]
        set low  [expr {max($yp-$A,-$A)}]        
        set y [expr {random($low,$high)}]

        
         # draw a cubic starting at (xp,yp) ending at (x,y).
         # The first point defining the curve tangent should have the *opposite*
         #  direction of the last tangent, but a reduced (half) length
         # This means that the new cubic starts with the same tangent
         # of the previous cubic with an half  strength.
         # The tangent at (x,y) is directed towards (xp,yp)

        set dx [expr {$x-$xp}]
        set dy [expr {$y-$yp}]
        set d [expr {sqrt($dx**2 + $dy**2)}]         

        lappend Path \
            [list [expr {$xp+$vxp*$d*$kT/2.0}] [expr {$yp+$vyp*$d*$kT/2.0}]] \
            [list [expr {$x-$dx*$kT}]  [expr {$y-$dy*$kT}]] \
            [list $x $y]                    


        set vxp [expr {$dx/$d}]
        set vyp [expr {$dy/$d}]

        set xp $x
        set yp $y        
        set ttp $tt        
    }
     # last point (x,y) = (length,0)
    set x $length
    set y 0

    set dx [expr {$x-$xp}]
    set dy [expr {$y-$yp}]
    set d [expr {sqrt($dx**2 + $dy**2)}]

    lappend Path \
        [list [expr {$xp+$vxp*$d*$kT/2.0}] [expr {$yp+$vyp*$d*$kT/2.0}]] \
        [list  [expr {$x-$dx*$kT}] [expr {$y-$dy*$kT}]]  \
        [list $x $y]      
     
    return $Path
}

# ============================================================================
# ============================================================================
# ============================================================================


   # ===========================================================================
   # sketch::line - generates a random hand-drawn line (simple stroke)
   #
   # generates a composite path as a sequence of cubic curves
   #
   # params      : a dictionary providing some coeffiecients for generating
   #               some variations.
   #               It may contains the following entries:
   #                -splits      : how many perturbations.
   #                              If missing then it's automatically determined
   #                              based on the line's length.
   #                              Suggested values 2..8
   #                -amplitude  : the max perturbation, i.e. the max distance
   #                              from the 'ideal' straight line.
   #                              If missing then it's automatically determined
   #                              based on the line's length (about 1% of the line's legth).
   #                -tension      : tension coefficient [0..1] for the perturbations.
   #                                higher values generates smooth curves
   #                                Default is 0.4
   # x0 y0 x1 y1 : line extremities
   #
   #
   # return a list of svg-like commands like the following
   #  {M {20.0 10}}   {C {1 2} {5 7} {2 0}}    {C {7 22} {3 2} {4.9,5.1}}   ....
   # ===========================================================================

proc sketch::line {params x0 y0 x1 y1} {

    set length [expr {sqrt(($x1-$x0)**2+($y1-$y0)**2)}]

    # rotate the line so that it becomes horizontal

    # this is just an ideal transformation; you start working on an horizontal line
    # from (0.0)  to (len,0)

    set Points [_horizontal_handmade_line $params $length]

     # reverse the initial roto-translation
    set cosTh [expr {($x1-$x0)/$length}]
    set sinTh [expr {($y1-$y0)/$length}]
    set rotMtx [list $cosTh $sinTh [expr {-$sinTh}] $cosTh 0 0]
    set mtx [MxM $rotMtx [Mtranslation $x0 $y0]]

    set Points [multiPxM $Points $mtx]

    set svg {}
    
    lappend svg [list "M" [lindex $Points 0]]
    foreach {P1 P2 P3} [lrange $Points 1 end] {
        lappend svg [list "C" $P1 $P2 $P3]
    }
    return $svg
}   


   # ===========================================================================
   # sketch::line_variablewidth - generates a random hand-drawn line (variable width)
   #
   # generates a composite path as a *closed* sequence of cubic curves
   #
   # params      : a dictionary providing some coeffiecients for generating
   #               some variations.
   #               See all params for sketch::line, PLUS
   #               -width      : max line width
   #               -sigmawidth : sigma (of the Gaussian bell) for decreasing
   #                             the width near the extremities.
   # x0 y0 x1 y1 : line extremities
   #
   #
   # return
   #  .. same as for sketch::line ,but note that the resulting svg-path is closed !
   # ===========================================================================
proc sketch::line_variablewidth {params x0 y0 x1 y1} {

    set WIDTH [dict get $params -width]
    set SIGMA [dict get $params -sigmawidth]
    
    set length [expr {sqrt(($x1-$x0)**2+($y1-$y0)**2)}]

    # rotate the line so that it becomes horizontal

    # this is just an ideal transformation; you start working on an horizontal line
    # from (0.0)  to (len,0)

    set Points [_horizontal_handmade_line $params $length]
    
    set revPoints [lmap P [lreverse $Points] {
        lassign $P x y
        
        set t [expr {$x/$length}]
         # Use a Gaussian centered on 1/2 (+/- 10% random)
        set mu [expr {random(0.40,0.60)}]
        set y [expr {$y+$WIDTH*exp(-((($t-$mu)/$SIGMA)**2))}]        
        list $x $y        
    }]
   # revPoints  sono trasformati da gaussiana..

     # reverse the initial roto-translation to Points and revPoints
     # -------------------------------------------------------------
    set cosTh [expr {($x1-$x0)/$length}]
    set sinTh [expr {($y1-$y0)/$length}]
    set rotMtx [list $cosTh $sinTh [expr {-$sinTh}] $cosTh 0 0]
    set mtx [MxM $rotMtx [Mtranslation $x0 $y0]]

    set Points [multiPxM $Points $mtx]
    set revPoints [multiPxM $revPoints $mtx]
   

     # finally, convert points in svg-like commands
    set svg {}
    
    lappend svg [list "M" [lindex $Points 0]]
    foreach {P1 P2 P3} [lrange $Points 1 end] {
        lappend svg [list "C" $P1 $P2 $P3]
    }

     # add a simple (LINE) junction to the 1st point of the revPoints
    lappend svg [list "L" [lindex $revPoints 0]]
    foreach {P1 P2 P3} [lrange $revPoints 1 end] {
        lappend svg [list "C" $P1 $P2 $P3]
    }
    lappend svg [list "Z"] 
    
    return $svg
}
