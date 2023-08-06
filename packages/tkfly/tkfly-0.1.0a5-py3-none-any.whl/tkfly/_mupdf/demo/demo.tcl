# mupdf::widget demo
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
package require mupdf::widget

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

proc GUI::main {filename} {
	wm title . [file tail $filename]
	set pdf [mupdf::open $filename]
	mupdf::widget .c $pdf
	pack .c -side left -expand 1 -fill both

	pack [label .coordspdf_lbl -text "  PDF coords (points)  "]
    pack [label .coordspdf -textvariable coordsPdfStr]
	
	pack [label .info -text {
Try to select same text ...

See Help for other
hints and tips.

<Control>+<s> - save the changes.
}]	
	pack [ttk::button .help -text "Help..." -command { GUI::help }]
	
	
	bind .c <<MuPDF.TextSelected>> { 
		%W annot_add highlight orange ; %W selection_clear 
	}

	 # SHOW PDF coords  (in Points)
	bind MuPDFWidget <Motion> { 
	    set coordsPdfStr  [GUI::formatCoords [%W win2PDFcoords %x %y]] 
	}

	bind . <Control-s> [list GUI::save $pdf]
}

	GUI::main [file join $THIS_DIR demo.pdf]

	update
	.c zoomfit xy
	focus .c