# mupdf::widget demo
#
# two mupdf::widget instances sharing and changing the same PDF document
#
catch {console show}

set THIS_DIR [file dirname [file normalize [info script]]]
lappend auto_path $THIS_DIR/..
lappend auto_path $THIS_DIR

set res [catch {package require tkMuPDF 2.0}]
if { $res } {
	tk_messageBox -message {
package mupdf not loaded.
		
Check if package tkMuPDF is installed under a directory listed in "auto_path"
	}
	exit
}
package require mupdf::widget 2.2

namespace eval GUI {
	 # page up/down
	bind MuPDFWidget <Key-Next>  {%W nextpage}
	bind MuPDFWidget <Key-Prior> {%W prevpage}

	 # zoom +/-
	bind MuPDFWidget <Key-plus>  { %W rzoom +1 }
	bind MuPDFWidget <Key-minus> { %W rzoom -1 }
	bind MuPDFWidget <Key-x> { %W zoomfit x }
	bind MuPDFWidget <Key-y> { %W zoomfit y }
	bind MuPDFWidget <Key-z> { %W zoomfit xy }
		 
	bind MuPDFWidget <Control-Key-f> { GUI::openSearchPanel %W }
}

proc GUI::help {} {
	if { [winfo exists .tophelp] } return
	
	toplevel .tophelp -padx 10 -pady 10
	text .tophelp.descr
	pack .tophelp.descr -expand 1 -fill both
		
	.tophelp.descr insert end { \
DEMO keyboards controls
-----------------------------------------
<PageUp>       --  previous page
<PageDown>     --  next page
< + >          -- increment zoom
< - >          -- decrement zoom
<up>/<down>    -- scroll page up/down
<right>/<left> -- scroll page right/left

<X>            -- fit page width
<Y>            -- fit page height
<Z>            -- fit page (best fit)

<ctrl-F>       -- search text ...

DEMO Mouse controls:
-------------------------------------
<MouseWheel>        -- vertical scroll
<Shift><MouseWheel> -- horizontal scrollo

DEMO trackpad controls:
-------------------------------------
two-fingers motion -- vertical/horizontal scroll

}
		.tophelp.descr  configure -state disabled
		wm attributes .tophelp -topmost true
}


proc GUI::doSearch { pdfW } {
	variable textSearch
	$pdfW search $textSearch($pdfW)			
}

proc GUI::openSearchPanel { pdfW } {
	variable textSearch ;# array: index is $pdfW
	
	set panelW $pdfW.searchPanel
	if { [winfo exists $panelW] } return

	set textSearch($pdfW) {}
		
	toplevel $panelW -padx 20 -pady 20
	wm title $panelW "Search ..."
	wm attributes $panelW -topmost true
	 
	entry $panelW.search -textvariable GUI::textSearch($pdfW)  
	button $panelW.ok -text "Search" 
	pack $panelW.search -fill x
	pack $panelW.ok

	$panelW.ok configure -command [list GUI::doSearch $pdfW]
	bind $panelW.search <Return> [list GUI::doSearch $pdfW]

   	 # place the new panel close to the pdfW widget
	set x0 [winfo rootx $pdfW]
	set y0 [winfo rooty $pdfW]
	wm geometry $panelW +[expr {$x0-10}]+[expr {$y0-10}] 

	 # when this panel is closed, reset the search
	bind $panelW <Destroy> [list apply { 
		{W panelW pdfW} {
		     # NOTE: since <Destroy> is propagated to all children,
			 #  the following "if", ensure that this core script is executed
			 #  just once.
			if {  $W != $panelW } return
			$pdfW search ""
			variable textSearch
			unset textSearch($pdfW)
		} GUI} %W $panelW $pdfW]

	focus $panelW.search		
}


proc GUI::formatCoords {L} {
    lassign $L x y
    format "(%.1f, %.1lf)" $x $y
}

proc GUI::save {pdfObj} {
	set filename [$pdfObj fullname]
	set new_filename [file join [file dirname $filename] "new_[file tail $filename]"]
	$pdfObj export "$new_filename"
	tk_messageBox -message "Saved $new_filename"
}

proc GUI::init {} {	
	set w .v1
	frame .v1
		mupdf::widget $w.c
		label $w.pagenum
		pack $w.c -expand 1 -fill both
		pack $w.pagenum
	 
	set w .midframe
	frame $w
	    pack [label $w.blabla -text {
REDs vs BLUEs

These are two
independent views
on the same PDF.

Try to select some text

The left view 
 writes in RED
 and deletes BLUE

The right view 
 writes in BLUE
 and deletes RED

Control-S - save the changes.

See Help 
 for other hints and tips
 ...

}]
		pack [ttk::button $w.help -text "Help..." -command { GUI::help }]
		frame $w.bottom    
			pack [label $w.bottom.coordspdf_lbl -text "  PDF coords (points)  "]
			pack [label $w.bottom.coordspdf -textvariable coordsPdfStr]
		pack $w.bottom -side bottom -pady 10
		 # SHOW PDF coords  (in Points)
		bind MuPDFWidget <Motion> { 
		    set coordsPdfStr  [GUI::formatCoords [%W win2PDFcoords %x %y]] 
		}

	set w .v2
	frame $w
		.v1.c clone $w.c
		label $w.pagenum
		pack $w.c -expand 1 -fill both
		pack $w.pagenum

	pack .v1 .midframe .v2 -side left -expand 1 -fill both
	pack .midframe -expand 0 -fill y
	
	bind .v1.c <<MuPDF.PageLoaded>> { .v1.pagenum configure -text "Page %d" }
	bind .v2.c <<MuPDF.PageLoaded>> { .v2.pagenum configure -text "Page %d" }
	
	 # -------------------------------------------------------------------------
	 # These are the play rules for this demo:
	 # .v1.c  creates RED  annots  and deletes BLUE annots; other annots becomes RED
	 # .v2.c creates BLUE annots  and deletes RED annots; other annots becomes BLUE
	 # -------------------------------------------------------------------------
	set ::RED     #ff0000
	set ::BLUE    #add8e6	
	bind .v1.c <<MuPDF.TextSelected>> { 
		%W annot_add highlight $::RED ; %W selection_clear 
	}
	bind .v2.c <<MuPDF.TextSelected>> { 
		%W annot_add highlight $::BLUE ; %W selection_clear 
	}
	
	bind .v1.c <<MuPDF.AnnotSelected>> { 
		set data [%W annot_get]
		set color [dict get $data -color]
		if { $color eq $::BLUE } {
			%W annot_delete
		} elseif { $color ne $::RED } {
			%W annot_setcolor $::RED
		}
	}	
	bind .v2.c <<MuPDF.AnnotSelected>> { 
		set data [%W annot_get]
		set color [dict get $data -color]
		if { $color eq $::RED } {
			%W annot_delete
		} elseif { $color ne $::BLUE } {
			%W annot_setcolor $::BLUE
		}
	}
}

	GUI::init
	wm title . "Demo#2"
	set pdfObj [mupdf::open [file join $THIS_DIR demo.pdf]]

	update
	.v1.c attach $pdfObj
	.v2.c attach $pdfObj
	.v1.c zoomfit x
	.v2.c zoomfit xy

	bind . <Control-s> [list GUI::save $pdfObj]
	
	bind MuPDFWidget <Enter> { focus %W }
