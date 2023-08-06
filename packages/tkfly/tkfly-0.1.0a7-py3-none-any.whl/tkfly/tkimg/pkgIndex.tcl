if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded zlibtcl 1.2.13 [list load [file join $dir tcl9zlibtcl1213.dll]]
} else {
    package ifneeded zlibtcl 1.2.13 [list load [file join $dir zlibtcl1213.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded pngtcl 1.6.38 [list load [file join $dir tcl9pngtcl1638.dll]]
} else {
    package ifneeded pngtcl 1.6.38 [list load [file join $dir pngtcl1638.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded tifftcl 4.4.0 [list load [file join $dir tcl9tifftcl440.dll]]
} else {
    package ifneeded tifftcl 4.4.0 [list load [file join $dir tifftcl440.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded jpegtcl 9.5.0 [list load [file join $dir tcl9jpegtcl950.dll]]
} else {
    package ifneeded jpegtcl 9.5.0 [list load [file join $dir jpegtcl950.dll]]
}
# -*- tcl -*- Tcl package index file
# --- --- --- Handcrafted, final generation by configure.

if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::base 1.4.14 [list load [file join $dir tcl9tkimg1414.dll]]
} else {
    package ifneeded img::base 1.4.14 [list load [file join $dir tkimg1414.dll]]
}
# Compatibility hack. When asking for the old name of the package
# then load all format handlers and base libraries provided by tkImg.
# Actually we ask only for the format handlers, the required base
# packages will be loaded automatically through the usual package
# mechanism.

# When reading images without specifying it's format (option -format),
# the available formats are tried in reversed order as listed here.
# Therefore file formats with some "magic" identifier, which can be
# recognized safely, should be added at the end of this list.

package ifneeded Img 1.4.14 {
    package require img::window
    package require img::tga
    package require img::ico
    package require img::pcx
    package require img::sgi
    package require img::sun
    package require img::xbm
    package require img::xpm
    package require img::ps
    package require img::jpeg
    package require img::png
    package require img::tiff
    package require img::bmp
    package require img::ppm
    package require img::gif
    package require img::pixmap
    package provide Img 1.4.14
}

if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::bmp 1.4.14 [list load [file join $dir tcl9tkimgbmp1414.dll]]
} else {
    package ifneeded img::bmp 1.4.14 [list load [file join $dir tkimgbmp1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::gif 1.4.14 [list load [file join $dir tcl9tkimggif1414.dll]]
} else {
    package ifneeded img::gif 1.4.14 [list load [file join $dir tkimggif1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::ico 1.4.14 [list load [file join $dir tcl9tkimgico1414.dll]]
} else {
    package ifneeded img::ico 1.4.14 [list load [file join $dir tkimgico1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::jpeg 1.4.14 [list load [file join $dir tcl9tkimgjpeg1414.dll]]
} else {
    package ifneeded img::jpeg 1.4.14 [list load [file join $dir tkimgjpeg1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::pcx 1.4.14 [list load [file join $dir tcl9tkimgpcx1414.dll]]
} else {
    package ifneeded img::pcx 1.4.14 [list load [file join $dir tkimgpcx1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::pixmap 1.4.14 [list load [file join $dir tcl9tkimgpixmap1414.dll]]
} else {
    package ifneeded img::pixmap 1.4.14 [list load [file join $dir tkimgpixmap1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::png 1.4.14 [list load [file join $dir tcl9tkimgpng1414.dll]]
} else {
    package ifneeded img::png 1.4.14 [list load [file join $dir tkimgpng1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::ppm 1.4.14 [list load [file join $dir tcl9tkimgppm1414.dll]]
} else {
    package ifneeded img::ppm 1.4.14 [list load [file join $dir tkimgppm1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::ps 1.4.14 [list load [file join $dir tcl9tkimgps1414.dll]]
} else {
    package ifneeded img::ps 1.4.14 [list load [file join $dir tkimgps1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::sgi 1.4.14 [list load [file join $dir tcl9tkimgsgi1414.dll]]
} else {
    package ifneeded img::sgi 1.4.14 [list load [file join $dir tkimgsgi1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::sun 1.4.14 [list load [file join $dir tcl9tkimgsun1414.dll]]
} else {
    package ifneeded img::sun 1.4.14 [list load [file join $dir tkimgsun1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::tga 1.4.14 [list load [file join $dir tcl9tkimgtga1414.dll]]
} else {
    package ifneeded img::tga 1.4.14 [list load [file join $dir tkimgtga1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::tiff 1.4.14 [list load [file join $dir tcl9tkimgtiff1414.dll]]
} else {
    package ifneeded img::tiff 1.4.14 [list load [file join $dir tkimgtiff1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::window 1.4.14 [list load [file join $dir tcl9tkimgwindow1414.dll]]
} else {
    package ifneeded img::window 1.4.14 [list load [file join $dir tkimgwindow1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::xbm 1.4.14 [list load [file join $dir tcl9tkimgxbm1414.dll]]
} else {
    package ifneeded img::xbm 1.4.14 [list load [file join $dir tkimgxbm1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::xpm 1.4.14 [list load [file join $dir tcl9tkimgxpm1414.dll]]
} else {
    package ifneeded img::xpm 1.4.14 [list load [file join $dir tkimgxpm1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::dted 1.4.14 [list load [file join $dir tcl9tkimgdted1414.dll]]
} else {
    package ifneeded img::dted 1.4.14 [list load [file join $dir tkimgdted1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::raw 1.4.14 [list load [file join $dir tcl9tkimgraw1414.dll]]
} else {
    package ifneeded img::raw 1.4.14 [list load [file join $dir tkimgraw1414.dll]]
}
if {[package vsatisfies [package provide Tcl] 9.0-]} {
    package ifneeded img::flir 1.4.14 [list load [file join $dir tcl9tkimgflir1414.dll]]
} else {
    package ifneeded img::flir 1.4.14 [list load [file join $dir tkimgflir1414.dll]]
}
