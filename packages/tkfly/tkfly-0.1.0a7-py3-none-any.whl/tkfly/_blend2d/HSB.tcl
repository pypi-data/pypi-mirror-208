package provide HSB 1.0

##  HSB.tcl
##
##	utilities for color processing
##             RGB <--> HSB 
##
##
## This library is free software; you can use, modify, and redistribute it
## for any purpose, provided that existing copyright notices are retained
## in all copies and that this notice is included verbatim in any
## distributions.
##

#  HSB h s b ?a?       --> 0xAARRGGBB 
#  RGB2HSB 0xAARRGGBB  --> { h s b a }


  # General info
  #
  #   h (hue)  is a 0.0..360.0 angle
  #   s (saturation)  is 0.0 .. 1.0
  #   b (brigthess)   is 0.0 .. 1.0  ( 0 is black, 1 is white )
  #
  #  alpha is 0.0 .. 1.0  



# hue:  any angle in degrees (internally normalized to 0.0..360)
# sat:  0.0 .. 1.0
# brigthness: 0.0 .. 1.0
# 
# returns:
#   a 32bit ARGB color as 0xAARRGGBB
 
proc HSB {hue sat val {alpha 1.0}} {
    set alpha [expr {round($alpha*255.0)}]
    set v [expr {round(255.0*$val)}]
    if {$sat == 0.0} {
    	return [expr {$alpha<<24 | $v<<16 | $v<<8 | $v}]
    }
    while { $hue < 0 } {
        set hue [expr {$hue+360.0}]
    }
    set hue [expr {fmod($hue,360.0)}]
    set hueSector [expr {$hue/60.0}]    ;# result is 0.0...5.999
	set i [expr {int($hueSector)}]
	set f [expr {$hueSector-$i}]
	set p [expr {round(255.0*$val*(1 - $sat))}]
    set q [expr {round(255.0*$val*(1 - ($sat*$f)))}]
    set t [expr {round(255.0*$val*(1 - ($sat*(1 - $f))))}]
    switch $i {
	    0 {return [expr {$alpha<<24 | $v<<16 | $t<<8 | $p}]}
	    1 {return [expr {$alpha<<24 | $q<<16 | $v<<8 | $p}]}
	    2 {return [expr {$alpha<<24 | $p<<16 | $v<<8 | $t}]}
	    3 {return [expr {$alpha<<24 | $p<<16 | $q<<8 | $v}]}
	    4 {return [expr {$alpha<<24 | $t<<16 | $p<<8 | $v}]}
	    5 {return [expr {$alpha<<24 | $v<<16 | $p<<8 | $q}]}
    }
}

# input is
#    a 32bit ARGB color as 0xAARRGGBB
#
# returns a list { hue sat brightness alpha }
#   hue: 0.0 .. 360.0
#   sat: 0.0 .. 1.0
#   brigthness: 0.0 .. 1.0
#   alpha: 0.0 .. 1.0
proc RGB2HSB { aarrggbb } {
    set alpha [expr {$aarrggbb>>24 & 0xFF}]
    set red   [expr {$aarrggbb>>16 & 0xFF}]
    set green [expr {$aarrggbb>>8  & 0xFF}]
    set blue  [expr {$aarrggbb     & 0xFF}]

    if {$red > $green} {
        set max $red
        set min $green
    } else {
        set max $green
        set min $red
    }
    if {$blue > $max} {
        set max $blue
    } else {
        if {$blue < $min} {
            set min $blue
        }
    }
    set range [expr {double($max-$min)}]
    if {$max == 0.0} {
        set sat 0.0
    } else {
        set sat [expr {$range/$max}]
    }
    if {$sat == 0.0} {
        set hue 0.0
    } else {
        set rc [expr {($max - $red)/$range}]
        set gc [expr {($max - $green)/$range}]
        set bc [expr {($max - $blue)/$range}]
        if {$red == $max} {
            set hue [expr {60.0*($bc - $gc)}]
        } else {
            if {$green == $max} {
                set hue [expr {60*(2 + $rc - $bc)}]
            } else {
                set hue [expr {.166667*(4 + $gc - $rc)}]
            }
        }
        if {$hue < 0.0} {
            set hue [expr {$hue + 360.0}]
        }
    }
    return [list $hue $sat [expr {$max/255.0}] [expr {$alpha/255.0}]]
}

