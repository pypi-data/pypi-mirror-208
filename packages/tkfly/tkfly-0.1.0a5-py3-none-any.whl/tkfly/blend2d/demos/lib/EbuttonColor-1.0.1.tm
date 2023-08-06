# EbuttonColor.tcl

# --- doc -------
if 0 {
EbuttonColor (Extended-Button Color)

is a new widget (looking like a standard ttk::button) for the selection of a color.
When clicked, it opens the standard "tk_chooseColor" dialog and then updates the
linked variable (see below) with the value of the chosen color.

EbuttonColor extends the ttk::button with a new option:
  -variable _varName_
that must be set at creation time.
This new option is mandatory since it's only by inspecting this variable that
the users can 'get' the value of the choosen color.
Varname should be the name of a global or a fully namespace-qualified variable.

Example:
	package require EbuttonColor
	
	set ::UI::PEN red  ;# the initial value
	EbuttonColor .b1 -text "Pen Color" -variable ::UI::PEN
	pack .b1
	
	... whenever user press .b1 and a color is chosen, the ::UI:PEN is updated.
	
	... on the other side, when the user sets UI::PEN, the button's color changes.
     

  If PEN is explicitely set with a non-color value, it's an error,
  although it's safe to set the "" value.

There are some limitation on the use of some standard ttk::button options,
the following options cannot be explicitely used or changed, since they are 
reserved for internal use, and moreover, they would be useless in this context.
 -class
 -image
 -compound
 -command
  
The "-class" option is useless, since these EbuttonColor are marked with the new "EbuttonColor" class.
The "-image" and "-compound" options are internally used for setting and updating the look of this widget.
The "-command" option is used internally. If user needs to trigger an action when the
button is released, she could set a "trace" on the linked variable.

Currently these options are not 'protected' against an improper use. It's user responsability !

 ver 1.01 - Bugfix :now -variable may be an array elem, too.
}



namespace eval EbuttonColor {
	namespace export EbuttonColor

	variable _map  ;# dict: key is widgetname, 
	                # value is {linkedVarname imagename}

    proc _postdestroy {win} {
        variable _map
        if { [dict exists $_map $win] } {
			lassign [dict get $_map $win] fqvarName imageName
			catch {trace remove variable $fqvarName write [list EbuttonColor::_OnChangedVar $win]}            
            
		}
		# else ... you have big troubles
		catch {image delete $imageName}
		dict unset _map $win     
    }

	proc _OnChangedVar {win args} {
        # args added by trace are simply ignored
        variable _map

        if { [dict exists $_map $win] } {
			lassign [dict get $_map $win] fqvarName imageName
            upvar #0 $fqvarName color
			$imageName put $color -to 0 0 [image width $imageName] [image height $imageName]
			$win configure -state [$win cget -state] ;# dummy op, just for refreshing the bitmap
        }
    }
    
    bind EbuttonColor <Destroy> { EbuttonColor::_postdestroy %W }
    
	proc _init {} {
		variable _map
		set _map {}	
		 # copy all the TButton bingings to EbuttonColor
		foreach evt [bind TButton] {
			bind EbuttonColor $evt [bind TButton $evt]
		}
	}
	
	_init
}


proc EbuttonColor::EbuttonColor {w args} {
	 # preprocess all the options (args); remove forbidden options,
	 #  and save and remove the custom "-variable" option
	set varName {}
	set newOptions {}
	foreach {opt val} $args {
		switch -- $opt {
		 -variable {
			 set varName $val		     
		  }
		 -class -		
		 -command -
		 -image -
		 -compound {
		 	# ignore this option !  (? explicit error message ?)
		 }
		 default {
		 	lappend newOptions $opt $val
		 }
		}
	}

	if { $varName eq "" } {
		error "missing mandatory option \"-variable\" varName"
	}

	ttk::button $w -class EbuttonColor {*}$newOptions
		# if it fails (.. some wrong options ...) widget is not created; nothing to undo.	

	set fqvarName [namespace which -variable $varName]
	if { $fqvarName eq "" } {
         # maybe varname is something like arr(elem) or  ::arr(elem) 
         # Add a :: as prefix  (it does not hurt if is repeated)
		set fqvarName ::$varName
	}
    	
	$w configure -command [ list apply {
		{varColor} {
            upvar #0 $varColor color
			if { [catch { winfo rgb . $color} ] } {
				set c [tk_chooseColor]
			} else {
				set c [tk_chooseColor -initialcolor $color]		
			}
			if { $c != "" } { set color $c}
		}
		} $fqvarName ]	

	 # create a tkphoto for button $w

     # too difficult to compute the button height, then then max height of the embedded image
     # ....
     # this value is hardcoded here
    set imgHeight 16
    set imgWidth  16
	set imageName [image create photo -width $imgWidth -height $imgHeight]
	 # the following statement may fail if the referenced variable 
	 #  does not contain a valid color.   ignore the error
	catch {
        upvar #0 $varName color
        $imageName put $color -to 0 0 $imgWidth $imgHeight
    }

	$w configure -image $imageName -compound right

	trace add variable $fqvarName write [list EbuttonColor::_OnChangedVar $w]

	 # save everything in a map, so that when this button $w will be destroyed,
	 #  custom imageName will be deleted.
	 #  custom trace on fqvarName will be removed		
	variable _map
	dict set _map $w [list $fqvarName $imageName]
	
	return $w
}

namespace import EbuttonColor::*
