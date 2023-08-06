
# t2dsvg.tcl
# 
# parse SVG path-data and build an equivalent BL::Path

 # load auxiliary SVGpath module for parsing the input string 
source [file join [file normalize [file dirname [info script]]] SVGpath.tcl]
 
 
namespace eval BL::SVG {   
    proc buildBLPathFromSVGPathD {blPath dataStr} {
        set CXY {0 0}  ;# current point
        set OXY {0 0}  ;# initial point (Origin of the sub-path)

        SVGpath::init $dataStr
        while {1} {
            lassign [SVGpath::getCmdAndArgs] cmd floats
            if { $cmd == "" } break
            
            set CXY [$cmd $blPath {*}$floats]            
        }
        return
    }

    # -------------------------------------------------------------------------
    # --- internal helpers ----------------------------------------------------
    # -------------------------------------------------------------------------
    
     #  args is a sequence of relative coords.
     #  the first coord is relative to the 'base'  b,
     #  ...
     #  the i-th coord is relative to the previous coord
    proc absCoords { b args } {
        lmap x $args {
            set b [expr {$b+$x}]         
        }
    }

     #  args is a sequence of relative coord-pairs.
     #  the first N coord-pairs are relative to the 'base' (bx,by),
     #  ...
     #  then the last coord-pair of every group of N
     #  becomes the base for the next group of N coord-pairs
     # 
     #
    proc absCoordPairs { bx by N args } {
        if { [llength $args] % 2 != 0 } {
            error "**Incomplete coord pairs. Found odd coords."
        }
        set absArgs {}
        set i 1
        foreach {x y} $args {
            set x [expr {$bx+$x}] 
            set y [expr {$by+$y}]
            lappend absArgs $x $y
            if { $i == $N } {
                set bx $x
                set by $y
                set i 1
            } else {
                incr i
            }
       }
       return $absArgs     
    }

    proc coords2coordpairs {args} {
        if { [llength $args] % 2 != 0 } {
            error "**Incomplete coord pairs. Found odd coords."
        }
        lmap {x y} $args {
            list $x $y
        }
    }


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------    
	# INTERNAL procs - they can be called only by buildBLPathFromSVGPathD
	#   since they share its local variables OXY and CXY  
    # -------------------------------------------------------------------------    
    # -------------------------------------------------------------------------

    # Below you can find the implementation of every 'absolute' path commands
    #   M, Z, L, Q, ....
    # All these command must follow these rules:
    #   * the 1st param must be a blPath
    #   * they must return the new 'current point' 
    #      (this is critical for transforming relative-path commands)

    proc M { blPath x y args } {
        upvar OXY OXY
        set OXY [list $x $y]

        set lastP [list $x $y]
        $blPath moveTo $lastP
                
# args must be 2x
if { [llength $args] % 2 != 0 } {
    error "required 2x"
}
        if { $args != {} } {
            set lastP [L $blPath {*}$args]
        }
        return $lastP
    }

    proc Z {blPath} {
        upvar OXY OXY
        $blPath close
        return $OXY
    }

    proc H { blPath args } {
        upvar CXY CXY
        lassign $CXY cx cy

        set points {}
        foreach x $args {
            lappend points [list $x $cy]                        
        }
        $blPath lineTo {*}$points                
        return [list $x $cy]        
    }

    proc V { blPath args } {
        upvar CXY CXY
        lassign $CXY cx cy

        set points {}
        foreach y $args {
            lappend points [list $cx $y]                        
        }
        $blPath lineTo {*}$points                
        return [list $cx $y]        
    }

    proc L { blPath args } {
# args must be 2x
        $blPath lineTo {*}[coords2coordpairs {*}$args]
        return [lrange $args end-1 end]
    }

    proc Q { blPath args } {
# args must be 4x
        $blPath quadTo {*}[coords2coordpairs {*}$args]
        return [lrange $args end-1 end]
    }

    proc C { blPath args } {
# args must be 6x
        $blPath cubicTo {*}[coords2coordpairs {*}$args]
        return [lrange $args end-1 end]
    }

    proc T { blPath args } {
# args must be 2x
        $blPath smoothQuadTo {*}[coords2coordpairs {*}$args]
        return [lrange $args end-1 end]
    }
    proc S { blPath args } {
# args must be 4x
        $blPath smoothCubicTo {*}[coords2coordpairs {*}$args]
        return [lrange $args end-1 end]
    }

    proc A { blPath args } {
# args must be 7x
        foreach {rx ry phi fa fs x y} $args {
            $blPath ellipticArcTo [list $rx $ry] $phi $fa $fs [list $x $y]
        }
        return [lrange $args end-1 end]
    }


     # since Blend2d only works with absolute-path commands,
     # we should translate the relative-path commands in terms of its equivalent ones.

    proc m {blPath args} { upvar CXY CXY; tailcall M $blPath {*}[absCoordPairs {*}$CXY 1 {*}$args] }
    proc z {blPath}      { tailcall Z $blPath }
    proc h {blPath args} { upvar CXY CXY; tailcall H $blPath {*}[absCoords [lindex $CXY 0] {*}$args] }
    proc v {blPath args} { upvar CXY CXY; tailcall V $blPath {*}[absCoords [lindex $CXY 1] {*}$args] }
    proc l {blPath args} { upvar CXY CXY; tailcall L $blPath {*}[absCoordPairs {*}$CXY 1 {*}$args] }
    proc q {blPath args} { upvar CXY CXY; tailcall Q $blPath {*}[absCoordPairs {*}$CXY 2 {*}$args] }
    proc c {blPath args} { upvar CXY CXY; tailcall C $blPath {*}[absCoordPairs {*}$CXY 3 {*}$args] }
    proc s {blPath args} { upvar CXY CXY; tailcall S $blPath {*}[absCoordPairs {*}$CXY 2 {*}$args] }
    proc t {blPath args} { upvar CXY CXY; tailcall T $blPath {*}[absCoordPairs {*}$CXY 1 {*}$args] }
    proc a {blPath args} { 
         #this is tricky because just some of the args should be converted
         # in absolute coords.
        upvar CXY CXY;
         #since I don't want to modify CXY trough its alias, make a copy
        set XY $CXY

        set newArgs {}         
        foreach {rx ry phi fa fs x y} $args {
             # just make absolute the (x,y) point
            set XY [absCoordPairs {*}$XY 1 $x $y]
            lappend newArgs $rx $ry $phi $fa $fs {*}$XY
        }
        tailcall A $blPath {*}$newArgs
    }

}


