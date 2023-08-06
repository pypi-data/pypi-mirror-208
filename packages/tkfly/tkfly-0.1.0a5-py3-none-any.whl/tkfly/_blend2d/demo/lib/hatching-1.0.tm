
proc swap {varA varB} {
    upvar $varA a
    upvar $varB b
    
    set x $a
    set a $b
    set b $x
    return
}

set PI [expr {acos(-1)}]


 # =====================================================================
 # hatching -- fill a bbox with parallel lines.
 #   theta   :  hatching angle (in degrees)
 #   A       :  amplitude (distance between parallele lines)
 #   bbox    :  bounding-box as a list {bx0 by0 bx1 by1}
 #   lineProc:  callback proc for drawing a line. It takes 4 floats {x0 y0 x1 y1}
 # =====================================================================
proc hatching { theta A bbox {lineProc {}} } {
     # ----------------------------------------
     # --checking and adjusting the parameters
     # ----------------------------------------          
    set theta [expr {$theta/180.0*$::PI}] ;#  now theta is in radians
    
    set A [expr {abs($A)}]
    if { $A < 1e-3 } {
        error "A must be positive"
    }
        
    if { [llength $bbox] != 4 } {
        error "malformed bbox: must be x0 y0 x1 y1"
    }
    lassign $bbox Bx0 By0 Bx1 By1 
    if { $Bx0>$Bx1 } { swap Bx0 Bx1 }
    if { $By0>$By1 } { swap By0 By1 }
    
    # ASSERT:  Bx0<=Bx1 && By0<=Bx0


    if { $lineProc == {} } {
        set lineProc {apply {{args} {}}}   ;# do nothing
    }
    # ASSERT: lineProc is a valid function

    # -- end of parameters checks

    set dx [expr {cos($theta)}]
    set dy [expr {sin($theta)}]

    # if (dx,dy) are both negative, change their sign
    if {$dx <= 0.0 && $dy <= 0.0 } {
        set dx [expr {-$dx}]
        set dy [expr {-$dy}]
    }
    
    # now only one among dx and dy may be negative;
    # if dy is negative, change dx and dy sign
    #  so that dy is positive and dx negative
    if { $dy < 0 } {
        set dx [expr {-$dx}]
        set dy [expr {-$dy}]
    }     
    # ASSERT: (dy>0)
     
    if { abs($dx) < 1e-7 } {
        set isVertical true
        set DY 0.0 ;#  INFINITE
    } else {
        set isVertical false
        set DY [expr {$A/$dx}]
    }

    if { abs($dy) < 1e-7 } {
        set isHorizontal true
        set DX 0.0  ;#  INFINITE
    } else {
        set isHorizontal false
        set DX [expr {$A/$dy}]
    }

    # ASSERT:  if (dx > 0) --> DY >=0 

    # The basic algorithm works for dx>0,dy>0.
    # Note that if both dx and dy are negative,they are inverted.
    # If dx < 0   then swap left/right edge and invert the sign of DX,DY
    if { $dx < 0 } {
        swap Bx0 Bx1    
        set DX [expr {-$DX}]
        set DY [expr {-$DY}]

        # ASSERT:  if (dx < 0 && dy not UNDEF)  DX <= 0
        # ASSERT:  DY >= 0
    }
    # ASSERT: DY >= 0
    
    
    # --------------------------------
    # -- 1) from left edge to top edge
    # --------------------------------
    set x $Bx0
    set y $By1
    set k 0
 
    if { ! $isVertical && ! $isHorizontal } {
        set k [expr {min(int(($Bx1-$Bx0)/$DX),int(($By1-$By0)/$DY))}]

        for {set i 0} {$i<$k} {incr i} {         
            set x [expr {$x+$DX}]
            set y [expr {$y-$DY}]            
            uplevel #0 $lineProc  $Bx0 $y   $x $By1                
        }
    }

    # --------------------------------
    # -- 2) from left edge to right edge
    # --------------------------------
    if { !$isVertical } {       
        # last line was passing through (Bx0,y*)
        #  then on left edge there's space for other k steps
        set k [expr {int(($y-$By0)/$DY)}]

        # compute the y-intersection with the vertical right edge (x=Bx1)    
        set t  [expr {($Bx1-$Bx0)/$dx}]
        set yr [expr {$dy*$t+$y}]

        for {set i 0} {$i<$k} {incr i} {
            set y [expr {$y-$DY}]
            set yr [expr {$yr-$DY}]
            uplevel #0 $lineProc  $Bx0 $y  $Bx1 $yr                
        }
    }

    # --------------------------------
    # -- 3) from bottom edge to top edge
    # --------------------------------
    if { !$isHorizontal } {        
        # last line was passing through (Bx0,y*)
        # compute the x-intersection with the horizontal bottom edge ( y=By0 )
        set t [expr {($By0-$y)/$dy}]
        set xbottom [expr {$dx*$t+$Bx0}]
        set k [expr {int(($Bx1-$x)/$DX)}]

        for {set i 0} {$i<$k} {incr i} {
            set x [expr {$x+$DX}]
            set xbottom [expr {$xbottom+$DX}]
            uplevel #0 $lineProc  $xbottom $By0  $x $By1  
        }
    }

    # --------------------------------
    # -- 4) from bottom edge to right edge
    # --------------------------------
    if { !$isHorizontal && !$isVertical } {           
        # last line was passing through (xbottom,By0)
        # compute the y-intersect with the vertical right edge ( x=Bx1 )

        # how many remaining steps?
        set k [expr {int(($Bx1-$xbottom)/$DX)}]
        
        set t  [expr {($Bx1-$xbottom)/$dx}]
        set y  [expr {$dy*$t+$By0}]
        set x $xbottom

        for {set i 0} {$i<$k} {incr i} {
            set x [expr {$x+$DX}]
            set y [expr {$y-$DY}]
            uplevel #0 $lineProc $x $By0  $Bx1 $y
        }
    }
}

# === TEST ============================================================
if 0 {
canvas .cvs -bg yellow
pack .cvs -fill both -expand true

 # draw xy axis and translate the canvas
.cvs create line 0 -1000 0 1000 -tags {AXIS}
.cvs create line -1000 0 1000 0 -tags {AXIS}
.cvs scan mark 0 0 ; .cvs scan dragto 100 100 1
                                                  
proc drawLine { cvs x0 y0 x1 y1 } {
    $cvs create line $x0 $y0 $x1 $y1 -tags {HATCHING}                             
}
proc printLine { x0 y0 x1 y1 } {
    puts "[format "(%8.1f, %8.1f) (%8.1f, %8.1f)" $x0 $y0 $x1 $y1]"
}

hatching 33 8 { 20 30 213 417 } {drawLine .cvs}
hatching 33 8 { 20 30 213 417 } {printLine}
}
