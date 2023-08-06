##  IKscale

## Classic tk::scale visually sucks, new ttk::scale is visually appealing
## (and its layout is also more adaptable - if only you understand ttk::style .. ).
##
## Unfortunately for me, ttk::scale lost one very important feature
##  the "-resolution" option
## and a simple way to display the current scale's value.
##
## The missing -resolution is critical for many apps (like mine):
##  suppose you have a scale from 1 to 10 and you want to invoke a -command
##  or trace the linked variable only when the scale reaches an integer value...
##  With ttk::scale this is not possible, because when the sliders moves from 
##  1.0 to 2.0, then the releated -command is invoked for 1.0001 1.002 ... and so on.
##  The same is for the linked variable: A linked variable will be updated 
##  with all the values between 1.0 and 2.0 ...
##  I only want to see  1.0, 2.0, 3.0 ... ! 
##
## This is my attempt to solve these problems.
##
## v 1.0.1 - BUGFIX - setting the linked variable should not trigger the -command
##

if 0 {
-- DOC ------------------------------------------------------------------------
IKscale look&feel is identical to ttk::scale, with the following added features:

* added option -resolution
   ...
* added option -labelside

IKscale is a new ttk megawidget, thus its look can be changed with ttk::theme
and ttk::style.

-------------------------------------------------------------------------------
}

package require snit

snit::widget IKscale {
    hulltype ttk::frame

    component sub_scale
    component sub_label

     # added options
    option -resolution -default 1.0 -type snit::double \
        -configuremethod Set_resolution
    option -labelside -default none  \
        -configuremethod Set_labelside
 
     # redefined options
    option -orient   -default "horizontal" -configuremethod Set_orient
    option -variable -default {}           -configuremethod Set_variable
    option -command  -default {}           -configuremethod Set_command 
    option -from     -default {}           -configuremethod Set_range 
    option -to       -default {}           -configuremethod Set_range 
                
    delegate option * to sub_scale 

     #redefined commands: get, state
    delegate method * to sub_scale

	variable my ;# array
      # my(roundedValue)  is the value shown in the sub_label
      #   ASSERT:  my(roundedValue) is always rounded to resolution
      # my(resolutionFormat) ;# fmt-specification for formatting the current value
      #	my(innerLinkedVar)
	           
    constructor {args} {
        install sub_scale using ttk::scale $win.scale
        install sub_label using ttk::label $win.label
        pack $sub_scale ;# sub_label is placed only if requested.

        set my(resolutionFormat) [getFormatForResolution $options(-resolution)]
        set my(roundedValue) 0
        $sub_scale configure -command [mymethod OnChanged_InnerValue]
		$sub_scale configure -variable [myvar my(innerLinkedVar)]
        $sub_label configure \
            -textvariable [myvar my(roundedValue)] \
            -anchor e
        
         # force -orient initializaztion
        $win configure -orient [$win cget -orient]
         # force -from, -to  initialization
        $win configure -from [$sub_scale cget -from]  -to [$sub_scale cget -to]
                                      
        $win configurelist $args
    }
    
    destructor {        
        #  remove trace on $options(-variable)
        set varName $options(-variable)
        if { $varName != {} } {
            uplevel #0 \
                trace remove variable $varName write [list [mymethod OnTrace_ExtVar]]
        }
    }

     # it's funny, but sometimes rounding a number rounded to some decimals
     # produces stranges results ...
     #  eg  RoundToResolution 16.86346863468635 0.1   -->  16.900000000000002     
     # the difference is infinitesimal, and we could use that value instead of 16.9,
     # BUT, we cannot *print* 16.900000000000002 when we want 16.9.
     # The so far found solution is to use the [format] command to display a
     # properly rounded number.

    proc countOfDecimalDigits { x } {
        # get decimals
        if { [regexp {\.(\d*)} $x _ decimalStr] } {
            # remove trailing 0s 
            set decimalStr [string trimright $decimalStr "0"]
            set decimals [string length $decimalStr]
        } else {
            set decimals 0
        }
        return $decimals
    }

    proc getFormatForResolution {resolution} {
        # resolution is a number like   10  10.0   2  2.0  2.5  2.50
        set n [countOfDecimalDigits $resolution]
        return "%.${n}f"     
    }

     # note: we assume x is a number in decimal notation (NO scientific notation!)
    proc howManyDigits { x resolution } {
        # get the integer part
        set xStr [string trim $x]
        set n [string first "." $xStr]
        if { $n == -1 } {
            set n [string length $xStr]
        }
        set d [countOfDecimalDigits $resolution]
        if { $d > 0 }  {
            incr d  ;#  add 1 for the "." character
        }       
        return [expr {$n+$d}]
    }    
             
    proc RoundToResolution {x resolution} {
        expr {round($x/$resolution)*$resolution}        
    }
    
    method OnChanged_InnerValue {args} {
    	set _roundedVal [$win get]
        if { $my(roundedValue) eq ""  ||  abs($_roundedVal - $my(roundedValue)) >= 1e-9 } {
            set my(roundedValue) $_roundedVal        
            
             # update the public -variable (if exists)
            if { $options(-variable) != {} } {
                uplevel #0 set $options(-variable) [list $my(roundedValue)]
            }
            
            # call the callback .. (if exists)
            if { $options(-command) != {} } {
                uplevel #0 $options(-command) [list $my(roundedValue)]
            }
        }
        
    }


    method OnTrace_ExtVar {args} {
        upvar #0 $options(-variable) extVar 
        catch {
        	set my(innerLinkedVar) $extVar
        	set my(roundedValue)   $extVar
        }
         # this will NOT trigger OnChanged_Inner
    }
    

    method Set_command {opt value} {
         # sub_scale should have no -command
         #  but -command should appear in the public interface.
        set options($opt) $value
    }
    
        
    method Set_resolution {opt value} {
        set my(resolutionFormat) [getFormatForResolution $value]

         # set option now ! (before callig OnTrace_InnerValue) 
        set options(-resolution) $value
        
        $sub_scale set [RoundToResolution [$sub_scale get] $value]
        $win ResizeLabel
    }

    method ResizeLabel {} {
        set width1 [howManyDigits $options(-from) $options(-resolution)]
        set width2 [howManyDigits $options(-to)   $options(-resolution)]

        $sub_label configure -width [expr {max(4, $width1, $width2)}]            
    }

     # used for -to and -from options
     #  we must resize the sub_label in order to properly display the wider value
    method Set_range {opt value} {    
        $sub_scale configure $opt $value
        set options($opt) $value
        
        $win ResizeLabel
    }
        
    method Set_variable {opt value} {
         # remove trace from current -variable (if not null)
        set varName $options(-variable)
        if { $varName != {} } {
            uplevel #0 \
                trace remove variable $varName write [list [mymethod OnTrace_ExtVar]]
        }

        set options(-variable) $value

         # add trace to new -variable (if not null)
        set varName $value
        if { $varName != {} } {
            $win OnTrace_ExtVar           
            uplevel #0 \
                trace add variable $varName write [list [mymethod OnTrace_ExtVar]]
        }

    }
 
    method Set_orient {opt value} {
        $sub_scale configure -orient $value
         # if I'm here, I'm sure value is "horizontal" or "vertical".
         # No other cases.
        switch -- $value {
         "horizontal" { pack $sub_scale -fill x -expand 1 }
         "vertical"   { pack $sub_scale -fill y -expand 1 }
        }
        set options($opt) $value
    }
    
    method Set_labelside {opt value} {
        if { $value == {} || $value == "none" } {
            pack forget $sub_label
        } else {
             # if value is invalid, "pack" raises an error an return a message
             # like the following:
             #   bad side "xxx": must be top, bottom, left, or right
            pack $sub_label -before $sub_scale -side $value        
        }
        set options($opt) $value
    }

	method get {} {
        set val [$sub_scale get]
        set _roundedVal [RoundToResolution $val $options(-resolution)]
         # this trick is for removing infinitesimal errors in RoundToResolution
        set _roundedVal [format $my(resolutionFormat) $_roundedVal]  			
		return $_roundedVal
	}
	    
    method state {status} {
        $sub_scale state $status
        $sub_label state $status        
    }
}