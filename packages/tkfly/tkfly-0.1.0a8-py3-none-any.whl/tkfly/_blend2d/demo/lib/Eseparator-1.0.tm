## Eseparator.tcl
## extended horizontal separator with label
##
## Copyright (c) 2008 <Irrational Numbers> : <aldo.buratti@tiscali.it> 
##
## This library is free software; you can use, modify, and redistribute it
## for any purpose, provided that existing copyright notices are retained
## in all copies and that this notice is included verbatim in any
## distributions.
##
## This software is distributed WITHOUT ANY WARRANTY; without even the
## implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
##

# How to use:
#   package require Eseparator
#   Eseparator .s1 -text "hello" -labelanchor e -font myfont
#   pack .s1 -fill x
#   pack .s1 -fill x -pady 10

# IMPORTANT NOTE:
#  This widget has ZERO height !
#  Therefore you should always tell youtr geom-manager to reserve some vertical
#  space (depending on the font-size).
#  * PACK g.m.
#    pack .s1 ......  -pady 10
#  * GRID g.m.
#    grid .s1 ......  -pady 10
#  * PLACE g.m.
#    place .s1 ....... -y 20
#
# This is not a bug; it is a feature !
# In this way a widget instance is totally transparent (i.e. it has no "solid backhround")
# , except for label-area, that may be adjusted via the -background 
#   option.


package require snit

snit::widget Eseparator {
    hulltype frame

    option -background -configuremethod SetBg
    option -foreground -configuremethod SetFg
    option -labelanchor -configuremethod SetLabelAnchor -default w  \
           -type { snit::enum -values { w c e } } 
    option -labelmargin -configuremethod SetLabelMargin -default 1c \
        -type snit::pixels

    
    option -text -default {} -configuremethod SetText
    delegate option -font to thisLabel
    delegate option -labelrelief to thisLabel as -relief
    delegate option -labelborderwidth to thisLabel as -borderwidth   
    
    option -y -default 0 -configuremethod SetY -type snit::pixels

     # many inherithed options should be hidden ( or at least deprecated )
     # in particular -bg/-fg should be hidden
    delegate option * to hull except {-bg -fg -height -padx -pady}

    component thisLabel
    
    constructor {args} {
         # WARNING
         #  this megawidget is made of two subwidgets:
         #    a separator (the hull frame) and a label (a companion label).    
        $hull configure -bd 2 -width 200 -relief raised
        
         # create a companion (non a children) widget
        install thisLabel using label ${win}_label
        
        $win PlaceLabel -in $win \
                -bordermode outside
        
        # force initial positioning        
        $win configure -text        {}	     
        $win configure -background  [$thisLabel cget -background]	     
        $win configure -foreground  [$thisLabel cget -foreground]
        $win configure -labelanchor w
        $win configure -labelmargin 1c
        
        $win configurelist $args
    }			
	
    destructor {
	     # since this label is not a children component (it is a companion),
	     #  we need to destroy it explicitely.
	    destroy $thisLabel
    }

    method SetBg {opt val} {
        $thisLabel configure -background $val
        set options($opt) $val
    }

    method SetFg {opt val} {
        $thisLabel configure -foreground $val
        $hull      configure -background $val
        set options($opt) $val
    }

    method SetLabelAnchor {opt val} {
        $win PlaceLabel -anchor $val
        switch -- $val {
            w { $win PlaceLabel -relx 0.0 -x $options(-labelmargin) }
            c { $win PlaceLabel -relx 0.5 -x 0 }
            e { $win PlaceLabel -relx 1.0 -x -$options(-labelmargin) }
        }	    
        set options($opt) $val
    }
    
    method SetLabelMargin {opt val} {
        switch -- $options(-labelanchor) {
            w { $win PlaceLabel -x $val }
            c { $win PlaceLabel -x 0 }
            e { $win PlaceLabel -x -$val }
        }
        set options($opt) $val
    }
    
    method SetY {opt val} {
        $win PlaceLabel -y $val
        set options($opt) $val
     }

    method SetText {opt val} {
        if { $val == {} } {
            $win HideLabel
        } else {
            $win RevealLabel
        }
        $thisLabel configure -text $val
        set options($opt) $val
     }


     # --- utilities for a better 'place' geometry manager
                
    variable isHidden     false
    variable SavedPlace   -array {}

     method HideLabel {} {
        set isHidden true
        place forget $thisLabel
     }
     
     method RevealLabel {} {
        set isHidden false
        place configure $thisLabel {*}[array get SavedPlace]
     }
     
     method PlaceLabel {args} {
        if { ! $isHidden } {
            place configure $thisLabel {*}$args
        }
        array set SavedPlace $args
     }    
}
