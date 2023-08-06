#
# Tcl package index file
#

package ifneeded perlin 1.0 [string map [list @ $dir] {

    switch -- $::tcl_platform(platform) {
        windows {
                switch -- $::tcl_platform(pointerSize) {
                    4 { set libfile win-x32/perlin.dll }
                    8 { set libfile win-x64/perlin.dll }
                    default { error "Unexpected word-size !!! "}
                }
        }                        
        unix {
            switch -- $::tcl_platform(os) {
            Linux {
                switch -- $::tcl_platform(pointerSize) {
                    4 { set libfile linux-x32/perlin.so }
                    8 { set libfile linux-x64/perlin.so }
                    default { error "Unexpected word-size !!! "}
                }                        
            }
            Darwin {
                set libfile darwin-x64/perlin.dylib
            }
            default { error "perlin:: unsupported platform" }
            }
        }
        default { error "perlin:: unsupported platform" }
    }
    load [file join {@} $libfile]
    package provide perlin 1.0
}]

