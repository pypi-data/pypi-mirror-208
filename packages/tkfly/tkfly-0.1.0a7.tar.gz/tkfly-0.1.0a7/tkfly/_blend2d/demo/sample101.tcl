set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

# --sample101 - demo

package require Blend2d

set sfc [image create blend2d -format {500 600} ]
label .x -image $sfc ; pack .x

set fontFace [BL::FontFace new "$thisDir/Blacksword.otf"]
set font [BL::Font new $fontFace 50.0]

set txtPath [BL::Path new]
foreach glyphIdx [$font glyphs "A"] {
    set gPath [$font glyph $glyphIdx]
    $txtPath add $gPath
    $gPath destroy
}


$sfc clear -fill.style [BL::color gray90]

$sfc configure -stroke.style [BL::color gray20] -compop SRC_OVER

 # print an header
$sfc fill [BL::text {20 50} $font "Font: Blacksword.otf"]

 # resize txtPath under the Header
$txtPath fitTo {20 100 460 460}
$sfc stroke $txtPath

BL::Path create arrow

proc resize&rotate {arrow len theta} {
    $arrow reset
    $arrow moveTo {0 0}
    set arrowEnd [list $len 0]
    $arrow lineTo $arrowEnd
    $arrow lineTo [list [expr {$len-3}] 2]
    $arrow lineTo [list [expr {$len-3}] -2]
    $arrow lineTo $arrowEnd
    $arrow close
    $arrow apply [Mtx::rotation $theta radians]
}

 # for each basic curve
 #  plot a red circle at B(0.25), B(0.5), B(0.75), B(1.0)
 #   (for t == 0.0 circle should be bigger)
 #  plot the normal
$sfc configure -fill.style [BL::color red 0.7]
$sfc configure -stroke.style [BL::color green 0.8]
foreach t {0.0 0.25 0.50 0.75 1.0} {
    if { $t == 0.0 } {
        set dotSize 5.0
    } else {
        set dotSize 2.5    
    } 

     # the command
     #    $txtPath contour * * normalAt $t
     # returns for each contour a list of {Point Direction} evaluated at B(t) of every curve.
    foreach contour [$txtPath contour * * normalAt $t] {
        foreach PN $contour {
            lassign $PN P N
            lassign $N dx dy

            $sfc fill [BL::circle $P $dotSize]
                        
            resize&rotate arrow 20 [expr {atan2($dy,$dx)}]
            $sfc stroke arrow -matrix [Mtx::translation {*}$P]        
        }
    }
}

arrow destroy

$txtPath destroy
$font destroy
$fontFace destroy
