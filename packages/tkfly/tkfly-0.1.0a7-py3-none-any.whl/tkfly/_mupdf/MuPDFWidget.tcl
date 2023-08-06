##  MuPDFWidget.tcl -  a basic PDF-viewer widget
##
## Copyright (c) 2021 <Irrational Numbers> : <aldo.w.buratti@gmail.com> 
##
##
## This library is free software; you can use, modify, and redistribute it
## for any purpose, provided that existing copyright notices are retained
## in all copies and that this notice is included verbatim in any
## distributions.
##
## This software is distributed WITHOUT ANY WARRANTY; without even the
## implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
##
## Changes:
##  7-nov-2021 : *BUGFIX: <<"clone" method raises an error if $win ha no attached pdf.>>
##	              Now FIXED
##	8-nov-2021 : *Added methods "annot_flatten" and "annot_get"		
##               *Now widget instances can do changes (add/change/remove annotations..)
##                and then the changes are propagated
##                to all the widget instances working on the same doc.
##

 # the following non-standard packages should be installed in 'standard paths'
 # OR within this 'lib' subdir
set auto_path [linsert $auto_path 0 [file join [file dirname [file normalize [info script]]] lib]]

package require snit
package require tkMuPDF 2.0

package provide mupdf::widget 2.2


snit::widgetadaptor  mupdf::widget {

	 # Draw a box with rounded corners 
	 #   args is a list of options (see polygon's options)
	 # Return the id
	proc roundedbox {cvs X0 Y0 X1 Y1 radius args} {
		set b [expr {$radius*2.0}]
		set x0 [expr {$X0+$b}]
		set x1 [expr {$X1-$b}]
		set y0 [expr {$Y0+$b}]
		set y1 [expr {$Y1-$b}]
		
		$cvs create polygon   \
			$X0 $y0   $X0 $Y0   $x0 $Y0 $x0 $Y0 \
			$x1 $Y0   $X1 $Y0   $X1 $y0 $X1 $y0\
			$X1 $y1   $X1 $Y1   $x1 $Y1 $x1 $Y1\
			$x0 $Y1   $X0 $Y1   $X0 $y1 $X0 $y1\
			-smooth bezier \
			{*}$args
	}

	 # Draw a shadow as a set of expanding concentic roundedboxes
	 #  one roundedbox for each graylevel 
	 # d is the distance between each concentric roundedbox
	 # - TODO (next) pass a shaded of color instead of grays
	 # This proc returns the list of the itemIDs making of the shadow.
	 #  It is highly recommended to group all these elementes with a grouping tag.
	proc shadowbox {cvs X0 Y0 X1 Y1 d  grayLevels} {
		set radius [expr {4.0*$d}]
		set IDs {}
		foreach g $grayLevels {
			set gg [format %x $g]; 
			set id [roundedbox $cvs $X0 $Y0 $X1 $Y1 $radius -fill #$gg$gg$gg]
			$cvs lower $id
			$cvs move $id 1 3
			lappend IDs $id
			
			set X0 [expr {$X0-$d}]
			set Y0 [expr {$Y0-$d}]
			set X1 [expr {$X1+$d}]
			set Y1 [expr {$Y1+$d}]
		}
		return $IDs
	}


	#=========================================================================
	# == Auxiliary procs on rectangles (boxes) ===============================
	# = a rectangle (aka a box) is simply a list of 4 numbers { x0 y0 x1 y1 }
	 
	 # xc is the fixed point
	proc scalePoint { x xc z } {
		expr {$z*($x-$xc)+$xc}
	}
	proc scaleRect { box C z } {
		lassign $box x0 y0 x1 y1
		lassign $C xc yc
		set x0 [scalePoint $x0 $xc $z]
		set x1 [scalePoint $x1 $xc $z]
		set y0 [scalePoint $y0 $yc $z]
		set y1 [scalePoint $y1 $yc $z]
		return [list $x0 $y0 $x1 $y1]
	}
	proc enlargeRect { rect dx dy } {
		lassign $rect x0 y0 x1 y1
		list [expr {$x0-$dx}] [expr {$y0-$dy}] [expr {$x1+$dx}] [expr {$y1+$dy}]
	}
	proc intersectRect {boxA boxB} {
		lassign $boxA ax0 ay0 ax1 ay1
		lassign $boxB bx0 by0 bx1 by1
		set x0 [expr {max($ax0,$bx0)}]
		set y0 [expr {max($ay0,$by0)}]
		set x1 [expr {min($ax1,$bx1)}]
		set y1 [expr {min($ay1,$by1)}]
		list $x0 $y0 $x1 $y1
	}
	proc isEmptyRect {box} {
		lassign $box x0 y0 x1 y1
		expr {$x0>=$x1 || $y0>=$y1}
	}
	proc containsRect { boxA boxB } {
		lassign $boxA ax0 ay0 ax1 ay1
		lassign $boxB bx0 by0 bx1 by1
		 # be careful: coords are real numbers, so always take care of rounding errors
		 #  consider boxB slight smaller
		set e 0.01
		expr {$ax0<=$bx0+$e  &&  $ax1>=$bx1-$e  &&  $ay0<=$by0+$e  &&  $ay1>=$by1-$e}
	}
	proc viewportBox {cvs} {
		list [$cvs canvasx 0] [$cvs canvasy 0] [$cvs canvasx [winfo width $cvs]] [$cvs canvasy [winfo height $cvs]]
	}

	# == end of Auxiliary procs on rectangles (boxes) ========================
	#=========================================================================


	#=========================================================================
	# This is the key for the propagation of changes made by one mupdfWidget
	# to all the muPdfWidgets working on the same topic (i.e. a pdfObj).
	# -
	# It's basically a MVC pattern:
	# When a mupdfWidget do any change on a pageObj or on the whole pdfObj,
	#  then it must inform the "ChangeMaster".
	#  Then, for every mupdfWidget working on the same pdfObj (and pageObj),
	#   the Changemaster will call a (common) callback (_On!notify).
	#   whose purpose is to adjust the internal data of every involved mupdfWidget
	#   and then invoke a page refresh.
	# Please note that when a mupdfWidget changes sometingh (e.g "adds an annotation to a pag")  
	#  it should not adjust its internal data, nor it should explicitely refresh the page;
	#  these operations will be triggered by the ChangeMaster.
	#=========================================================================

	typevariable _clients ;# clients (muPdfWidget instances) of changeMaster

	typemethod _ChangeMaster_subscribe { client topic } {
		dict set _clients $client $topic
	}
	typemethod _ChangeMaster_unsubscribe { client } {
		 # it's not an error if client is not subscribed
		set _clients [dict remove $_clients $client]
	}
	 # args is a list of key/values:
	 #  keys are:
	 #    -page  - the involved pageObj (or "" meanining "all pages")
	 #    -op    - operation code
	 #    -id    - subject of change (its meaning depends on -op)
	typemethod _ChangeMaster_notify { client theTopic args } {
		dict for {client topic} $_clients {
			if { $theTopic eq $topic } {
				$client _On!Notify {*}$args
			}
		}
	}

	 # this is the (implicit) widget's callback used by ChangeMaster
	 #  used for
	 #  for sending a notification to every mupdfWidget.
	 # args :  see 
	method _On!Notify {args} {
		set page [dict get $args "-page"]		
		 # do nothing if the change is not about the current page (my(page.handle)
		 # **  exception: "" means "all pages"
		if { $page ne "" && $page != $my(page.handle) } return

		set op [dict get $args "-op"]
		set id [dict get $args "-id"]
	
		switch -- $op {
			AnnotChanged {}
			AnnotDeleted {
				$my(canvas) delete "MU.ANNOT && annotID:${id}"		
			}
			AnnotAdded {
				set annotType [$my(page.handle) annot get $id -type]		
			
				foreach {x0 y0 x1 y1} [$my(page.handle) annot get $id -vertices] {
					_annot_add_overlay $my(canvas) $x0 $y0 $x1 $y1 $annotType $id
				}
				 # then zoom ...
				$my(canvas) scale "MU.ANNOT && annotID:${id}" 0 0 $my(zoom) $my(zoom)
			}
		}
		$win _SchedulePaint
	}
	#=========================================================================
	# End of the ChangeMaster section
	#=========================================================================

	typeconstructor {
		# MuPDFWidget is the 'pseudo' class of the mupdf::widget widget.
		
		bind MuPDFWidget <Configure> [list apply {
			{W} { 
				$W _UpdateScrollRegion
				$W _SchedulePaintIfNeeded
				event generate $W <<MuPDF.Configured>> -data [$W reqsize]
		}}  %W ]
		
		bind MuPDFWidget <ButtonPress-1> { focus %W }
		 # scrolling with mousewheel ( or two fingers on a trackpad )
		 # NOTE: ON Windows, with Tcl 8.6.10 , horizontal-scrolling is supported !!
		 #  TO BE TESTED on Mac/Linux?? e su mac 
		bind MuPDFWidget <MouseWheel> { if { %D > 0 } { %W scroll 0 -50 } else { %W scroll 0 50 } }
		bind MuPDFWidget <Shift-MouseWheel> { if { %D > 0 } { %W scroll -50 0 } else { %W scroll 50 0 } }
		 # scrolling with arrow keys ..
		bind MuPDFWidget <Key-Up>    { %W scroll 0 -10 }
		bind MuPDFWidget <Key-Down>  { %W scroll 0 +10 }
		bind MuPDFWidget <Key-Left>  { %W scroll -10 0 }
		bind MuPDFWidget <Key-Right> { %W scroll +10 0 }
		
		# other binding for UI control may be added/changed at run-time
		# ( even before creating the 1st instance of the widget )

		# init ChangeMaster
		set _clients [dict create]
	}

	option -extramargin -type ::snit::pixels -default 30 -configuremethod _SetOption
	option -cursor -default {} -configuremethod _SetCursor
	option -foundtextcolor	-default red
	option -selectioncolor	-default yellow
	option -zoomratio -type {::snit::double -min 1.01} -default 1.4142
	
	delegate option -background to hull
	option -shadows -default {}
	delegate option -width to hull
	delegate option -height to hull    
	delegate method canvasx to hull
	delegate method canvasy to hull
	 # xview, yview, x/yscrollcommand, x/yscrollincrement,  
	 #  are required to enable standard interaction with scrollbars
	 # xview and yvyew are internally redefined.
	delegate option -xscrollcommand to hull
	delegate option -yscrollcommand to hull
	delegate option -xscrollincrement to hull
	delegate option -yscrollincrement to hull
	
	
	 # Note: widget cursor must be independent of the underlying canvas cursor
	method _SetCursor {option value} {
		set options(-cursor) $value
		$my(canvas) configure -cursor $value
	}
	method _ResetCursor {} {
		$my(canvas) configure -cursor [$win cget -cursor]
	}

	method _SetOption {option value} {
		 # special checks ..
		switch -- $option {
			-extramargin {
				set v [winfo pixels $win $value]
				if { $v < 0 } {
					error "option's $option value must be > 0"
				}
			}
		}
		set options($option) $value
		switch -- $option {
			-extramargin { 
				$win _UpdateScrollRegion
				$win _SchedulePaintIfNeeded
			}
		}
	}

	# GENERAL INFO:
	#  A mupdf::widget is made of a canvas containing:
	#  * a rectangle item ( tag MU.PAGEBOX )
	#    large as the whole zoomed page
	#  * an image-item ( tag MU.IMAGEBOX )
	#   containing the rendered tk-photo of a pdf page, or just
	#   a portion of the page properly placed.

	  # There's only one instance variable : the array my()
	variable my -array {}	
	 # instance members:
	 #	canvas		- just an alias for the unpronounceable $hull 
	 #	pdf.handle	- the PDF document Handle. ..  ?? Must be specified at widget-creation-time.
	 #	page.number	- the number of the currently displayed page.
	 #  page.handle  - (bound to page.number) the PDF handle for the current page
	 #	tkimage		- the (constant) tk-image containing the rendering of the current page
	 #	              ( or better, the visible portion of the page .. plus some margins ...)
	 #	zoom		- the current zoom factor
	 #  search.obj     
	 #  search.needle - the searched needle
	 #  search.page.number - the page search.boxes are about
	 #  search.boxes  - a list of boxes returned by [$my(search.obj) find ...]
	 #	scheduled	- a flag for scheduling the refresh
	 #
	 #  currentAnnotType
	 #  currentAnnotID
	 #
	 #  textboxes        - list of text bboxes (a sequence of x0 y0 x1 x1 ... )
	 #  indexOfTextboxes   list of item-ID. Each item-id is a canvas rectangle 
	 #                     related to a textbox 
	 #  textSelectionStart - starting point (in pdf coord) of the text selection

	constructor {{pdfHandle {}} args} {
		installhull using canvas \
			-highlightthickness 0 \
			-borderwidth 0
		
		set my(canvas) $hull
		 # scrollincrement for smooth scroll
		$my(canvas) configure -xscrollincrement 1 -yscrollincrement 1
		 # -confine 1 needed for using a scrolleregion
		$my(canvas) configure -confine 1
		
		$my(canvas) create rectangle {0.0 0.0 0.0 0.0} \
			-fill gray12 -stipple gray12 -outline {} \
			-tags MU.PAGEBOX
		set my(tkimage) [image create photo]
		$my(canvas) create image 0.0 0.0 -anchor nw -image $my(tkimage) -tags MU.IMAGEBOX
		
		 # WARNING: This is the the recommended -background and its -shadows
		 #  if you change -background, then it's your responsability
		 #  to adapt -shadows
		 # LIMITATIONS: since currently shadows are only gray-level shadows
		 #  -background should be a gray,too  
		 # ( unless you decide to "$win configure -shadows {} )
		 # WARNING: since changing -background and -shadows is discouraged
		 #  currently if you change -shadows, the effect will be visible
		 #  only after reloading ir resizing (zoom) the page.
		$win configure -background #f3f3f3
		$win configure -shadows { 205 213 224 233 238 241 242 }
		
		set my(zoom) 1.0
		set my(page.number)	0
		set my(pdf.handle) {}
		set my(search.obj) {}
		set my(scheduled) false
		set my(currentAnnotID) {}

if { $::tcl_platform(os) eq "Darwin" } {
		$win configure -selectioncolor orange
}
		
		 # TODO: find a better cursor ...
		$my(canvas) bind MU.ANNOT <Enter> [list $my(canvas) configure -cursor center_ptr]
		$my(canvas) bind MU.ANNOT <Leave> [list $win _ResetCursor]
		$my(canvas) bind MU.ANNOT <ButtonPress-1> [mymethod _annotStartEditing %X %Y]
		
		$my(canvas) bind MU.IMAGE <Enter> [list $my(canvas) configure -cursor tcross]
		$my(canvas) bind MU.IMAGE <Leave> [list $win _ResetCursor]

		$my(canvas) bind MU.TEXT <Enter> [list $my(canvas) configure -cursor xterm]
		$my(canvas) bind MU.TEXT <Leave> [list $win _ResetCursor]
				
		$my(canvas) bind MU.TEXT <ButtonPress-1> [mymethod _textSelectionStart %x %y]
		$my(canvas) bind MU.TEXT <B1-Motion> [mymethod _extendTextSelection %x %y]
		$my(canvas) bind MU.TEXT <ButtonRelease-1> [mymethod _notifyTextSelection]

		bindtags $win [linsert [bindtags $win] 1 MuPDFWidget]		

		if { $pdfHandle ne ""} {
			$win attach $pdfHandle ; # fail on bad value.  ok 
		}
		
		$win configurelist $args		
		$win _SchedulePaint
	}

	destructor {
		$type _ChangeMaster_unsubscribe $win
		catch {image delete $my(tkimage)}
	}

	method reqsize {} {
		lassign [$my(canvas) coords MU.PAGEBOX] x0 y0 x1 y1
		list \
			[expr {2*$options(-extramargin)+($x1-$x0)}] \
			[expr {2*$options(-extramargin)+($y1-$y0)}]
	}

	 # $w attach         ;#  GET current pdfHandle
	 # $w attach ""      ;#  SET current pdfHandle to ""   (i.e. reset the attach)
	 #                       my(tkimage) is reset
	 # $w attach  $pH    ;#  SET current pdfHandle. restart from page 0
	 # $w attach  $pH  n ;#  SET current pdfHandle. restart from page n  (or the closest to n)
	method attach {args} {
		switch -- [llength $args] {
			0 { # get !
				return $my(pdf.handle)
			}
			1 -
			2 { # set !
				set pdfH [lindex $args 0]
				set pagenum [lindex $args 1]
				if { $pagenum eq "" } { set pagenum 0 }
				if { $pdfH eq {} } {
					$type _ChangeMaster_unsubscribe $win

					set my(pdf.handle) {}
					set my(page.handle) {}
					if { $my(search.obj) ne {} } {
						catch { $my(search.obj) destroy }
						set my(search.obj) {}
					}
					# reset tkimage.
					image create photo $my(tkimage)
					$win _ResetSearch
					$win _ResetOverlays
					return
				}
				
				if { ! [mupdf::isobject $pdfH] || [mupdf::classinfo $pdfH] != "::mupdf::Doc" } {
					error "\"$pdfH\" is not a valid pdf-object"
				}
				set my(pdf.handle) $pdfH
				
				$type _ChangeMaster_subscribe $win $pdfH
				
				# create a new TextSearch related to $pdfH.
				# When $pdfH will be (externally) destroyed, then
				#  all the related objects (opened pages and text-search objs)
				#  will be destroyed.
				set my(search.obj) [mupdf::TextSearch new $pdfH]
				$win _ResetSearch
				$win _ResetOverlays
				
				set npages [$my(pdf.handle) npages]
				if { $pagenum >= $npages } {
					set pagenum [expr {$npages-1}]
				}
				$win page $pagenum
				$win _SchedulePaint
				}
			default {
				error "method pdfHandle: bad params"
			}
		}
	}

	 # create a new mupdf::widget
	method clone {newWin} {
		$type  $newWin [$win attach]
		 # copy all the $win options
		foreach cfg [$win configure] {
			lassign $cfg  opt dummy dummy dummy val
			$newWin configure $opt $val
		}
		set page [$win page]
		if { [$newWin attach] ne "" } {
			$newWin page $page
			$newWin zoom [$win zoom]
		}
		return $newWin
	}

	# just for testing. Not a supported method !
method hull {} { return $hull }

	method _UpdatePageBox {} {
		if { $my(pdf.handle) eq {} } return
		set pageBox [list 0.0 0.0 {*}[$my(page.handle) size]]
		set zoomedPageBox [scaleRect $pageBox {0.0 0.0} $my(zoom)]
		$my(canvas) coords MU.PAGEBOX $zoomedPageBox
		$win _UpdateScrollRegion
		
		 # note: an existing shadowbox cannot be scaled, since scaling
		 #  will also change the radius of their rounded corners (this is bad).
		 # For this reason, a shadowbox should be destroyed and recreated
		$my(canvas) delete MU.SHADOW
		set IDs [shadowbox $my(canvas) {*}$zoomedPageBox 1.0 \
					$options(-shadows) \
				]
		foreach id $IDs { 
			$my(canvas) addtag MU.SHADOW withtag $id
		}
		event generate $win <<MuPDF.Configured>> -data [$win reqsize]
	}

	 # -scrollregion should be equal to the MU.PAGEBOX area, *plus*  extra margins
	 # note: extra margins provide a better visual feedback about the page boundary.
	method _UpdateScrollRegion {} {
		set zoomedPageBox [$my(canvas) coords MU.PAGEBOX]
		lassign $zoomedPageBox x0 y0 x1 y1
		set W [winfo width $win]
		set dx [expr {($W-($x1-$x0))/2.0}]
		if { $dx < $options(-extramargin) } {
			set dx $options(-extramargin)
		}
		set H [winfo height $win]
		set dy [expr {($H-($y1-$y0))/2.0}]
		if { $dy < $options(-extramargin) } {
			set dy $options(-extramargin)
		}
		$my(canvas) configure -scrollregion [list [expr {$x0-$dx}] [expr {$y0-$dy}] [expr {$x1+$dx}] [expr {$y1+$dy}]]              
	}

	 # $w zoom        ;#  GET current zoom
	 # $w zoom  2.1   ;#  SET current zoom	 
	method zoom {args} {
		switch -- [llength $args] {
			0 { # get !
				return $my(zoom)
			}
			1 { # set !
				 # side effects:
				 #  resize the MU.PAGEBOX rectangle-item
				 #  resize the scrollregion
				set oldzoom $my(zoom)
				set val [lindex $args 0]
				set my(zoom) [expr {double($val)}]
				
				$win _UpdatePageBox
				$win _ResizeOverlays $oldzoom $my(zoom)
				$win _UpdateSearchBoxes
				$win _SchedulePaint
			}
			default {
				error "method zoom: bad params"
			}
		}
	}

	method rzoom {delta} {
		if { $delta > 0 } {
			$win zoom [expr {$my(zoom)*$options(-zoomratio)}]
		} else {
			$win zoom [expr {$my(zoom)/$options(-zoomratio)}]
		}
	}

	method zoomfit {mode} {
		if { $my(pdf.handle) eq {} } return
		
		set viewBox [viewportBox $win]
		lassign [viewportBox $win] vx0 vy0 vx1 vy1
		lassign [$my(page.handle) size] dx dy
		set m $options(-extramargin)
		switch -- $mode {
			x  {
				set bestzoom [expr {($vx1-$vx0-2*$m)/$dx}]
			}
			y {
				set bestzoom [expr {($vy1-$vy0-2*$m)/$dy}]
			}
			xy {
			set bestXzoom [expr {($vx1-$vx0-2*$m)/$dx}]
			set bestYzoom [expr {($vy1-$vy0-2*$m)/$dy}]
			set bestzoom [expr {min($bestXzoom,$bestYzoom)}]
			}
			default { error "valid mode is one of x, y or xy"}
		}
		$win zoom $bestzoom
	}

	 # I think this is an old method no more necessary after the
	 #  introduction of _UpdateScrollRegion bound to <Configure>
	method align {where} {
		switch -- $where {
		 left {
			$win xview moveto 0.0
		 }
		 right {
			lassign [$win xview] a b
			if { $b == 1.0 } {
				 # notes about 10000 pages ...
				 #  in this context a page is the displayed window (i.e. the viewport)
				 #  Scrolling by 1 page means that the viewport is shifted by
				 #  9/10 of its size, and of course this shift is limited by the scrollregion.
				 # To be sure to scroll the page till its right edge, scroll it
				 #  10000 times ! (remember: the scrollregion limits this shift)
				 # Thanks to tk-canvas logic, we don't need to use maths !
				$win xview scroll -10000 pages
			} else {
				$win xview scroll +10000 pages
			}
		 }
		 top {
			$win yview moveto 0.0
		 }
		 bottom {
			lassign [$win yview] a b
			if { $b == 1.0 } {
				$win yview scroll -10000 pages
			} else {
				$win yview scroll +10000 pages
			}
		 }
		 default { error "valid values are: left, right, top, bottom" }
		}
	}

	 # same notes for the above 'align' method ...
	method center {mode} {
		set Wdx [winfo width $win]
		set Wdy [winfo height $win]		
		lassign [$my(page.handle) size] Pdx Pdy
		
		set Pcx [expr {$Pdx/2.0}]
		set Pcy [expr {$Pdy/2.0}]
		set Wcx [expr {$Wdx/2.0}]
		set Wcy [expr {$Wdy/2.0}]
		
		switch -- $mode {
		  x  {
		  	set dragx  [expr {[$win canvasx 0] -($my(zoom)*$Pcx-$Wcx)}]
		  	set dragx  [expr {round($dragx)}]
		  	set dragy  0
		  }
		  y {
		  	set dragx 0
			set dragy  [expr {[$win canvasy 0] -($my(zoom)*$Pcy-$Wcy)}]
		  	set dragy  [expr {round($dragy)}]
		  }
		  xy {
		  	set dragx  [expr {[$win canvasx 0] -($my(zoom)*$Pcx-$Wcx)}]
		  	set dragx  [expr {round($dragx)}]
			set dragy  [expr {[$win canvasy 0] -($my(zoom)*$Pcy-$Wcy)}]
		  	set dragy  [expr {round($dragy)}]
		  }
		  default { error "valid mode is one of x, y or xy"}
		}
		$win scan mark 0 0
		$win scan dragto $dragx $dragy 1
	}

	 # $w page        ;#  GET current page (page.number)
	 # $w page  3     ;#  SET current page	 
	method page {args} {
		switch -- [llength $args] {
		0 { # get !
			return $my(page.number)
		}
		1 { # set !
			set val [lindex $args 0]
			set my(page.handle) [$my(pdf.handle) getpage $val]  ;# may raise error ..
			set my(page.number) $val
			
			$win _UpdatePageBox
			$win _CreateOverlays
			$win _UpdateSearchBoxes	
			$win _SchedulePaint
			
			event generate $win <<MuPDF.PageLoaded>> -data $my(page.number)
			return
		}
		default {
			error "method page: bad params"
		}
		}
	}

	method nextpage {} { 
		set res [catch { $win page [expr {$my(page.number) +1}] }]
		expr {$res ? false: true} 
	}
	method prevpage {} {
		set res [catch { $win page [expr {$my(page.number) -1}] }]
		expr {$res ? false: true} 
	}

	method scroll {dx dy} {	
		$my(canvas) xview scroll $dx units
		$my(canvas) yview scroll $dy units
		$win _SchedulePaintIfNeeded
	}

	 # redefined !
	method scan {cmd args} {
		$my(canvas) scan $cmd {*}$args
		if { $cmd == "dragto" } {
			$win _SchedulePaintIfNeeded
		}
	}

	 # redefined !
	method xview {args} {
		set res [$my(canvas) xview {*}$args]
		$win _SchedulePaintIfNeeded
		return $res
	}
	method yview {args} {
		set res [$my(canvas) yview {*}$args]
		$win _SchedulePaintIfNeeded
		return $res
	}

	 # Given a screen-point (x,y) of the widget ( (0,0) is the top left corner ),
	 # returns the corresponding point in the currently displayed pdf-page coord system.
	 # (result depend on the current zoom factor and page displacement)
	 # NOTE: PDF coord sys  ( 0,0 is lower-left corner, Y upwards)
	method win2PDFcoords {x y} {
		 # TO DO - you should store pdf size in my(...) (update it when page is changes)
		lassign [$my(page.handle) size] dx dy
		set px [expr {[$my(canvas) canvasx $x]/$my(zoom)}]
		set py [expr {$dy - [$my(canvas) canvasy $y]/$my(zoom)}]
		return [list $px $py]
	}

	method win2page {x y} {
		set px [expr {[$my(canvas) canvasx $x]/$my(zoom)}]
		set py [expr {[$my(canvas) canvasy $y]/$my(zoom)}]
		return [list $px $py]
	}

 	method _ResetOverlays {} {
		$my(canvas) delete MU.OVERLAY
	}
	method _ResizeOverlays {oldzoom newzoom} {
		set zf [expr {$newzoom/$oldzoom}]
		$my(canvas) scale MU.OVERLAY 0 0 $zf $zf
	}


 	method _ResetSearch {} {
 		$my(canvas) delete MU.SEARCHBOX
		set my(search.needle) ""
		set my(search.page.number) -1
		set my(search.boxes) {} 
	}
	 # $w search                     ;# GET current searched needle
	 # $W search ""                  ;# RESET search
	 # $w search abc ?-currpageonly true/false? ;# SET search from currentpage (and limit/nolimit to this page only)
	method search {args} {
		switch -- [llength $args] {
		  0 { # GET
			return $my(search.needle)
		  }
		  default {
		  	set args [lassign $args needle]
			 # set defaults
			set startpage $my(page.number) ;# current page
			set currpageonly false
			while { [llength $args] > 0 } {
				set args [lassign $args opt val]
				switch -- $opt {
				  -startpage { set startpage $val }
				  -currpageonly { set currpageonly $val }				  
				  default { error "unrecognized option \"$opt\"; valid values are: -startpage" }
				}
			}
			  # end of parsing; let's start
			$win _ResetSearch
			if { $needle == "" } return
			
			$my(search.obj) currpage $startpage
			set textBoxList [$my(search.obj) find $needle -max 1 -currpageonly $currpageonly]
			 
			if { [llength $textBoxList] == 0 } return
			
			set my(search.needle) $needle
			set pageNum [lindex $textBoxList 0 0]
			if { $pageNum == $my(page.number) } {
				$win _UpdateSearchBoxes			
			} else {
				$win page $pageNum  ;# this page-change will trigger _UpdateSearchBoxes
			}
		  }
		}
	}

	method _UpdateSearchBoxes {} {
		if { $my(pdf.handle) eq {} } return
		if { $my(search.needle) == "" } return
		if { $my(search.page.number) != $my(page.number) } {
			$my(search.obj) currpage $my(page.number)
			set L [$my(search.obj) find $my(search.needle) -currpageonly true -max 100] ;# want more ?
			 # each item of L is a list of {pageNum box} ; extract just the boxes.
			set my(search.boxes) [lmap item $L { lindex $item 1 } ]
			
			set my(search.page.number) $my(page.number)
		}
 		$my(canvas) delete MU.SEARCHBOX
		foreach box $my(search.boxes) {
			$my(canvas) create rectangle [scaleRect $box {0 0} $my(zoom)] \
				-outline $options(-foundtextcolor) -tags MU.SEARCHBOX
		}
	}

	method _RedrawIfNeeded {} {
		set viewBox [viewportBox $win]
		set zoomedPageBox [$my(canvas) coords MU.PAGEBOX]
		lassign [$my(canvas) coords MU.IMAGEBOX] xo yo
		set tkimageBox [list $xo $yo [expr {$xo+[image width $my(tkimage)]}] [expr {$yo+[image height $my(tkimage)]}]]   
		if { ! [containsRect $tkimageBox [intersectRect $viewBox $zoomedPageBox]] } {
			 # don't reschedule; paint now !
			$win _DoPaint
		}
	}

	method _SchedulePaintIfNeeded {} {
		set viewBox [viewportBox $win]
		set zoomedPageBox [$my(canvas) coords MU.PAGEBOX]
		lassign [$my(canvas) coords MU.IMAGEBOX] xo yo
		set tkimageBox [list $xo $yo [expr {$xo+[image width $my(tkimage)]}] [expr {$yo+[image height $my(tkimage)]}]]   
		if { ! [containsRect $tkimageBox [intersectRect $viewBox $zoomedPageBox]] } {
			$win _SchedulePaint
		}
	}

	method _SchedulePaint {} {
		if { ! $my(scheduled) } {
			set my(scheduled) true
			 # invalidate the image
			image create photo $my(tkimage)
			 # note: after 0 is BEFORE after idle
			after 0 [mymethod _DoPaint]
			 # todo: save id for after cancel
		}
	}

	method _DoPaint {} {
		set my(scheduled) false
		if {$my(pdf.handle) eq "" } return
		
		set viewBox [viewportBox $win]
		set zoomedPageBox [$my(canvas) coords MU.PAGEBOX]  
		set viewBox [intersectRect $viewBox $zoomedPageBox]
		 # create a larger rectangle
		set viewBoxExtended [enlargeRect $viewBox 500 500] ;# .. todo:  extra margin should depend on .. 
		set viewBoxExtended [intersectRect $viewBoxExtended $zoomedPageBox]
		
		 # reset tkimage, so that saveImage will return a properly sized image
		image create photo $my(tkimage)
		 # move the anchor point for the image
		lassign $viewBoxExtended x0 y0   
		$my(canvas) coords MU.IMAGEBOX  $x0 $y0
		
		set pdfBox [scaleRect $viewBoxExtended {0 0} [expr {1.0/$my(zoom)}]]
		$my(page.handle) saveImage $my(tkimage) -zoom $my(zoom) -from {*}$pdfBox
	}

	#  === Pdf-Annotations and Text-Selections stuff ============

	# After loading a pdf-page,
	#  prepare some invisible boxes for the image/text selection
	#  and for highilighting the pdf-annotations.
	# All these special boxes are tagged "MU.OVERLAY";
	#  - pdf-blocks also have tags "MU.BLOCK" and (MU.IMAGE or MU.TEXT)
	#  - pdf-lines  also have tags "MU.SELECTEDTEXT"
	#  - pdf-annotations also have tags "MU.ANNOT" and "annotID:xxx"
	#    (xxx is the id of the annotation (it is unique on the whole pdf))
	method _CreateOverlays {} {
		$win _ResetOverlays
		
		 # draw the blocks with the original (pdf) size.
		 # They will be then scaled at the end of this proc
		foreach block  [$my(page.handle) blocks] {
			set bbox [lassign $block type]
			if { $type == "textblock" } {
				set type MU.TEXT
			} else {
				set type MU.IMAGE
			}
			$my(canvas) create rectangle $bbox -fill {} -outline {} \
				-tags [list MU.OVERLAY MU.BLOCK $type]
		}
		
		# --- prepare hidden textboxes for text selection
		set my(textboxes) [$my(page.handle) lines]
		
		# for each textbox in my(textboxes) create a dummy, hidden
		#  canvas-rectangle.
		# During the interactive selection phase, some of these
		#  rectangle will be highlighted (even partially).
		# my(indexOfTextboxes) holds the correspondence between
		#  each element of my(textboxes) and its canvas-rectangle.
		 # More precisely, the i-th element of my(indexOfTextboxes) 
		 #  is the itemID of a tagged MU.SELECTEDTEXT dummy recytangle.
		set my(indexOfTextboxes) {}
		foreach box $my(textboxes) {
			lappend my(indexOfTextboxes) [$my(canvas) create rectangle 0 0 0 0 \
				-state hidden -tags {MU.OVERLAY MU.SELECTEDTEXT} \
			]
		}
if { $::tcl_platform(os) eq "Darwin" } {
		 # the stipple effect used as a sort of semi-transparency is not supporte on Darwin.
		$my(canvas) itemconfigure "MU.OVERLAY && MU.SELECTEDTEXT" -fill {} -outline red
} else {
		$my(canvas) itemconfigure "MU.OVERLAY && MU.SELECTEDTEXT" -fill yellow -stipple gray12
}

		 #  --- overlays for Annotations
		foreach annotID [$my(page.handle) annots] {
			set annotType [$my(page.handle) annot get $annotID -type]
			if { $annotType ni { "highlight" "underline" "strikeout" "squiggly" } } continue
			
			foreach {x0 y0 x1 y1} [$my(page.handle) annot get $annotID -vertices] {
				_annot_add_overlay $my(canvas) $x0 $y0 $x1 $y1 $annotType $annotID
			}
		}
		
		# scaling all the overlays..
		$win _ResizeOverlays 1.0 $my(zoom)
	}


	method _annotStartEditing {X Y} {
		$win _annotEndEditing
		
		 # get the current annotID and annotType...
		set currID ""
		foreach tag [$my(canvas) gettags current] {
			if { [regexp {^annotID:(.*)} $tag _ currID] ==1 } break
		}
		set annotType ""
		foreach tag [$my(canvas) gettags current] {
			if { [regexp {^annotType:(.*)} $tag _ annotType] ==1 } break
		}
		
		if {$currID == "" } {
			# severe error if ID not found !!
			return
		}
		set my(currentAnnotID) $currID
		
		 # add temporary annot's marks - to all boxes withtag annotID:xxx
		$my(canvas) itemconfigure "MU.ANNOT && annotID:$my(currentAnnotID)" -outline red -width 3
		
		 # You could (should) bind a proc to this event.
		 # Be aware that your proc should not be an async/delayed proc
		 # because after it is completed, the current selection is cleared.
		 # It is safe to open a tk_popup, since tk_popup is a blocking op
		 #  (tested on Windows, to be tested on Mac/Linux)
		event generate $win <<MuPDF.AnnotSelected>> -when now -x $X -y $Y -data $annotType 
		$win _annotEndEditing
	}

	method _annotEndEditing {} {
		# remove temporary annot's marks
		$my(canvas) itemconfigure "MU.ANNOT && annotID:$my(currentAnnotID)" -outline {} -width 0
		set $my(currentAnnotID) {}
	}

	method annot_get {} {
		if { $my(currentAnnotID) == {} } return
		$my(page.handle) annot get $my(currentAnnotID)
	}
	
	method annot_flatten {} {
		if { $my(currentAnnotID) == {} } return
		$my(page.handle) annot flatten $my(currentAnnotID)
		# op flatten is like op "AnnotDeleted"

		$type _ChangeMaster_notify $win $my(pdf.handle) -op AnnotDeleted -id $my(currentAnnotID) -page $my(page.handle)
		set my(currentAnnotID) ""
	}

	method annot_setcolor {color} {
		if { $my(currentAnnotID) == {} } return
		$my(page.handle) annot set $my(currentAnnotID) -color $color

		$type _ChangeMaster_notify $win $my(pdf.handle) -op AnnotChanged -id $my(currentAnnotID) -page $my(page.handle)
	}

	method annot_delete {} {
		if { $my(currentAnnotID) == {} } return
		$my(page.handle) annot delete $my(currentAnnotID)
		
		$type _ChangeMaster_notify $win $my(pdf.handle) -op AnnotDeleted -id $my(currentAnnotID) -page $my(page.handle)
		set my(currentAnnotID) {}
	}

# =========================  text selection ==================================

	method selection_clear {} {
		# remove temporary annot's marks
		$my(canvas) itemconfigure "MU.SELECTEDTEXT" -state hidden
		 # clean the selection
		set my(selectedboxes) {}
	}

	  # TO DO:  add in tkMuPDF a method returning the selected text (from point A to point B)
	  #   then add in MuPDFWidget a method returning the text.
	
	method _notifyTextSelection {} {
		if { $my(selectedboxes) eq {} } return
		event generate $win <<MuPDF.TextSelected>>
	}

	 #  Based on the current selection, 
	 #   add a pdf annotation, and clear the selection.
	method annot_add {annotType color} {
		if { $my(selectedboxes) eq {} } return		
		set annotID [$my(page.handle) annot create $annotType -color $color -vertices $my(selectedboxes)]
		
		$type _ChangeMaster_notify $win $my(pdf.handle) -op AnnotAdded -id $annotID -page $my(page.handle)
	}

	proc _annot_add_overlay {cvs x0 y0 x1 y1 annotType annotID} {
		 # the rectangle should be invisible but not hidden
		 # otherwise bindings on MU.ANNOT  won't work
		$cvs create rectangle $x0 $y0 $x1 $y1 \
			-fill {} -outline {} \
			-tags [list MU.OVERLAY MU.ANNOT "annotType:$annotType" "annotID:$annotID"]
	}
	
	proc swap {varA varB} {
		upvar $varA A
		upvar $varB B
		set z $A
		set A $B
		set B $z
		return
	}

	 # get the index of the bbox closer (or containing) the point P
	proc _checkin { P boxes } {
		lassign $P X Y    
		set idx 0
		set minDist 1e6
		foreach box $boxes {
			lassign $box x0 y0 x1 y1
			if { $x0 <= $X && $X <= $x1 && $y0 <= $Y && $Y <= $y1 } {
				return $idx
			}
			# proximity test
			if { $X < $x0 } { 
				set distx [expr {$x0-$X}] 
			} elseif { $X > $x1 } {
				set distx [expr {$X-$x1}]
			} else {
				set distx 0.0
			}
			if { $Y < $y0 } { 
				set disty [expr {$y0-$Y}] 
			} elseif { $Y > $y1 } {
				set disty [expr {$Y-$y1}]
			} else {
				set disty 0.0
			}
			
			set dist  [expr {max($distx,$disty)}]
			
			if { $dist < $minDist} {
				set minDist $dist
				set minIdx $idx
			}
			incr idx
		}
		return $minIdx
	}


	method _textSelectionStart {x y} {
		set my(selectedboxes) {}
		set my(textSelectionStart) [$win win2page $x $y]
	}

	method _extendTextSelection {x y} {
		$win _textSelection $my(textSelectionStart) [$win win2page $x $y] 
	}


	  # A and B are points (in pdf-coords)
	  #  side effect: save in my(selectedboxes)   all the coords (in pdf coords )
	method _textSelection {A B} {
		$win selection_clear
		 # NOTE: textboxes are expressed in pdf-coords (independent of the zoom)
		set idxA [_checkin $A $my(textboxes)]
		set idxB [_checkin $B $my(textboxes)]
		if { $idxA > $idxB } {
			swap idxA idxB
			swap A B
		}
		
		# special case: idxA == idxB   ( just a part of 1 textbox )
		if { $idxA == $idxB } {
			# get the bbox of index idxA       
			lassign [lindex $my(textboxes) $idxA] bbx0 bby0 bbx1 bby1
			set itemID [lindex $my(indexOfTextboxes) $idxA]
			
			# get the reduced the bbox
			set ax [lindex $A 0]
			set bx [lindex $B 0]
			if { $ax > $bx } { swap ax bx }
			
			set cx0 [expr {max($ax,$bbx0)}]
			set cx1 [expr {min($bx,$bbx1)}]
			
			# resize and show the related MU.SELECTEDTEXT
			lappend my(selectedboxes) $cx0 $bby0 $cx1 $bby1
			$my(canvas) coords $itemID $cx0 $bby0 $cx1 $bby1
			$my(canvas) itemconfigure $itemID -state normal
if { $::tcl_platform(os) eq "Darwin" } {
			# the stipple effect used as a sort of semi-transparency is not supporte on Darwin,
		 	#  therefore use just the outline (fill is {})
			$my(canvas) itemconfigure $itemID -outline $options(-selectioncolor)
} else {
			$my(canvas) itemconfigure $itemID -fill $options(-selectioncolor)
}
			$my(canvas) scale $itemID 0 0 $my(zoom) $my(zoom)
			return
		}
		
		# else ... more than 1 textbox 
		
		# 1st textbox
		set ax [lindex $A 0]
		
		lassign [lindex $my(textboxes) $idxA] bbx0 bby0 bbx1 bby1
		set itemID [lindex $my(indexOfTextboxes) $idxA]
		
		set cx0  [expr {max($ax,$bbx0)}]
		lappend my(selectedboxes) $cx0 $bby0 $bbx1 $bby1
		$my(canvas) coords $itemID $cx0 $bby0 $bbx1 $bby1
		$my(canvas) itemconfigure $itemID -state normal
		$my(canvas) scale $itemID 0 0 $my(zoom) $my(zoom) 
		
		# intermediate textboxes: from idxA+1 to idxB-1
		for {set idx [expr {$idxA+1}] } {$idx<=[expr {$idxB-1}]} {incr idx} {
			set itemID [lindex $my(indexOfTextboxes) $idx]
			
			lappend my(selectedboxes) {*}[lindex $my(textboxes) $idx]
			$my(canvas) coords $itemID [lindex $my(textboxes) $idx]
			$my(canvas) itemconfigure $itemID -state normal
			$my(canvas) scale $itemID 0 0 $my(zoom) $my(zoom)         
		}
		
		# last line idxB
		set bx [lindex $B 0]
		
		lassign [lindex $my(textboxes) $idxB] bbx0 bby0 bbx1 bby1
		set itemID [lindex $my(indexOfTextboxes) $idxB]
		
		if {$bx <$bbx0} { set bx $bbx0 }
		if {$bx >$bbx1} { set bx $bbx1 }
		
		lappend my(selectedboxes) $bbx0 $bby0 $bx $bby1
		$my(canvas) coords $itemID $bbx0 $bby0 $bx $bby1
		$my(canvas) itemconfigure $itemID -state normal
		$my(canvas) scale $itemID 0 0 $my(zoom) $my(zoom)
		return
	}

}
