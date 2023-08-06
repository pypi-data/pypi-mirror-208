package ifneeded Mtx 1.0 [list source [file join $dir Mtx.tcl]]
package ifneeded HSB 1.0 [list source [file join $dir HSB.tcl]]

package ifneeded BL::SVG 1.0 [list apply { dir {
    source [file join $dir t2dsvg.tcl]
    package provide BL::SVG 1.0
}} $dir] ;# end of lambda apply

package ifneeded BL::Filter 1.0 [list apply { dir {
    source [file join $dir t2d_filters.tcl]
    package provide BL::Filter 1.0
}} $dir] ;# end of lambda apply

package ifneeded tkBlend2d 1.0 [list apply { dir  {
	source [file join $dir t2d.tcl]
    load [BL::_findDLL $dir "tkBlend2d"] T2d
    package provide tkBlend2d 1.0
}} $dir] ;# end of lambda apply

package ifneeded tclBlend2d 1.0 [list apply { dir  {
	source [file join $dir t2d.tcl]
    load [BL::_findDLL $dir "tclBlend2d"] T2d
    package provide tclBlend2d 1.0
}} $dir] ;# end of lambda apply
    
# --- Alias
package ifneeded Blend2d 1.0 [list apply { dir  {
    package require -exact tkBlend2d 1.0
    package provide Blend2d 1.0
}} $dir] ;# end of lambda apply
