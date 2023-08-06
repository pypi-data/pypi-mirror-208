
# For every new filter XXX
#  two methods should be provided:
#   1)   method CheckArgs-XXX { args } { ... }
#   2)   method filter-XXX { ..params... } { .. }

#   filter-XXX will take every required parameter in a simple fixed format
#      example:    method filter-XXX { alpha beta ARGBcolor offset }
#   CheckArgs-XXX will take the parameters expressed as a list of key/options
#      e.g.    -color blue -alpha 30
#   and return a list of values (without the keys) conformat to the expected parameters of filter-XXX
#   * note: take care of missing key/value (-> provide internal default values)
#   *       take care of the order of the expected parameters of filter-XXX.
#   Example:
#   *   if the expected parameters are {alpha beta ARGBcolor offset }
#       and the input parameters are "-color blue -alpha 30"   (NOTE: keys "-beta" and "-offset" unspecified )
#       then
#          alpha  takes "30"  from "-alpha" parameters
#          beta   takes  "360" from internal default
#          color  takes "#0xFF0000FF" from "-color" ( then converted in a proper format)
#          offser takes {3 3} from internal default
#       then
if 0 {
       method CheckArgs-XXX {args} {
		  # set default values for the expected parameters
		  set alpha 0.0
		  set beta  360.0
		  set ARGBcolor 0xFF000000
		  set offset {3 3}

			... parse $args and update   alpha, beta, ....
			
			
		   return [list $alpha $beta $ARGBcolor $offest]
		}
}
# ---------------------------------------------------------------------

 # to do .. make them public !
proc BL::_box2rect { x0 y0 x1 y1} {
	list $x0 $y0 [expr {$x1-$x0}] [expr {$y1-$y0}]
}
proc BL::_enlargedRect { x y w h dx dy} {
	list [expr {$x-$dx}] [expr {$y-$dy}] [expr {$w+2*$dx}] [expr {$h+2*$dy}]
}


oo::define BL::Surface method CheckArgs-blur {args} {
	 # expected options and default values
	 # note: these options must be listed in the same order of the Filter-blur arguments
	set Args [dict create \
			-radius 5 \
			]
	set argc [llength $args]
	set i 0
	while { $i < $argc } {
		set opt [lindex $args $i] ; incr i
		switch -- $opt {
			-radius {
				if { $i >= $argc } { error "option \"$opt\" requires a value."}
				set val [lindex $args $i] ; incr i
				if { $val eq "" || ! [string is digit $val] || $val < 1 } {
					error "option \"$opt\" requires an integer > 0"
				}
				dict set Args $opt $val
			}
			default {
				error "Unrecognized option \"$opt\". Valid options are [join [dict keys $Args] ","]"
			}
		}
	}
	return [dict values $Args]
}

oo::define BL::Surface method filter-blur {radius} {
	set bbox [my DirtyArea]
	if { $bbox != {} } {
		set rect [BL::_box2rect {*}$bbox]
		set rect [BL::_enlargedRect {*}$rect $radius $radius]		
		my blur $radius -rect $rect
	}
}


oo::define BL::Surface method CheckArgs-shadow {args} {
	 # expected options and default values
	 # note: these options must be listed in the same order of the Filter-shadow arguments
	set Args [dict create \
			-radius 10 \
			-dxy {3 5} \
			-color [BL::color gray30] \
			]
	set argc [llength $args]
	set i 0
	while { $i < $argc } {
		set opt [lindex $args $i] ; incr i
		switch -- $opt {
			-radius {
				if { $i >= $argc } { error "option \"$opt\" requires a value."}
				set val [lindex $args $i] ; incr i
				if { $val eq "" || ! [string is digit $val] || $val < 1 } {
					error "option \"$opt\" requires an integer > 0"
				}
				dict set Args $opt $val
			}
			-dxy {
				if { $i >= $argc } { error "option \"$opt\" requires a value."}
				set val [lindex $args $i] ; incr i
				if { [llength $val] != 2 } {
					error "option \"$opt\" requires a list of two integers {dx dy}"
				}
				lassign $val dx dy
				if { 
					$dx == "" || ! [string is integer $dx] 
					||
					$dy == "" || ! [string is integer $dy] 
					} {
					error "option \"$opt\" requires a list of two integers {dx dy}"					
					}
				dict set Args $opt $val
			}
			-color {
				if { $i >= $argc } { error "option \"$opt\" requires a value."}
				set val [lindex $args $i] ; incr i
				 # if $val is not a color , raise an error .. ok
				  # dirty trick for checking..
				my push
				  try {
				  	my configure -fill.style $val
				  } on error err {
				  	error "invalid BL::color \"$val\""
				  } finally {
				    my pop
				  }
				dict set Args $opt $val				
			}
			default {
				error "Unrecognized option \"$opt\". Valid options are [join [dict keys $Args] ","]"
			}
		}
	}
	return [dict values $Args]
}

oo::define BL::Surface method filter-shadow {radius dxy shadowColor} {
	try {
		set bbox [my DirtyArea]
		if { $bbox == {} } return

		set rect [BL::_box2rect {*}$bbox]
		set enlargedRect [BL::_enlargedRect {*}$rect $radius $radius]		
	
		lassign $enlargedRect ex ey ew eh
		set shadowSurf [BL::Surface new -format [list $ew $eh PRGB32]]
		$shadowSurf clear -compop CLEAR
		$shadowSurf copy [self] -from $rect -to [list $radius $radius]
		$shadowSurf clear -style $shadowColor -compop SRC_ATOP
		$shadowSurf blur $radius
	
		 # draw the shadow UNDER the current picture (and translated)
		lassign $dxy dx dy		
		incr ex $dx
		incr ey $dy
		
		my rawcopy $shadowSurf -to [list $ex $ey] -compop DST_OVER
	} finally {
		catch {$shadowSurf destroy}
	}
}


 # PRIVATE
oo::define BL::Surface method Swap {otherSurf} {
	set thisSurf [self]
	rename $thisSurf ${thisSurf}__tmp
	rename $otherSurf $thisSurf
	rename ${thisSurf}__tmp $otherSurf
} 

 #
 #  $surface filter _filterType_ ?_filter_arguments_?  _script_
 #
oo::define BL::Surface method filter {filterType args} {
	# parsing args
	set filterArgs [lrange $args 0 end-1]
	set script [lindex $args end]

	 # no way to check if script is valid, until you execute it !
	 # of course it is "complete" or it weren't passed to this method.

	#....  parse filterArgs
	set validFilters {ignore blur shadow}
	if { $filterType ni $validFilters } {
		error "\"$filterType\" is not a supported filter"
	}

	 # special shortcut:
	 # if filterType is "ignore", don't create remove all the supporting surfaces;
	 # just run here the script !
	if { $filterType eq "ignore"} {
		# --------------
		uplevel $script
		# --------------	
		return
	}

	# may raise error .. ok
	set filterParams [my CheckArgs-${filterType} {*}$filterArgs]
	try {
		 # -- init: create a new workSurface an redirect all the 
		 #          next operations to workSurface
		set origSurfName [self]
   		set workSurf [my dup]
  		$workSurf clear -compop CLEAR
		$workSurf DirtyArea on		

		my Swap $workSurf
		 # from now, everything involving $origSurfName is redirected to the new Surfcae
		try {
			# --------------
			uplevel $script
			# --------------
		} finally {
			 # --- turn back the redirection
			my Swap $origSurfName
		}

		# ---------------------------------------
		$workSurf  filter-${filterType} {*}$filterParams
		# ---------------------------------------
			
	} on error err {
	  error $err	
	} on return res {
		return -code return "$res"
	} finally {
		
		set bbox [$workSurf DirtyArea]
		if { $bbox != {} } {
			set rect [BL::_box2rect {*}$bbox]
			set xy [lrange $rect 0 1]
		  	my rawcopy $workSurf -from $rect -to $xy
		}
		 # OK, force a full realignment of the surface state
		my CloneState $workSurf
		$workSurf destroy
	}
}
