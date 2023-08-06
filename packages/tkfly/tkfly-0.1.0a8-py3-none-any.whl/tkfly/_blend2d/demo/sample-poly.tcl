set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

#
# Blend2d - polygon sample
#

package require Blend2d 1.0b1

proc tcl::mathfunc::randomSign {} {
    expr {rand()< 0.5 ? 1.0: -1.0}
}

 # initialize N random cubics in a rectangle {0 0 w h}
 #  set the global VTX and DIR arrays.
proc InitRandomParticles {N w h} {
    global VTX
    global DIR

    # since a cubic requires 4 points, and the start/end points are shared,
    # we should add 1+3*N points
    set N [expr {1+3*$N}]
            
    set prev [llength $VTX]
    if { $N > $prev } {
        set VTX [lrange $VTX 0 $N-1]
        set DIR [lrange $DIR 0 $N-1]
    }

     # add more vertices
    while { $prev < $N } {
        lappend VTX [list [expr {rand()*$w}] [expr {rand()*$h}]]
        lappend DIR [list [expr {(rand()*0.5 +1.0)*randomSign()}] [expr {(rand()*0.5 +1.0)*randomSign()}]]    
        incr prev    
    }     
}             

 # adjust VTX, DIR
proc moveParticles {W H} {
    global VTX
    global DIR

    set newV {}
    set newD {}
    foreach v $VTX d $DIR {
        lassign $v vx vy
        lassign $d dx dy

        set vx [expr {$vx+$dx}]
        set vy [expr {$vy+$dy}]

        if { $vx <= 0.0 ||  $vx > $W } {
            set dx [expr {-$dx}]
            set vx [expr {min($vx+$dx,$W)}]
        }
        if { $vy <= 0.0 ||  $vy > $H } {
            set dy [expr {-$dy}]
            set vy [expr {min($vy+$dy,$H)}]
        }
        lappend newV [list $vx $vy]
        lappend newD [list $dx $dy]        
    }
    set VTX $newV
    set DIR $newD
}


proc drawParticles {sfc} {
    global VTX
    global HUE

    set cPath [BL::Path new]

    set V [lassign $VTX p0]
    $cPath moveTo $p0   
    foreach {p1 p2 p3} $V {
        $cPath cubicTo $p1 $p2 $p3 
    }
    set HUE [expr {fmod($HUE+0.1,360.0)}]
    $sfc fill $cPath -style [HSB $HUE 1.0 1.0]
    $cPath destroy
}


# Paint
# parameters:
#   SFC      : the BL::Surface
#   WIDTH HEIGHT : the window size (i.e. the Surface size)
proc Paint {SFC WIDTH HEIGHT} {	
     # background is black, with a low alpha.
     # In this way, instead of filling with pure black,
     # we get a "fade-to-black" effect
    $SFC clear -style 0x05000000
    moveParticles $WIDTH $HEIGHT
    drawParticles $SFC
}

#------ GUI and Controls ----------------------------------------------

label .cvs
frame .controls
    .controls configure -pady 20 -padx 10
    
    label .controls.lab1 -text "Renderer"
    ttk::combobox .controls.renderer -state readonly
    ttk::button .controls.run
    
    foreach w [winfo children .controls] {
    	pack $w -pady 5
    }

pack .controls -side left -expand 0 -fill y
pack .cvs -expand 1 -fill both


# -----

set THREADS 0
set WIDTH  500
set HEIGHT 500
set HUE 0.0


set SFC [image create blend2d -format [list $WIDTH $HEIGHT]]
$SFC threads $THREADS
$SFC configure -fill.rule EVEN_ODD
 # WARNING: remove any decoration from the container, or the <Configure> handler will resize the image indefinitely !
.cvs configure -image $SFC -borderwidth 0 -padx 0 -pady 0
.cvs configure -image $SFC



set RENDERER_TABLE [dict create \
    "No Threads"   0 \
    "2 Threads"    2 \
    "4 Threads"    4 \
    ]
    
 # starting renderer
set RENDERER [lindex $RENDERER_TABLE 0]

.controls.renderer configure \
    -values [dict keys $::RENDERER_TABLE] \
    -textvariable ::RENDERER

trace add variable RENDERER write OnChangedRenderer

proc OnChangedRenderer {args} {
    global SFC
    global RENDERER_TABLE    
    set threadCount [dict get $RENDERER_TABLE $::RENDERER]    
    $SFC threads $threadCount
}



set RUNNING_LABEL "Run"
.controls.run configure \
    -textvariable ::RUNNING_LABEL \
    -command SwitchRunningState

set RUNNING false

proc SwitchRunningState {} {
    global RUNNING
    global RUNNING_LABEL
    
    if { $RUNNING } {
        set RUNNING false
        set RUNNING_LABEL "Run"
    } else {
        set RUNNING true
        set RUNNING_LABEL "Pause"
    }
    if { $RUNNING } StartPaintLoop 
}

proc StartPaintLoop {} {
    global RUNNING
    global SFC
    global WIDTH
    global HEIGHT
    
    if { $RUNNING } {
        Paint $SFC $WIDTH $HEIGHT
        after 1 StartPaintLoop
    }
}

bind .cvs <Configure> {
	set w %w
	set h %h
	if { $w != $WIDTH || $h != $HEIGHT } {
		set WIDTH $w
		set HEIGHT $h
		$SFC configure -format [list $WIDTH $HEIGHT]
        drawParticles $SFC
	}
}

# == MAIN =====

wm title . "\"Blend2d\" high performance 2D vector graphics engine - TclTk bindings"

set VTX {}
set DIR {}
InitRandomParticles 10 $WIDTH $HEIGHT
 
  # just the 1st frame
Paint $SFC $WIDTH $HEIGHT