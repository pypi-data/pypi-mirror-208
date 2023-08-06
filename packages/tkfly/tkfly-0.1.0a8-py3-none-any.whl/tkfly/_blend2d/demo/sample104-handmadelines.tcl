 # sample104
 #
 # Toolkit for tuning (pseudo) hand-drawn lines
 # 

set thisDir [file normalize [file dirname [info script]]]
set auto_path [linsert $auto_path 0 [file dirname $thisDir]]

set auto_path [linsert $auto_path 0 [file join $thisDir lib]]
tcl::tm::path add [file join $thisDir lib]

#
# Blend2d - Back to primary school
#

package require tile
package require Eseparator
package require EbuttonColor
package require IKscale

package require sketchline
package require hatching

package require Blend2d 1.0b1


# === GUI ====================================================================

label .cvs
set w .controls
frame $w
    $w configure -pady 10 -padx 10

    #-----------------------------------------------------------------
    Eseparator $w.sep1 -text "Hand drawn style"
    
    ttk::label $w.labs0 -text "Background\ncolor"
    EbuttonColor $w.background -variable G(BACKGROUND)
    ttk::label $w.labs1 -text "Stroke\ncolor"
    EbuttonColor $w.strokecolor -variable G(STROKE_COLOR)
    ttk::label $w.labs2 -text "Stroke\nwidth"
    IKscale $w.strokewidth -variable G(STROKE_WIDTH) -labelside right
    
    grid $w.sep1 - -pady {30 10}
    grid $w.labs0 $w.background
    grid $w.labs1 $w.strokecolor
    grid $w.labs2 $w.strokewidth    

    #-----------------------------------------------------------------
    Eseparator $w.sep1a -text "Variable width"

    ttk::label $w.labhm4 -text "variable width"
    ttk::checkbutton $w.hm_variablewidth \
        -onvalue true -offvalue false \
        -variable G(HM_VARIABLEWIDTH)

    trace add variable G(HM_VARIABLEWIDTH) write {
        apply { 
            {boolVal w args} {
                #ignore args
                set status [expr {$boolVal ? "!disabled" : "disabled"}]
                $w.labhm5 state $status
                $w.hm_sigmawidth state $status
            }           
        } $::G(HM_VARIABLEWIDTH) $w  \
    }

    ttk::label $w.labhm5 -text "Sigma width"
    IKscale $w.hm_sigmawidth  -variable G(HM_SIGMAWIDTH) -labelside right 

    grid $w.sep1a - -pady {30 10}
    grid $w.labhm4 $w.hm_variablewidth
    grid $w.labhm5 $w.hm_sigmawidth
                    
    #-----------------------------------------------------------------
    Eseparator $w.sep2 -text "Sketching tweaks"

    ttk::label $w.labhm1 -text "splits"
    IKscale $w.hm_splits -variable G(HM_SPLITS) -labelside right
    
    ttk::label $w.labhm2 -text "% amplitude"
    IKscale $w.hm_amplitude -variable G(HM_AMPLITUDE) -labelside right
    
    ttk::label $w.labhm3 -text "tension"
    IKscale $w.hm_tension -variable G(HM_TENSION) -labelside right

    grid $w.sep2 - -pady {30 10}
    grid $w.labhm1 $w.hm_splits
    grid $w.labhm2 $w.hm_amplitude
    grid $w.labhm3 $w.hm_tension
    
    #-----------------------------------------------------------------
    Eseparator $w.sep3 -text "Hatching"
    ttk::label $w.labh1 -text "angle"
    IKscale $w.hatchingangle -variable G(HATCHING_ANGLE) -labelside right

    ttk::label $w.labh2 -text "distance"
    IKscale $w.hatchingdistance -variable G(HATCHING_DISTANCE) -labelside right
    
    grid $w.sep3 - -pady {30 10}
    grid $w.labh1 $w.hatchingangle
    grid $w.labh2 $w.hatchingdistance
    
pack $w -side left -expand 0 -fill y
pack .cvs -expand 1 -fill both

  # -- set valid ranges (euristics)
$w.strokewidth      configure -from 0.1 -to 10.0 -resolution 0.1
$w.hm_sigmawidth configure -from 0.05 -to 1.2 -resolution 0.05

$w.hm_splits     configure -from 0   -to 20  -resolution 1.0
$w.hm_amplitude  configure -from 0.0 -to 2.0 -resolution 0.01
$w.hm_tension    configure -from 0.0 -to 1.0 -resolution 0.05


$w.hatchingangle    configure -from -90 -to 90  -resolution 1.0
$w.hatchingdistance configure -from   5 -to 100 -resolution 0.1
    
# --- GUI control logic -------------------------------------------------------

 # set all the defaults before setting the GUI control-logic 
set G(BACKGROUND)   black
set G(STROKE_COLOR) #BBBBBB
set G(STROKE_WIDTH) 1.5

set G(HM_SPLITS)          5
set G(HM_AMPLITUDE)      0.6
set G(HM_TENSION)        0.55
set G(HM_SIGMAWIDTH)     0.4
set G(HM_VARIABLEWIDTH)  false

set G(HATCHING_DISTANCE) 20.0
set G(HATCHING_ANGLE)    0.0

set G(SFC)   [image create blend2d -format {400 400}]
$G(SFC) configure \
    -fill.style   [BL::color $G(BACKGROUND)] \
    -stroke.style [BL::color $G(STROKE_COLOR)] \
    -stroke.width $G(STROKE_WIDTH)
set G(HATCHING_SHAPE) [BL::Path new]


 # simple variable tracing.
 #   varname must be a global var (or a fully qualified var) (even an array element)
 #   script will be executed at global level.
 #
 #  Be aware: 
 #    if script changes the same varname, then it's NOT re-executed.
 #    if script changes another 'traced' variable, then the related script is excecuted too.
 #    ? what happens if  scriptA changes B and scriptB changes A ?
 #    -> from the "trace" reference manual:
 #       While commandPrefix is executing during a read or write trace,
 #       traces on the variable are temporarily disabled.
 proc OnChanged {varname script } {
    uplevel #0 [list \
        trace add variable $varname write [list uplevel #0 $script \;\# ] \
    ]
 }

OnChanged  G(BACKGROUND) {
    $G(SFC) configure -fill.style [BL::color $G(BACKGROUND)]
    REDRAW
}

OnChanged  G(STROKE_COLOR) {
    $G(SFC) configure -stroke.style [BL::color $G(STROKE_COLOR)]
    REDRAW
}

OnChanged  G(STROKE_WIDTH) {
    $G(SFC) configure -stroke.width $G(STROKE_WIDTH)
     # this paramis (improperly) used also for sketch::line_variablewidth.
     # in that case you should rebuild..
    if { $G(HM_VARIABLEWIDTH) }  REBUILD_HATCHING
    REDRAW
}

foreach tag {HM_SPLITS HM_AMPLITUDE HM_TENSION HM_VARIABLEWIDTH HM_SIGMAWIDTH} {
    OnChanged G($tag) {
        REBUILD_HATCHING ; REDRAW    
    }
}

foreach tag {HATCHING_DISTANCE HATCHING_ANGLE} {
    OnChanged G($tag) {
        REBUILD_HATCHING ; REDRAW    
    }
}

 # return a bbox covering all the surface $sfc less the margin
proc innerBBox {sfc margin} {
    lassign [$sfc size] W H
    list $margin $margin [expr {$W-$margin}] [expr {$H-$margin}]
}

proc appendToBLPath { blPath svgcmds } {
    foreach cmd $svgcmds {
        set points [lassign $cmd cmdPrefix]
        switch -- $cmdPrefix {
          M { $blPath moveTo {*}$points }
          L { $blPath lineTo {*}$points }
          Q { $blPath quadTo {*}$points }
          C { $blPath cubicTo {*}$points }          
        }
    }
}

proc HANDMADE_LINE { lineAlgorithm shape opts x0 y0 x1 y1 } {
    set svgpath [$lineAlgorithm $opts $x0 $y0 $x1 $y1]
    appendToBLPath $shape $svgpath
}

 
proc REBUILD_HATCHING {} {
    variable G
    set opts [dict create \
        -splits     $G(HM_SPLITS) \
        -amplitude  $G(HM_AMPLITUDE) \
        -tension    $G(HM_TENSION) \
    ]

    set margin 40.0

    if { $G(HM_VARIABLEWIDTH) } {
        dict set opts -sigmawidth $G(HM_SIGMAWIDTH)
        dict set opts -width      $G(STROKE_WIDTH)
        
        set G(SKETCH_TYPE) fill
        set lineAlgorithm sketch::line_variablewidth
    } else {
        set G(SKETCH_TYPE) stroke
        set lineAlgorithm sketch::line
    }
    
    $G(HATCHING_SHAPE) reset   
    hatching \
        $G(HATCHING_ANGLE) $G(HATCHING_DISTANCE) \
        [innerBBox $G(SFC) $margin] \
        [list HANDMADE_LINE $lineAlgorithm $G(HATCHING_SHAPE) $opts]
}

proc REDRAW {} {
    variable G

    $G(SFC) clear ;# with default -style.fill
    if { $G(SKETCH_TYPE) == "fill" } {
        $G(SFC) fill $G(HATCHING_SHAPE) -style [BL::color $G(STROKE_COLOR)]
    } else {
        $G(SFC) stroke $G(HATCHING_SHAPE) -stroke.cap ROUND
    }
}


 # ==== main =================================================================

wm title . "Tuning (pseudo) hand-drawn lines"

.cvs configure -image $G(SFC)
 # WARNING remove all decoration from the label, 
 # or the <Configure> handler will go crazy !
.cvs configure -borderwidth 0 -padx 0 -pady 0


bind .cvs <Configure> {OnContainerResize %W %w %h }

proc OnContainerResize {win W H} {
    [$win cget -image] configure -format [list $W $H]
    REBUILD_HATCHING
    REDRAW
}

REBUILD_HATCHING
REDRAW
