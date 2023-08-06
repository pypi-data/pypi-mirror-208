 # The original version
 #  was based on a single BLPath
 #  therefore the fill style was costants (solid, gradient, pattern).
 #
 # This variant split the single BLPath in single tiles (Squares), so that
 #  they can be filled with different styles.
 
set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

package require Blend2d

set WIDTH 600
set HEIGHT $WIDTH

wm title . "TclTk binding for Blend2d - Dodecagon demo - variant A"
set sfc [image create blend2d -format [list $HEIGHT $WIDTH]]
label .x -image $sfc ; pack .x


proc random {a b} {
    expr {$a+($b-$a)*rand()}
}


set PI [expr {acos(-1.0)}]

proc degToRad {deg} {
    global PI
    expr {$deg/180.0*$PI}
}

set Theta [degToRad 30.0]  ;#  360/12 = 30 degrees

 # draw all the 12 squares on the sides of a dodecagon 
proc dodecagon { sfc radius } {
    global PI
    global Theta

     # square size    
    set L [expr {$radius*sin($Theta/2.0)*sqrt(2.0)}]
    
    set centerQ [list [expr {$radius*cos($Theta/2.0)}] 0.0]

    set M [$sfc cget -matrix]

    set halfL [expr {$L/2.0}]    
    set Square [BL::rect -$halfL -$halfL $L $L]
    
    for {set i 0} {$i<12} {incr i} {
        set MQ [Mtx::translate $M {*}$centerQ]
        set MQ [Mtx::rotate $MQ 45 degrees]

        set hue [random -10 10] ;# red(0)  +/-10
        set saturation [random 0.6 0.9]
        set color [HSB $hue $saturation 0.8]
        
        $sfc fill $Square -matrix $MQ \
            -style $color

        set M [Mtx::rotate $M $Theta radians]
    }
}


set R [expr {$WIDTH/2.0-20}]  ;# radius of the bigger dodecagon

# some temporary math ..
    # a dodecagon of radius R has 12 sides of length 2*R*sin(Theta/2)
    #  this is also the size of the diagonal of the rotated square,
    # thefore the square size is that diagonal divided by sqrt(2) ....
      set L [expr {$R*sin($Theta/2.0)*sqrt(2.0)}] ;# square size (for dodec of radius R)
   # the inner dodecagon should have a radius R0
  set R0 [expr {$R*cos($Theta/2.0)-($L/sqrt(2.0))}]

 # Z is the ratio between a dodecagon and its inner dodecagon ..
 # 1/Z is the ratio between a dodecagon and its outer dodecagon
set Z [expr {$R0/$R}]
set Z_1 [expr {1.0/$Z}]



 # place the origin at the center of the surface
set M [Mtx::translation [expr {$WIDTH/2.0}] [expr {$HEIGHT/2.0}]]
$sfc configure -matrix $M

 # background with a pale gradient
$sfc clear -style \
    [BL::gradient LINEAR \
        [list 0.0 [expr {-$HEIGHT/2.0}] 0.0 [expr {$HEIGHT/1.5}]] \
        {0  0xFFFFFDCC 1 0xFFFFFFEE} ]

$sfc push ;# save the status since we'are going to touch the transformation matrix
set N 10 ;# number of nested dodecagons
for {set i 0} {$i < $N} {incr i} {
    dodecagon $sfc $R

     # the inner dodecagon should be
     #  scaled by $Z and rotated 15 degrees
    set R [expr {$R*$Z}]
    set M [Mtx::rotate $M [expr {$Theta/2.0}] radians]
    $sfc configure -matrix $M
}
$sfc pop ;#  restore the status