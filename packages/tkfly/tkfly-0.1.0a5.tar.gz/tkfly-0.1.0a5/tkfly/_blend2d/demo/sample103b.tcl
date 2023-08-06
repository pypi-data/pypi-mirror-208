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

wm title . "TclTk binding for Blend2d - Dodecagon demo - variant B"
set sfc [image create blend2d -format [list $HEIGHT $WIDTH]]
label .x -image $sfc ; pack .x


set PI [expr {acos(-1.0)}]

proc degToRad {deg} {
    global PI
    expr {$deg/180.0*$PI}
}

set Theta [degToRad 30.0]  ;#  360/12 = 30 degrees

 # draw all the 12 squares on the sides of a dodecagon 
proc dodecagon { sfc radius pattern } {
    global PI
    global Theta

     # square size    
    set L [expr {$radius*sin($Theta/2.0)*sqrt(2.0)}]
     # center of the first square (at 0 degrees)
    set centerQ [list [expr {$radius*cos($Theta/2.0)}] 0.0]

    set halfL [expr {$L/2.0}]
     # this is the basic shape; a square centered at 0,0 ;
     # it will be placed and rotated on the circle    
    set Square [BL::rect -$halfL -$halfL $L $L]

    $sfc push
    set M [$sfc cget -matrix]    
    for {set i 0} {$i<12} {incr i} {
         # MQ is the Matrix transf for the Square
        set MQ [Mtx::translate $M {*}$centerQ]
        set MQ [Mtx::rotate $MQ 45 degrees]

         # collimate the fill-pattern origin with the Square vertex
         #  note that pattern will take the same rotation of MQ
        $sfc push
        $sfc configure -matrix [Mtx::translate $MQ $halfL $halfL]
        $sfc configure -fill.style $pattern
        
         # ====  draw the square =========================
        $sfc fill $Square -matrix $MQ
         # ===============================================
        $sfc pop        

         #shadow - very simple ...
        set MS [Mtx::post_translate $MQ 2 4]
        $sfc fill $Square -style 0x40000000  -compop DST_OVER  -matrix $MS
        set MS [Mtx::post_translate $MQ 4 6]
        $sfc fill $Square -style 0x20000000  -compop DST_OVER  -matrix $MS

         # next loop, rotate M
        set M [Mtx::rotate $M $Theta radians]
    }
    $sfc pop
}


set R [expr {$WIDTH/2.0-20}]  ;# radius of the biggest dodecagon

# some temporary math ..
    # Each side of a dodecagon takes an angle Theta = 360/12 = 30.
    # A dodecagon of radius R has 12 sides of length 2*R*sin(Theta/2)
    #  this is also the size of the diagonal of the rotated square,
    # thefore the square size is that diagonal divided by sqrt(2) ....
      set L [expr {$R*sin($Theta/2.0)*sqrt(2.0)}] ;# square size (for dodec of radius R)
    # The inner dodecagon should have a radius R0
      set R0 [expr {$R*cos($Theta/2.0)-($L/sqrt(2.0))}]

    # Z is the ratio between a dodecagon and its inner dodecagon ..
    # 1/Z is the ratio between a dodecagon and its outer dodecagon
set Z [expr {$R0/$R}]
set Z_1 [expr {1.0/$Z}]

 # prepare a BL::pattern for filling the squares
set patternSfc [BL::Surface new]
$patternSfc load $thisDir/greenSlate.jpg
set pattern [BL::pattern $patternSfc]


 # place the origin at the center of the surface
set M [Mtx::translation [expr {$WIDTH/2.0}] [expr {$HEIGHT/2.0}]]
$sfc configure -matrix $M

$sfc push ;# save the status since we'are going to touch the transformation matrix

 # transparent bg
$sfc fill all -style 0x0

set N 10 ;# number of nested dodecagons ...  it's your choice ..
for {set i 0} {$i < $N} {incr i} {
    dodecagon $sfc $R $pattern

     # the inner dodecagon should be
     #  scaled by $Z and rotated 15 degrees
    set R [expr {$R*$Z}]
    set M [Mtx::rotate $M [expr {$Theta/2.0}] radians]
    $sfc configure -matrix $M
}
$sfc pop ;#  restore the status

 # background with a pale gradient
$sfc fill all -compop DST_OVER \
    -style \
    [BL::gradient LINEAR \
        [list 0.0 [expr {-$HEIGHT/2.0}] 0.0 [expr {$HEIGHT/1.5}]] \
        [list 0  [HSB 0 0.4 0.7] 1 [HSB 10 0.5 0.9]] ]


# clean up ---
$patternSfc destroy
