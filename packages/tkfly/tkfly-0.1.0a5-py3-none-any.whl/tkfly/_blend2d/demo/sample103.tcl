set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

package require Blend2d

set WIDTH 600
set HEIGHT $WIDTH

wm title . "TclTk binding for Blend2d - Dodecagon demo"
set sfc [image create blend2d -format [list $HEIGHT $WIDTH]]
label .x -image $sfc ; pack .x




set PI [expr {acos(-1.0)}]

proc degToRad {deg} {
    global PI
    expr {$deg/180.0*$PI}
}

set Theta [degToRad 30.0]  ;#  360/12 = 30 dgrees

 # return a new BLPath with  a dodecagon 
proc dodecagon { radius } {
    global PI
    global Theta

     # square size    
    set L [expr {$radius*sin($Theta/2.0)*sqrt(2.0)}]
    
    set centerQ [list [expr {$radius*cos($Theta/2.0)}] 0.0]
    set M [Mtx::translation {*}$centerQ]
    set M [Mtx::post_rotate $M 45 degrees  $centerQ]

    set halfL [expr {$L/2.0}]    
    set Square [BL::rect -$halfL -$halfL $L $L]
    
    set path [BL::Path new]
    
    for {set i 0} {$i<12} {incr i} {
        $path add $Square -matrix $M
        set M [Mtx::post_rotate $M $Theta radians]
    }

    return $path
}


set R [expr {$WIDTH/2.0-20}]  ;# radius of the bigger dodecagon

# some temporary math ..
    # a dodecagon of radius R has 12 sides of length 2*R*sin(Theta/2)
    #  this is also the size of the diagonal of the rotated square,
    # therefore the square size is that diagonal divided by sqrt(2) ....
      set L [expr {$R*sin($Theta/2.0)*sqrt(2.0)}] ;# square size (for dodec of radius R)
   # the inner dodecagon should have a radius R0
  set R0 [expr {$R*cos($Theta/2.0)-($L/sqrt(2.0))}]

 # Z is the ratio between a dodecagon and its inner dodecagon ..
 # 1/Z is the ratio between a dodecagon and its outer dodecagon
set Z [expr {$R0/$R}]
set Z_1 [expr {1.0/$Z}]


set basicDodecagon [dodecagon $R]

set MD [Mtx::identity]
set fullPath [BL::Path new]
set N 10 ;# number of nested dodecagons
for {set i 0} {$i < $N} {incr i} {
    $fullPath add $basicDodecagon -matrix $MD

     # the inner dodecagon should be
     #  scaled by $Z and rotated 15 degrees
    set MD [Mtx::post_scaling $MD $Z $Z]
    set MD [Mtx::post_rotate $MD [expr {$Theta/2.0}] radians]
}
$basicDodecagon destroy ;# free mem

 # place the origin at the center of the surface
set M  [Mtx::translation [expr {$WIDTH/2.0}] [expr {$HEIGHT/2.0}]]
$sfc configure -matrix $M


 # transparent background
$sfc clear -style 0x0

$sfc fill $fullPath -style 0xFFE11A1A
 # shadow
$sfc fill $fullPath -style 0x40000000  -compop DST_OVER  -matrix [Mtx::translate $M 2 4]
$sfc fill $fullPath -style 0x20000000  -compop DST_OVER  -matrix [Mtx::translate $M 4 6]

 # background with a pale gradient
$sfc fill all -compop DST_OVER -style \
    [BL::gradient LINEAR \
        [list 0.0 [expr {-$HEIGHT/2.0}] 0.0 [expr {$HEIGHT/1.5}]] \
        {0  0xFFFFFDCC 1 0xFFFFFFEE} ]

$fullPath destroy ;# free mem
