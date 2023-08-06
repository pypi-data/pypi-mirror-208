set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname [file dirname $thisDir]]]

# Porter-Duff in Action
# TclTk + Blend2d poting from 
#   https://ciechanow.ski/alpha-compositing/
#   by Bartosz Ciechanowski
#

package require Blend2d


proc prepareChessboardPattern {filename} {
    set sfc [BL::Surface new]
    $sfc load $filename
    return [BL::pattern $sfc]
}

proc drawStep {surf step {debug true}} {
    if {$step < 0 } { set step 0 }

    lassign [$surf size] W H

    $surf configure -matrix [Mtx::identity]
        
    if { $step >= 0 } {
        set msg "CLEAR"
        $surf fill all -compop CLEAR
    }
    
    set mtx [Mtx::translation [expr {$W/2.0}] [expr {$H/2.0}]]
    $surf configure -matrix $mtx
     # default setting ( mainly used for debug stroking )
    $surf configure -stroke.width 4 -stroke.style [BL::color #2968FF] \
        -compop SRC_OVER  

    set radius [expr {$H/3.0}]

     # step 1 - circle
    if { $step >= 1 } {
        set msg "SRC_OVER orange circle"
        $surf fill [BL::circle {0 0} $radius] -style [BL::color #EC6D44] -compop SRC_OVER
    }
    if { $step == 1 && $debug } {
        $surf stroke [BL::circle {0 0} $radius]
    }

     # step 2
    if { $step >= 2 } {
        set msg "SRC_ATOP  two rotated white rectangles"
        set w [expr {$W/12.0}]
        set rect [BL::rect [expr {-$w/2.0}] [expr {-$radius}] $w [expr {2*$radius}]]
        $surf fill $rect -style [BL::color #f5f5f5] -matrix [Mtx::rotate $mtx +45 degrees] -compop SRC_ATOP
        $surf fill $rect -style [BL::color #f5f5f5] -matrix [Mtx::rotate $mtx -45 degrees] -compop SRC_ATOP
    }
    if { $step == 2 && $debug } {
        $surf stroke $rect -matrix [Mtx::rotate $mtx +45 degrees]
        $surf stroke $rect -matrix [Mtx::rotate $mtx -45 degrees]
    }

    set r1 [expr {$radius*3/5.5}]  ;# internal radius
    
     # step 3
    if { $step >= 3 } {
        set msg "SRC_ATOP radial gradient square"
          # these are the original stops from Bartosz Ciechanowski's work.
          # they are for a radial gradient on an annulus from radius R1 to radius R2
          # ..
          # We need to transform the "c" coeff so that they work for a radial gradient
          # on a circle of raius R2 
          # c R G B A
        set origStops {
          0.0   0 0 0 0.7
          0.1  0 0 0 0.4
          0.15 0 0 0 0.15
          0.2  0 0 0 0.1
          0.35 0 0 0 0.03
          0.4  0 0 0 0.01
          0.5  0 0 0 0.0
          0.6  0 0 0 0.01
          0.65 0 0 0 0.03
          0.8  0 0 0 0.1
          0.85 0 0 0 0.15
          0.9  0 0 0 0.3
          1.0  0 0 0 0.7
        }

         # rescale stops from radius r1..r2 to 0..r2
        proc rescaleStops { stops r1 r2 } {
            set dr [expr {$r2-$r1}]
            set L {}
            lappend L 0.0  0xFF000000
                foreach {c R G B A} $stops {
                    set argb [format "0x%02X%02X%02X%02X"  [expr {int($A*255)}] [expr {int($R*255)}] [expr {int($G*255)}] [expr {int($B*255)}]]

                    set x [expr {($r1+$c*($r2-$r1))/$r2}]
                    lappend L  $x  $argb
                }   
            return $L
        }


        set newStops [rescaleStops $origStops [expr {$r1-3}] [expr {$radius+3}]]

        set gradient [BL::gradient RADIAL [list 0 0 0 0 [expr {$H/3.0+3}]] $newStops]
        set rect [BL::rect [expr {-$radius-1}] [expr {-$radius-1}] [expr {2*$radius+2}] [expr {2*$radius+2}]]
        $surf fill $rect -style $gradient -compop SRC_ATOP
        # if you repeat it, shadows are more evident
    }
    if { $step == 3 && $debug } {
        $surf stroke $rect
    }
    
    # step 4
    if { $step >= 4 } {
        set msg "DST_OUT circle"
        $surf fill [BL::circle {0 0} $r1] -style [BL::color #000000] -compop DST_OUT
    }
    if { $step == 4 && $debug } {
        $surf stroke [BL::circle {0 0} $r1]
    }
    
     
    # step 5 - shadow
    if { $step >= 5 } {
        set msg "DST_OVER transparent black stroked circle"
         # draw an annulus:
         #  stroke a circle of radius r having a lineWidth of w
        set r [expr {($radius+$r1)/2.0}]
        set w [expr {$radius-$r1}]
         #  ok; orgin of the circle is translated
        set geom [BL::circle [list [expr {-$H/28}] [expr {$H/28}]] $r]
        $surf stroke $geom -style [BL::color black 0.4] -width $w -compop DST_OVER
    }
    if { $step == 5 && $debug } {
        $surf stroke $geom
    }
    
    # setp 6 -onde
    if { $step >= 6 } {
        set msg "SRC_OVER transparent white stroked circles"
        $surf push
        $surf configure -compop SRC_OVER -stroke.width 2

        set r [expr {($radius+$H*0.62)/2.0}]
        $surf stroke [BL::circle {0 0} $r] -style [BL::color #FFFFFF 0.1]
        set r [expr {$r+$H*0.15}]
        $surf stroke [BL::circle {0 0} $r] -style [BL::color #FFFFFF 0.07]
        set r [expr {$r+$H*0.15}]
        $surf stroke [BL::circle {0 0} $r] -style [BL::color #FFFFFF 0.03]

        $surf pop
    }
    if { $step == 6 && $debug } {
        set r [expr {($radius+$H*0.62)/2.0}]
        $surf stroke [BL::circle {0 0} $r]
        set r [expr {$r+$H*0.15}]
        $surf stroke [BL::circle {0 0} $r]
        set r [expr {$r+$H*0.15}]
        $surf stroke [BL::circle {0 0} $r]
    }

     # step 7
    if { $step >= 7 } {
        set msg "CLEAR outside ellipse"
        
        set r [expr {($radius+$H/2.0)/2.0}]
         
if 0 {
          # NOTE : in Blend2d this does not work...
         set r [expr {($radius + $H/2.0)/2.0}]
         $surf fill [BL::ellipse {0 0} [expr {2*$r}] $r] -style 0xFFFFFFFF -compop DST_IN
} else {
         # alternative trick for Blend2d
        set p [BL::Path new]
        $p add [BL::box [list [expr {-$W/2}] [expr {-$H/2}]] [list $W $H]]
        $p add [BL::ellipse {0 0} [expr {2*$r}] $r] -direction CCW
        $surf fill $p -compop CLEAR
        $p destroy
}
    } 
    if { $step == 7 && $debug } {
         $surf stroke [BL::ellipse {0 0} [expr {2*$r}] $r]
    }

     # step 8
    if { $step >= 8 } {
        set msg "DST_OVER blue rectangle"
        $surf fill all -style 0xFF2052BB -compop DST_OVER
    }    

     # limit step ..
    if { $step > 8 } { set step 8 }

    # -------------------------------------------------------------------------
 
 
    set ::LABELMSG "Step ${step}/8 - $msg"    
     # draw transparency chess board below ..
    $surf fill all \
        -compop DST_OVER \
        -style $::bgChessBoardPattern

    return $step
}

 # ==== MAIN =================================================================
set thisDir [file dirname [file normalize [info script]]]


wm title . "Porter-Duff in Action"
pack [label .topLabel \
    -text "Click on the right half of the image to advance, on the left half to go back."
    ] -pady 3
    
set surf [image create blend2d -format {600 400}]
pack [label .surf -image $surf]
set bgChessBoardPattern [prepareChessboardPattern $thisDir/chessboard.png]

set LABELMSG ""
pack [label .label -textvariable LABELMSG] -expand 1 -fill x -pady 3


bind .surf <Button-1> {
    if {%x < [winfo width %W]/2} {
        incr STEP -1
    } else {
        incr STEP
    }
    set STEP [drawStep $surf $STEP]    
}

set STEP 0
drawStep $surf $STEP

 # on exit: 
# $bgChessBoardPattern destroy
# $surf destroy
