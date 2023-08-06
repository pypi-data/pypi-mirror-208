# extracted from https://wiki.tcl-lang.org/page/Affine+transforms+on+a+canvas

# Affine Matrices 
# Affine transformations on 2D, can be performed with some particular 3x3 matrices,
# here called Affine Matrices.
# An Affine Matrix is a 3x3 matrix whose last column is fixed 0 0 1
#  a b 0
#  c d 0
#  e f 1
# Given this rule it is convenient to express such matrices as a list of 6 numbers
#  { a b c d e f } instead of 9 numbers.
    

namespace eval Mtx {}

proc Mtx::identity {} {list 1 0 0 1 0 0}

 # ---------------------------------------------------------------------------
 # Basic operations:
 #   MxM:        Matrix x Matrix x ... -->  Matrix
 #   determinant Matrix                -->  number
 #   invert      Matrix                -->  Matrix (or error)

 #   PxM:        Point x Matrix        -->  Point
 #   multiPxM:   ListOfPoints x Matrix -->  ListOfPoints
 #   P-P:        Point - Point         -->  Vector
 #   VxM:        Vector x Matrix       -->  Vector
 # ---------------------------------------------------------------------------
    
proc Mtx::MxM {M1 M2} {
	lassign $M1 a00 a01 a10 a11 a20 a21
	lassign $M2 b00 b01 b10 b11 b20 b21
	list \
		[expr {$a00*$b00+$a01*$b10}]      [expr {$a00*$b01+$a01*$b11}] \
		[expr {$a10*$b00+$a11*$b10}]      [expr {$a10*$b01+$a11*$b11}] \
		[expr {$a20*$b00+$a21*$b10+$b20}] [expr {$a20*$b01+$a21*$b11+$b21}]
}

proc Mtx::determinant {M} {
	lassign $M m00 m01 m10 m11 m20 m21
	expr {double($m00*$m11-$m01*$m10)}
}

proc Mtx::invert {M} {
	set d [determinant $M]
	if { $d == 0.0 } {
		error "Matrix is not invertible"
	}
	lassign $M m00 m01 m10 m11 m20 m21	
	set t00	[expr {$m11/$d}]
	set t01 [expr {-$m01/$d}]
	set t10 [expr {-$m10/$d}]
	set t11 [expr {$m00/$d}]

	list \
		$t00  $t01 \
		$t10  $t11 \
		[expr {-($m20*$t00+$m21*$t10)}]  [expr {-($m20*$t01+$m21*$t11)}]
}

 # map a Point
proc Mtx::PxM {P M} {
	lassign $P px py
	lassign $M m00 m01 m10 m11 m20 m21
	
	list [expr {$px*$m00+$py*$m10+$m20}] [expr {$px*$m01+$py*$m11+$m21}]
}

 # map a list of Points
proc Mtx::multiPxM {Points M} {
	lassign $M m00 m01 m10 m11 m20 m21

	set L {}
	foreach P $Points {
		lassign $P px py	
		lappend L [list [expr {$px*$m00+$py*$m10+$m20}] [expr {$px*$m01+$py*$m11+$m21}]]
	}
	return $L
}

 # get the vector from A to B   (A-B)
proc Mtx::P-P {A B} {
	set V {}
	foreach a $A b $B {
		lappend V [expr {$a-$b}]
	}
	return $V
}

 # mapVector
 # VxM(v,M) =  PxM(v,M)-PxM(0,M)
proc Mtx::VxM {V M} {
	lassign $V vx vy
	lassign $M m00 m01 m10 m11 m20 m21
	
	list [expr {$vx*$m00+$vy*$m10}] [expr {$vx*$m01+$vy*$m11}]
}

 # ---------------------------------------------------------------------------
 # Basic Matrices:
 #  identity                                 --> Matrix
 #  translation dx dy                        --> Matrix
 #  scale sx ?sy? ?Point?                    --> Matrix
 #  rotation alfa ?degrees|radians?  ?Point? --> Matrix
 #  skew sx sy                               --> Matrix
 #  xreflection                              --> Matrix
 #  yreflection                              --> Matrix 
 # ---------------------------------------------------------------------------
 
 
proc Mtx::translation {dx dy} {list 1 0 0 1 $dx $dy}

# scale sx sy around point C
#  fixed-point invariant:   C x T = C
proc Mtx::scale { sx {sy {}} {C {}} } {
	if {$sy eq {}} {set sy $sx}
	if { $C eq {} } {
		# C = (0 0), hence just a scale
		set T [list $sx 0 0 $sy 0 0]	
	} else {
		lassign $C cx cy
		set T [list \
				$sx 0  \
				0  $sy \
				[expr {$cx*(1-$sx)}] [expr {$cy*(1-$sy)}] \
				]
	}
	return $T
}

set Mtx::PI [expr {acos(-1)}]

proc Mtx::rotation {angle {units radians} {C {0 0}}} {
	switch -- $units {
		degree - degrees {
			variable PI
			set angle [expr {double($angle)/180*$PI}]
		}
		radian - radians {
			# Do nothing
		}
		default {
			return -code error "unknown angle unit \"$units\": must be degree(s) or radian(s)"
		}
	}
	set sinA [expr {sin($angle)}]
	set cosA [expr {cos($angle)}]
	if { $C eq {} } { set C {0 0} }
	lassign $C cx cy
	list \
		$cosA           $sinA \
		[expr {-$sinA}] $cosA \
		[expr {$cx-$cosA*$cx+$sinA*$cy}] [expr {$cy-$sinA*$cx-$cosA*$cy}]
}

proc Mtx::skew {sx sy} {list 1 $sx $sy 1 0 0}

proc Mtx::xreflection {} {list -1 0 0 1 0 0}

proc Mtx::yreflection {} {list 1 0 0 -1 0 0}

 # ---------------------------------------------------------------------------
 # Composite transformations
 # 
 # common transformation like
 #  apply a (pre/post)translation to the current matrix
 #  apply a (pre/post)rotation to the current matrix
 # could be easily written as:
 #
 #   # (pre) translate current matrix
 #   MxM [translation $dx $dy] $M
 #
 #   # (post) translate current matrix
 #   MxM $M [translation $dx $dy]
 #
 #  ... and so on ...
 #
 # here some explicit common composite operations:
 #  translate      M dx dy                          --> Matrix
 #  post_translate M dx dy                          --> Matrix
 #  scaling        M sx sy ?Point?                  --> Matrix
 #  post_scaling   M sx sy ?Point?                  --> Matrix

 #  rotate         M angle degrees!radians ?Point?  --> Matrix
 #  post_rotate    M angle degrees!radians ?Point?  --> Matrix
 
 # ---------------------------------------------------------------------------

 # (pre)translate
proc Mtx::translate {M dx dy} {
	# eqq  Mtx::MxM [Mtx::translation $dx $dy] $M
	lassign $M m00 m01 m10 m11 m20 m21
	list \
		$m00 $m01 \
		$m10 $m11 \
		[expr {$dx*$m00+$dy*$m10+$m20}] [expr {$dx*$m01+$dy*$m11+$m21}]
}

proc Mtx::post_translate {M dx dy} {
	# eqq  Mtx::MxM $M [Mtx::translation $dx $dy]
	lassign $M m00 m01 m10 m11 m20 m21
	list \
		$m00 $m01 \
		$m10 $m11 \
		[expr {$dx+$m20}] [expr {$dy+$m21}]
}


  # (pre)scaling 
  # C is the fixed point 
proc Mtx::scaling { M sx sy {Cxy {0 0}} } {
    return [MxM [scale $sx $sy $Cxy] $M]
}

  # (post)scaling 
proc Mtx::post_scaling { M sx sy {Cxy {0 0}} } {
    return [MxM $M [scale $sx $sy $Cxy]]
}


proc Mtx::rotate {M angle units {Cxy {0 0}}} {
    set M [MxM [rotation $angle $units $Cxy] $M]
	return $M
}

proc Mtx::post_rotate {M angle units {Cxy {0 0}}} {
    set M [MxM $M [rotation $angle $units $Cxy]]
	return $M
}

proc Mtx::yreflect {M} {
     # note: it's a post-transformation
    MxM $M [yreflection] 
}

package provide Mtx 1.0
