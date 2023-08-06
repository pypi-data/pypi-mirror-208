from tkfly.blend2d.demos import run_eval

run_eval("""
set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname [file dirname $thisDir]]]

# Composition Test ===========================================================

package require Blend2d

proc prepareChessboardPattern {filename} {
    set sfc [BL::Surface new]
    $sfc load $filename
    return [BL::pattern $sfc]
}
 
 # WARNING: chessboard pattern should be applied at the end for filling (semi)transparent pixels
 # After drawing a chessboard pattern, transparent pixels are lost !
proc drawChessboard {sfc BLpattern} {
    $sfc fill all \
        -compop DST_OVER \
        -style $BLpattern
}

 #draw a colorWheel
proc colorWheel {sfc xc yc radius} { 
    $sfc fill [BL::circle [list $xc $yc] $radius] \
        -style [BL::gradient CONICAL [list $xc $yc [expr {-3.1415/6}]] \
            {0 0xFFFF0000  0.166 0xffffff00 0.333 0xff00ff00 0.5 0xFF00FFFF 0.666 0XFF0000FF 0.8333 0xffff00ff  1 0xffFF0000}]
}

 #draw a faded ColorWheel
 # PLUS a BLUE 20x20 SQUARE at 12,12
proc fadedColorWheel {sfc xc yc radius} {
    colorWheel $sfc $xc $yc $radius
    
    $sfc fill [BL::circle [list $xc $yc] [expr {$radius+2.0}]] \
        -compop DST_IN \
        -style [BL::gradient RADIAL [list $xc $yc $xc $yc $radius] {0 0xFFFFFFFF 0.40 0xFFFFFFFF 0.70 0xDDDDDDDD 1 0x00000000}]
    $sfc fill [BL::rect 12 12 20 20] -style 0xFF0000FF
}


 # return a new Surface
 # with 3 circles R G B    (G at top, R,B below)
 # plus
 # a 20x20 RED square at 2,2
proc precomputeRGBimage {dx dy radius} {
    set sfc [BL::Surface new -format [list $dx $dy PRGB32]]
    $sfc fill all -compop SRC_COPY -style 0x00 ;# transparent

    $sfc fill [BL::rect 2 2 20 20] -style [BL::color #FF0000]

    set M  [Mtx::identity]
    set M  [Mtx::translate $M [expr {$dx/2.0}] [expr {$dy/2.0}]] 
    set M  [Mtx::scaling $M 1.0 -1.0]  ;# invert Y

    $sfc configure -matrix $M
    set C [list [expr {$radius/1.3}] 0] ;# centre of circle
     #  GREEN
    set M [Mtx::rotate $M 90 degrees]
    $sfc fill [BL::circle $C $radius] -style [BL::color #00FF00] -compop PLUS -matrix $M
     #  RED
    set M [Mtx::rotate $M 120 degrees]
    $sfc fill [BL::circle $C $radius] -style [BL::color #FF0000] -compop PLUS -matrix $M
     #  BLUE
    set M [Mtx::rotate $M 120 degrees]
    $sfc fill [BL::circle $C $radius] -style [BL::color #0000FF] -compop PLUS -matrix $M
    return $sfc
}

# =============================================

set COMPOPS [BL::enum COMP_OP]

proc Next {} {
    variable COMPIDX
    variable COMPOPS

    incr COMPIDX
    if {$COMPIDX == [llength $COMPOPS] } {set COMPIDX 0}
    return $COMPIDX
}
proc Prev {} {
    variable COMPIDX
    variable COMPOPS

    incr COMPIDX -1
    if {$COMPIDX < 0 } { set COMPIDX [llength $COMPOPS] ; incr COMPIDX -1 }
    return $COMPIDX
}

variable COMPIDX 0

proc drawComposition {idx srf} {
    variable WIDTH
    variable HEIGHT
    variable COMPOP
    variable COMPOPS
    variable BLchessboardPattern
    variable SRF_RGBcircles    

    set COMPOP [lindex $COMPOPS $idx]
    
    # reset bg (fill with transparent color)
    $srf fill all -compop SRC_COPY -style 0    
    fadedColorWheel $srf [expr {$WIDTH/2.0}] [expr {$HEIGHT/2.0}] [expr {$HEIGHT/2.0}]
    # draw theRGBcircles with the given COMPOP
    $srf copy $SRF_RGBcircles -compop $COMPOP
    
    drawChessboard $srf $BLchessboardPattern
}


# = prepare ..
#      BLchessboardPattern
#      SRF_RGBcircles  (surface-buffer WIDTHxHEIGHT)
#      BLimage   (the drawing surface WIDTHxHEIGHT)
set WIDTH  400
set HEIGHT 400
set BLchessboardPattern [prepareChessboardPattern $thisDir/chessboard.png] 
 # 100 is the radius of each single circle 
set SRF_RGBcircles [precomputeRGBimage $WIDTH $HEIGHT 100.0]

set BLimage [image create blend2d -format [list $WIDTH $HEIGHT PRGB32]]
$BLimage fill all

# = GUI ====================================================================

label .sfc -image $BLimage
label .mode -textvariable COMPOP
pack .sfc
pack .mode

button .prev -text "Prev" -command {drawComposition [Prev] image1}
button .next -text "Next" -command {drawComposition [Next] image1}
pack .prev .next  -side left -expand 1

drawComposition $COMPIDX image1

""")
