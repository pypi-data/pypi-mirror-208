from tkfly.blend2d.demos import run_eval


run_eval("""
set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

wm title . "TclTk binding for Blend2d - Cubicles demo"
set sfc [image create blend2d -format {1000 1000} ] ;# a square sfc
label .x -image $sfc ; pack .x


 # 3d conventions:
 #  XY plane is the vertical 'front plane'
 #  Z-axis is the depth

  # P is a 3d point ; M is a 3x2 mtx ; result is a 2d point
proc PxM { P M } {

	lassign $P px py pz
	lassign $M m00 m01 m10 m11 m20 m21
	
	list [expr {$px*$m00+$py*$m10+$pz*$m20}] [expr {$px*$m01+$py*$m11+$pz*$m21}]
}

# dimetric transf - alpha, beta in degrees

proc dimetricMatrix {alpha beta} {
    set alpha [expr {$alpha*3.1415/180.0}]
    set beta  [expr {$beta*3.1415/180.0}]

    list \
    [expr {cos($alpha)}] [expr {-sin($alpha)}]  \
    0                   1                     \
    [expr {cos($beta)/2}]   [expr {sin($beta)/2}]
}


 # cube of size LxLxL .
 # Origin placed in the center of the cube
 
  # XY is the font plane; Z is depth
proc precomputeCube {size} {
    global Face ;# array  
    global FaceColor ; #array
    
    set Face3D(front)  { {-1 -1 -1} {+1 -1 -1} {+1 +1 -1} {-1 +1 -1} }
    set Face3D(back)   { {-1 -1 +1} {+1 -1 +1} {+1 +1 +1} {-1 +1 +1} }
    set Face3D(left)   { {-1 -1 -1} {-1 -1 +1} {-1 +1 +1} {-1 +1 -1} }
    set Face3D(right)  { {+1 -1 -1} {+1 -1 +1} {+1 +1 +1} {+1 +1 -1} }
    set Face3D(bottom) { {-1 -1 -1} {+1 -1 -1} {+1 -1 +1} {-1 -1 +1} }
    set Face3D(top)    { {-1 +1 -1} {+1 +1 -1} {+1 +1 +1} {-1 +1 +1} }

     #pale yellow
    cubeColors 60 0.5 1.0
     # scale the 3D cube 
    foreach face [array names Face3D] {
        set Q3s {}
        foreach P3 $Face3D($face) {
            set Q3 [lmap c $P3 { expr {$size/2.0*$c} }]
            lappend Q3s $Q3
        }
        set Face3D($face) $Q3s
    }

     # apply the dimetric transformation
     #  from Face3D(..) to Face(..)
    set M [dimetricMatrix 7 42]
    foreach face [array names Face3D] {
        set Face($face) {}
        foreach P3 $Face3D($face) {
            lappend Face($face) [PxM $P3 $M]        
        }    
    }
}


proc cubeColors { h s b } {
    variable FaceColor

    foreach {face color} [list \
        front  [HSB $h $s $b]  \
        back   [HSB $h $s $b]  \
        left   [HSB $h $s [expr {$b*0.7}]]  \
        right  [HSB $h $s [expr {$b*0.8}]]  \
        top    [HSB $h $s [expr {$b*0.9}]]  \
        bottom [HSB $h $s [expr {$b*0.9}]]  \
        ] {
        set FaceColor($face) $color    
    }
}

proc random {a b} {
    expr {$a+($b-$a)*rand()}
}

proc cube {sfc} {
    variable Face
    variable FaceColor

    $sfc push
    
    if { 3*rand() < 1.0 } {
        set isTransparent true
        $sfc configure -globalalpha 0.5

       # trasparent cubes should be smaller..
        set M [$sfc cget -matrix]
        set OXY [Mtx::PxM {0 0} $M]
       $sfc configure -matrix [Mtx::post_scaling $M 0.93 0.93 $OXY]


       set hue [random 100 180]
       set frontColor [HSB $hue 1 0.8]
       set rightColor [HSB $hue 1 0.6]
       set topColor [HSB $hue 1 0.6]
              
      set lineColor [HSB $hue 0.2 0.8] 
       
    } else {
        set isTransparent false
        $sfc configure -globalalpha 1.0
        set frontColor $FaceColor(front)
       set rightColor $FaceColor(right)
       set topColor $FaceColor(top)
       # solid cubes should be a little bit (random) bigger ..
        set M [$sfc cget -matrix]
        set OXY [Mtx::PxM {0 0} $M]
        set size [expr {1.0+(rand()*0.2)}] ; # 1.0 .. 1.2
        $sfc configure -matrix [Mtx::post_scaling $M $size $size $OXY]

      lassign [RGB2HSB $FaceColor(front)] h s b
      # b lerp(b,1,30%)
      set b [expr {$b+(1-$b)*0.3}]  
      set lineColor [HSB $h $s $b] 
    }
    
    if { $isTransparent } {   
         # draw the back faces
        $sfc fill [BL::polygon {*}$Face(back)]   -style $FaceColor(back)
        $sfc fill [BL::polygon {*}$Face(left)]   -style $FaceColor(left)
        $sfc fill [BL::polygon {*}$Face(bottom)] -style $FaceColor(bottom)
    }    
     # draw the front faces
    $sfc fill [BL::polygon {*}$Face(top)]    -style $topColor
    $sfc fill [BL::polygon {*}$Face(right)]  -style $rightColor 
    $sfc fill [BL::polygon {*}$Face(front)]  -style $frontColor 

     # stroke the front edges
# todo: avoid to stroke the edges twice  (bad antialiasing)     

    $sfc configure -stroke.style $lineColor ;#0xFF222222
    $sfc stroke [BL::polygon {*}$Face(top)]   
    $sfc stroke [BL::polygon {*}$Face(right)]
    $sfc stroke [BL::polygon {*}$Face(front)]
    $sfc pop
}


# ---------- main -----------------------------------------------------------

 # precompute the projected faces of the cube
#  ... to to .. split set Cube3d a precompute projections..

set DM [dimetricMatrix 7 42]
 lassign [$sfc size] WX WY
set DX 88 ;# cube size

precomputeCube $DX
$sfc clear
set OM [Mtx::translation [expr {$WX/2.0}] [expr {$WY/2.0}]] ; # origin at the center
set OM [Mtx::MxM [Mtx::yreflection] $OM]
$sfc configure -matrix $OM

$sfc configure -stroke.width 1.0

proc cubeOfCubes {sfc WX DX} {
	variable STOP
    variable OM
    variable DM

set STOP false
	# background
	$sfc fill all -style [BL::gradient RADIAL [list 0 0 0 0 [expr {4.0/5.0*$WX}]] \
		[list 0 [HSB 120 1.0 0.6] 0.9 [HSB 120 1.0 0.2] ]]
    
    $sfc push
    for {set z [expr {-$WX/5.0}]} {$z<=$WX/5.0*1.5} {set z [expr {$z+$DX}]} {
        for {set y [expr {-$WX/5.0}]} {$y<=$WX/5.0} {set y [expr {$y+$DX}]} {
            for {set x [expr {-$WX/5.0}]} {$x<=$WX/5.0} {set x [expr {$x+$DX}]} {
                #.. every 10%, skip a cube  ...
                if { rand() <0.1 } continue

                $sfc configure -matrix [Mtx::translate $OM {*}[PxM [list $x $y [expr {-$z}]] $DM]]
                cube $sfc
                if { $STOP } return
                 # refresh the scene 
				after 10; update
            }
        }
    }
                                                   
    $sfc pop
}

cubeColors 120 0.8 0.3

# repeat on every click
bind . <ButtonPress-1> { 
	set STOP true;
	 # NOTE: this is not a clever sync method , anyway ... 
	 # we should wait until the running cubeOfCubes ends.
	 # Knowing that cubeOfCubes has a sleeping time of 10 ms, we must set a start-time after 11 ms  
	after 11 cubeOfCubes $sfc $WX $DX 
}
set STOP false
cubeOfCubes $sfc $WX $DX
""")
