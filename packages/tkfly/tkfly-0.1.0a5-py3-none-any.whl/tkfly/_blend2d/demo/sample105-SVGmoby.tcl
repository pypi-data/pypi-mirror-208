#  Extract from a SVG file
#  the geometry properties "d" of each <path> element
#  and convert it in a BL::Path

set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

if { [catch {
    package require tdom
    } errMsg ] } {
        tk_messageBox -icon error -message "This demo requires package \"tdom\""
        exit    
    }

package require Blend2d

namespace eval  simpleSVGparser {
    variable D_PROP ""
    
     # expat callback:
     #  if element is "path", append to D_PROP list the contents of the attribute "d"
    proc _ElementStartCb {name attribs} {
        variable D_PROP
        if { $name eq "path" } {
            if { [dict exists $attribs "d"] } {
                lappend D_PROP  [dict get $attribs "d"]
            }
        }
    }

     # return a list of strings; 
     # each string is the content of the "d" attribute of one <path> element.
    proc getPathD { filename } {
        variable D_PROP {}
        set p [expat -elementstartcommand _ElementStartCb]
        
        try {
            $p parsefile $filename 
        } on error errMsg {
            error "$errMsg"
        } finally {
            $p free
        }
        
         # trick; return D_BUFF and reset it !
        set res $D_PROP ; set D_PROP {}
        return $res
    }

 }

 # == MAIN =====

wm title . "\"Blend2d\" high performance 2D vector graphics engine - TclTk bindings"

set filename [file join $thisDir moby.svg]

set SFC [image create blend2d]
label .cvs -image $SFC -borderwidth 0
pack .cvs -padx 20 -pady 20 -expand 1 -fill both

set blPath [BL::Path new]
foreach dataStr [simpleSVGparser::getPathD $filename] {
    $blPath addSVGpath $dataStr
}

proc Redraw {SFC blPath DX DY} {
	lassign [$SFC size] oDX oDY
	if { $oDX == $DX && $oDY== $DY } return

	# === preliminary transformation fitting the image	
	
	# resize the blPath (preserving the proportions)
	set borderSize 30
	lassign [$blPath bbox] px0 py0 px1 py1
	set dx [expr {$px1-$px0}]
	set dy [expr {$py1-$py0}]
	 # subtract $borderSize pixels per side for the border 
	incr DX [expr {-2*$borderSize}]
	incr DY [expr {-2*$borderSize}]
	set bestZoom [expr {min($DX/$dx,$DY/$dy)}]
	
	set DX [expr {int($dx*$bestZoom)+2*$borderSize}]
	set DY [expr {int($dy*$bestZoom)+2*$borderSize}]
	
	$SFC configure -format [list $DX $DY]
	$SFC clear -style [BL::color darkblue]
$SFC push
	 # change the scale at metamatrix
	$SFC configure -matrix [Mtx::scale $bestZoom -$bestZoom]
	$SFC userToMeta
	
	 # translate the origin at (px0,py1)  (inverting the y axis)
	$SFC configure -matrix [list 1 0 0 1 [expr {-($px0-$borderSize/$bestZoom)}] [expr {-($py1+$borderSize/$bestZoom)}]]

	# draw the blPath 
	$SFC fill $blPath -style [BL::color white]    
$SFC pop
}  


Redraw $SFC $blPath 500 300     
      
bind .cvs <Configure> { Redraw $SFC $blPath %w %h }     
      
      