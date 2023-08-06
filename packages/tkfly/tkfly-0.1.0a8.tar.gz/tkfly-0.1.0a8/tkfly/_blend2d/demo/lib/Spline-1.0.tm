##  Spline - Catmull-Rom splines
##
## Copyright (c) 2021 <Irrational Numbers> : <aldo.w.buratti@gmail.com> 
##
##
## This library is free software; you can use, modify, and redistribute it
## for any purpose, provided that existing copyright notices are retained
## in all copies and that this notice is included verbatim in any
## distributions.
##
## This software is distributed WITHOUT ANY WARRANTY; without even the
## implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
##

# == Catmull-Rom Splines =====================================================

#  A (k-Dim) Point is represented as a list of k numbers.
#
#  A Catmull-Rom spline is defined by a sequence of N (N>=4) Points
#  (also called ControlPoints (CP)).
#
#  WARNING:
#  Splines are not limited to 2-Dim Splines, this package can work with K-Dim Splines,
#   but it's the programmers's responsability to ensure that all Points
#   in a given Spline have the same dimension, or result can be unpredictable.
#
#  The Spline class provides basic methods for adding/deleting/repositioning 
#   ControlPoints, but above all provides the method 'cubics'
#   for deriving a chained sequence of cubic curves.
#  Each cubic curve joins two consecutive ControlPoints (a curved segment), 
#   but the first and the last 'segments'
#   are not 'developed' as cubics curves, since the first ControlPoint (CP0)
#   is just required for defining the starting tangent of the first cubics curve
#   (from CP1 to CP2), and the last ControlPoint (CPN-1) is just required for 
#   defining the ending tangent of the last cubic curve (form CPN-3 to CPN-2).
#
#   Thus, with N ControlPoints (CP0, CP1 ..., CPN-2, CPN-1) we can get
#   a sequence of (N-3) chained cubic curves represented as a sequence 
#   of 1+3*(N-3) points,
#   that should be interpreted as a sequence of SVG-like commands like
#     MOVE CP1
#     CUBIC p p CP2
#     CUBIC p p CP3
#     ....
#     CUBIC p p CPN-2
#
#  This Spline class also provide the 'extended_cubics' method. 
#  This method allows to build an Open or Closed spline, passing through
#  all the ControlPoints, including the first and and the last ControlPoints
#  that are normally discarded. This is done by adding two dummy
#  hidden controlpoints (an initial and a final controlpoint) required for a classic 
#   Catmull-Rom spline.
# 
#  By using the 'extended_cubics' method it's also possible to build an open-spline
#  with just 2 control-points (it's a straight segment) 
#  and a closed-spline with just 3 points.

# =============================================================================

package require snit

snit::type Spline {

     # Alternative to "Spline create %AUTO% ..."
    typemethod new {args} {
        uplevel 1  [list $type create %AUTO% {*}$args]
    }

    proc _flatten {args} {
        if { [llength $args] == 1 } {
           set args {*}$args
        }
        return $args    
    }

	 # return true or raise an error
	proc _check_Point {P idx} {
		set dim [llength $P]
		if { $dim < 1 } {
			error "Point #$idx is empty"
		}
		foreach c $P {
			if { $c eq "" || ![string is double $c] } {
				error "Point #$idx has non-numeric components"
			}
		}
		return true	
	}     

	 # return true or raise an error
	proc _check_ListOfPoints {L} {
		set P0 [lindex $L 0]
		_check_Point $P0 0  ;# --> may raise an error
		set dim [llength $P0]
		set idx 0
		foreach P $L {
			set pdim [llength $P]
			if { $dim != $pdim } {
				error "Point #$idx has ${pdim} dimensions. All Points must have ${dim} dimensions" 
			}
			_check_Point $P $idx  ;# --> may raise an error
			incr idx
		}
		return true	
	}     

	variable my
	
	  # args is a sequence of Points or 1 list of Points
	constructor {args} {
		set my(userdata) {}
		set my(isClosed) false

		 # Saved values for lazy evaluation of cubics,
		 # my(saved.cubics) must be reset every time a controlpoint changes
		set my(saved.cubics) {} 
		set my(saved.tau) {}
		
		set points [_flatten {*}$args]
# ???
# trick: format the string as a list
#		set points [lrange $points 0 end]
		_check_ListOfPoints $points   ;# may raise an error ...

		set my(ControlPoints) $points
	}

	 # get/set userdata
	 #  userdata can be anything : a string, a list, ... 
	 #  we recommentd to use a dict"
	method userdata {args} {
		switch -- [llength $args] {
		 0 { return $my(userdata) }
		 1 { set my(userdata) {*}$args ; return }
		 default {
		 	error "should be \"$self userdata ?value?\""}
		}
	}

	 # get/set loop:
	 # $c loop  -> true/false  (true means: $s is a closed spline)
	 # $c loop true -> turn spline in a closed spline
	 # $c loop false -> turn spline in an open spline
	method loop {args} {
		switch -- [llength $args] {
		 0 { return $my(isClosed) }
		 1 { 
		 	set val {*}$args
		 	if { $val eq "" || ![string is boolean $val] } {
				error "expected a boolean value; got \"$val\"" 
			}
		 	set my(isClosed) $val
		 	set my(saved.cubics) {}
			return 
		 }
		 default {
		 	error "should be \"$self loop ?value?\""}
		}
	}

	method clone {} {
		set newObj [$type new [$self points]]
		$newObj loop $my(isClosed)
		$newObj userdata $my(userdata)
		return $newObj
	}
	
			
	method nOfPoints {} { return [llength $my(ControlPoints)] } 

	method points {args} {
		if { [llength $args] == 0 } {
			return $my(ControlPoints)
		}
		
		set my(ControlPoints) [_flatten {*}$args]
	 	set my(saved.cubics) {}
		return
	}

	 # insert a ControlPoint before idx
	method insertPoint { idx P } {
		set my(ControlPoints) [linsert $my(ControlPoints) $idx $P]
	 	set my(saved.cubics) {}
	}

	 # no error if the i-th ControlPoints does not exists
	method removePoint {idx} {
		set my(ControlPoints) [lreplace $my(ControlPoints) $idx $idx]	
		set my(saved.cubics) {}
	}

	method movePoint {idx dP} {
		if { $idx < 0 || $idx >= [llength $my(ControlPoints)] } {
			error "index out of range"
		}
		set P [lindex $my(ControlPoints) $idx]
		set newP {}
		foreach p $P dp $dP {
			lappend newP [expr {$p+$dp}]
		}
		$self setPoint $idx $newP
		set my(saved.cubics) {}
	}

	 # translate the whole Spline 
	method move {dP} {
		set idx 0
		set newCPs {}
		foreach P $my(ControlPoints) {
			set newP {}
			foreach p $P dp $dP {
				lappend newP [expr {$p+$dp}]
			}
			lappend newCPs $newP		
		}
		set my(ControlPoints) $newCPs
		
		 # TODO optimization:
		 # in this case you don't need to recompute the cubics;
		 # they could be simply translated by dP
		set my(saved.cubics) {}
		return
	}

	 # scale the whole Spline.
	 #  originP - the origin (fixed-point) of the scale transformation
	 #  sVector - specify how to scale each dimension
	method scale {originP sVector} {
		set idx 0
		set newCPs {}
		foreach P $my(ControlPoints) {
			set newP {}
			foreach p $P o $originP s $sVector {
				lappend newP [expr {($p-$o)*$s+$o}]
			}
			lappend newCPs $newP		
		}
		set my(ControlPoints) $newCPs

		 # TODO optimization:
		 # in this case you don't need to recompute the cubics;
		 # they could be simply scaled
		set my(saved.cubics) {}

		return
	}


	 # change the i-th ControlPoint
	 #  - raise error if idx is out of range
	method setPoint {idx P} {
		lset my(ControlPoints) $idx $P
		set my(saved.cubics) {}
	}
	method getPoint {idx} {
		lindex $my(ControlPoints) $idx
	}
	
	 # this is the 'official' cubics expansion.
	 # Currently it uses the _cemyuksel_cubics algorithm  		
	 # See also the alternative algorithm  "_uniform_cubics"
	proc _cubics { cPoints {tau 0.5} } {
		_cemyuksel_cubics $cPoints $tau
	}


	 #	distance_alpha(A,B,a) is  ||A-B||**a
	proc _distance_alpha {A B {alpha 0.5}} {
		set d 0.0
		foreach a $A b $B {
			set d [expr {$d+($a-$b)*($a-$b)}]
		}
		return [expr {$d**(0.5*$alpha)}]
	}

	 # non-uniform distance parameterized CatmullRom
	 # see http://www.cemyuksel.com/research/catmullrom_param/catmullrom.pdf
	 #	alpha = 0    -> uniform
	 #	alpha = 1    -> chordal
	 #	alpha = 1/2  -> centripetal
	proc _cemyuksel_cubics { cPoints {alpha 0.5} } {
		if { [llength $cPoints]  <4 } {return {}}

		set bPoints {} ;# bezier-Points i.e. the bezier-cubic points
	     # get the first 3 control-points (and discard them from $cPoints)
		set cPoints [lassign $cPoints P0 P1 P2]

		 #	di = ||P(i)-P(i-1)||^a    ( for i = 1,2,3) )
		set d1 [_distance_alpha $P1 $P0 $alpha]
		set d2 [_distance_alpha $P2 $P1 $alpha]

		lappend bPoints $P1 ;# starting point

		foreach P3 $cPoints {

			set d3 [_distance_alpha $P3 $P2 $alpha]

			# B0 = P1
			# B1 = (d1^2*P2-d2^2*P0 + (2*d1^2+3*d1*d2+d2^2)*P1) / (3*d1*(d1+d2))
			# B2 = (d3^2*P1-d2^2*P3 + (2*d3^2+3*d3*d2+d2^2)*P2) / (3*d3*(d2+d3))
			# B3 = P2	
			set B1 {}
			set B2 {}
			
			set denomB1 [expr {3*$d1*($d1+$d2)}]  ;# >= 0.0
			set denomB2 [expr {3*$d3*($d2+$d3)}]  ;# >= 0.0
			
			foreach p0 $P0 p1 $P1 p2 $P2 p3 $P3 {
				if { $denomB1 < 1e-9 } {
					lappend B1 $p1
				} else {
		    		lappend B1 [expr {($d1*$d1*$p2-$d2*$d2*$p0+(2*$d1*$d1+3*$d1*$d2+$d2*$d2)*$p1)/$denomB1}]
				}
				if { $denomB2 < 1e-9 } {
					lappend B2 $p2
				} else { 
	    			lappend B2 [expr {($d3*$d3*$p1-$d2*$d2*$p3+(2*$d3*$d3+3*$d3*$d2+$d2*$d2)*$p2)/$denomB2}]
				}
			}
			lappend bPoints $B1 $B2 $P2
			
			 # shift
			set P0 $P1
			set P1 $P2
			set P2 $P3
			
			set d1 $d2
			set d2 $d3
		}
		return $bPoints		
	}

	 # This method is *unused*; it's left here just for future implementations.
	 #  It computes cubics based on uniform-distance parametrization
	 #  controlled by a tau (tension) parameter.
	 #  If tau -> INF , then the spline -> polyline
	proc _uniform_cubics { cPoints {tau 1.0} } {
		if { [llength $cPoints]  <4 } {return {}}

		set bPoints {} ;# bezier-Points i.e. the bezier-cubic points
	     # get the first 3 control-points (and discard them from $cPoints)
		set cPoints [lassign $cPoints P0 P1 P2]

		lappend bPoints $P1 ;# starting point
		foreach P3 $cPoints {
			# B1 = P1 + (P2-P0)/(6*tau)
			# B2 = P2 - (P3-P1)/(6*tau)
			set B1 {}
			set B2 {}
			foreach p0 $P0 p1 $P1 p2 $P2 p3 $P3 {
				lappend B1 [expr {$p1+($p2-$p0)/(6.0*$tau)}]
				lappend B2 [expr {$p2-($p3-$p1)/(6.0*$tau)}]
			}
			lappend bPoints $B1 $B2 $P2
			
			 # shift
			set P0 $P1
			set P1 $P2
			set P2 $P3
		}
		return $bPoints		
	}


	 # Given a spline with N ControlPoints,
	 #  compute a sequence of 1+3*(N-3) points denoting (N-3) chained cubic curves.
	 # 
	 # if the number of ControlPoints is less tha 4, result is {}
	 # (a sequence of 0 points, hence 0 cubics curves)
	 #
	 # tau is unused, since we use the _cemyuksel_cubics
	method cubics { {tau 0.5} } {
		if { $my(saved.cubics) eq {} || $tau != $my(saved.tau) } {
			 # tau 0.5 is for centripetal splines
			set my(saved.cubics) [_cemyuksel_cubics $my(ControlPoints) $tau]
			set my(saved.tau) $tau
		}
		return $my(saved.cubics)
	}


	 # distance between Points A and B
	proc _distance {A B} {
		set d 0.0
		foreach a $A b $B {
			set d [expr {$d+($a-$b)*($a-$b)}]
		}
		return [expr {sqrt($d)}]
	}


	 #NOTE:
	 #When defining a CLOSED Spline, it's not necessary
	 #the last point be equal to the first.
 	 #We recommend: don't add a closure point (it's not a fault, but it's useless
	 #and furthermore it generates a final degenere segment (just a point).
	proc _extended_cubics {cPoints tau isClosed} {
		set ecPoints {} ;# extended control-points
		switch -- $isClosed {
		   	true {
				if { [llength $cPoints] < 3 } {	return {} }
							   	
				lappend ecPoints [lindex $cPoints end]
				lappend ecPoints {*}$cPoints
				lappend ecPoints {*}[lrange $cPoints 0 1]		   
			   }
			false {
				if { [llength $cPoints] < 2 } { return {} }
							   	
				 # Compute the new point before the first point
				 # P = P0+(P0-P1)*tau
				lassign $cPoints P0 P1
				set P {}
				foreach p0 $P0 p1 $P1 {
					lappend P [expr {$p0+($p0-$p1)/$tau}]
				}
				lappend ecPoints $P
				
				lappend ecPoints {*}$cPoints
	
				 # Compute the new point after the last point
				 # P = P(N)+(P(N)-P(N-1))*tau
				set PN_1 [lindex $cPoints end-1]
				set PN   [lindex $cPoints end]
				set P {}
				foreach p0 $PN p1 $PN_1 {
					lappend P [expr {$p0+($p0-$p1)/$tau}]
				}
				lappend ecPoints $P 
			}
			default {
				error "wrong mode \"$mode\. Must be OPEN or CLOSED"
			}
		}
		_cubics $ecPoints $tau
	 }

 # -----------------------------------------------------
 #  This method allows to build an open or closed spline, by defining just the points
 #  on the curve; the 'hidden' initial and final points 
 #  required for a classic CatmullRom spline are automatically computed.
 #
 #   _mode_ can be OPEN (default) for open curves or CLOSED for closed curves.
 #
 #  If the spline is CLOSED, then it's not required that the last point be equal to the first point,
 #  then someting like a 'fat' triangle can be defined with just 3 points.
 #  Note that the curves resulting from 
 #   extended_spline {A B C A} tau false (OPEN spline)
 #  are different from the curves resulting from 
 #   extended_spline {A B C} tau true  (CLOSED spline)
 #   or
 #   extended_spline {A B C A} tau true (CLOSED spline)
 #
 # --
 # Given a list with N Points, extended_cubics generates a sequence of Points denoting 
 # a chain of N-1 cubic curves (one more cubic curve if spline is closed) 
 # 
 # For an OPEN extented_spline with N Points, result will be a sequence of 1+3*(N-1) Points;
 #   Note that for N=2 result will be a sequence of 4 Points denoting a (degenerate) cubic-curve looking like a straight segment.
 #   If N<2 then result will be {}
 # For a CLOSED extented_spline with N Points, result will be a sequence of 1+3*(N) Points.
 #   If N<3 then result will be {}
 #

	method extended_cubics {{tau 0.5}} {
		_extended_cubics $my(ControlPoints) $tau  $my(isClosed)
	}
}
 