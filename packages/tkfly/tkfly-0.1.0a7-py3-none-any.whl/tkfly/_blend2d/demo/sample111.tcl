#  Extract the geometries from a set of SVG files.
#  then draw each shape with a shadow
#
catch {console show}

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

wm title . "TclTk bindings for Blen2d - demo 111"

# 	layer_6.svg  #A41310

set FilesAndColors {
	layer_5.svg  #A1DFFB
	layer_4.svg  #C33124
	layer_3.svg  #F98365
	layer_2.svg  #E8A628
	layer_1.svg  #F9DE59	  
}

set FILTER_TYPE "ignore"
ttk::checkbutton .shadow -text "Shadows" -variable FILTER_TYPE \
	-offvalue "ignore" -onvalue "shadow"
pack .shadow -padx 5 -side left
set SFC [image create blend2d]
label .cvs -image $SFC -borderwidth 0
pack .cvs -padx 20 -pady 20 -expand 1 -fill both



set layersAndColors {}
foreach {filename color} $FilesAndColors {
	set blPath [BL::Path new]
	foreach dataStr [simpleSVGparser::getPathD [file join $thisDir Q $filename]] {
    	$blPath addSVGpath $dataStr
	}
	lappend layersAndColors $blPath $color
}


proc Redraw {SFC layersAndColors DX DY filterType} {
	# === preliminary transformation fitting the image	
	
	# set the transform matrix so that the surface can contain the bbox of the 1st layer
	set borderSize 30
	lassign [[lindex $layersAndColors 0 0] bbox] px0 py0 px1 py1
	set dx [expr {$px1-$px0}]
	set dy [expr {$py1-$py0}]
	 # subtract $borderSize pixels per side for the border 
	incr DX [expr {-2*$borderSize}]
	incr DY [expr {-2*$borderSize}]
	set bestZoom [expr {min($DX/$dx,$DY/$dy)}]
	
	set DX [expr {int($dx*$bestZoom)+2*$borderSize}]
	set DY [expr {int($dy*$bestZoom)+2*$borderSize}]
	
	lassign [$SFC size] oDX oDY
	if {$oDX != $DX || $oDY != $DY } {
		$SFC configure -format [list $DX $DY]
	}

	$SFC clear -style [BL::color #A41310]
$SFC push
	 # change the scale at metamatrix
	set pmx [expr {($px0+$px1)/2.0}]
	set pmy [expr {($py0+$py1)/2.0}]

	set M [Mtx::MxM \
			[Mtx::scale $bestZoom] \
			[Mtx::translation $borderSize $borderSize] \
		]	
	$SFC configure -matrix $M
	
	foreach {blPath color} $layersAndColors {
		$SFC filter $filterType -radius 20 -dxy {3 10} -color [BL::color gray20] {
			$SFC fill $blPath -style [BL::color $color]
		}
	}
$SFC pop
}  


Redraw $SFC $layersAndColors 500 300 $FILTER_TYPE    
      
bind .cvs <Configure> { Redraw $SFC $layersAndColors %w %h $FILTER_TYPE }     
.shadow configure -command { Redraw $SFC $layersAndColors {*}[$SFC size] $FILTER_TYPE }  
      