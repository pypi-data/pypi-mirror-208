 #
 # parse SVG-Path "d" sequence
 #
 # Usage:
 # SVGpath::init "M10-5,1e-1-2 q7-3.1 4 2zl1,2,3,4,5,6Z"
 # SVGpath::getCmdArgs
 #  -->  M {10 -5 0.01 2}
 #    ...
 #   .. repeat SVGpath::getCmdAndArgs until it return {} (or raise an error)
 
 
namespace eval SVGpath {
    variable G ; # array holding the all the 'globals' of the current module
    
     #--------------------------------------
     # constants
     #--------------------------------------
    set G(RE_FLOAT) {
        \A
        [-+]? (?: [0-9]* \.? [0-9]+ | [0-9]+ \.? ) (?:[eE][-+]?[0-9]+)?
    }
    set G(FLOAT_INIT_SYMBOLS) "+-0123456789.eE"

    set G(RE_WHITES) {
        \A
        [[:space:]]*
    }
    set G(RE_WHITES_OR_COMMA) {
        \A
        [[:space:]]* ,? [[:space:]]*
    }
    
    set G(PATHDATA_CMDS) "mMlLqQcChHvVsStTaAzZ"

     #--------------------------------------
     #  scanner ststus
     #--------------------------------------
    set G(STR) {}  ;# string to scan
    set G(CH)  {}  ;# current character  (EndOfString is "")
    set G(IDX) 0   ;# current scan index

    proc init {str} {
        variable G        
        set G(STR) $str
        set G(IDX) 0
        set G(CH) [string index $str 0]
    }

      # advance the scan cursor of n chars
      # on EndOfString CH is {}
    proc _NEXT { {n 1} } {
        variable G        
        set G(CH) [string index $G(STR) [incr G(IDX) $n]]        
    }

    proc _Scan {regexp} {
        variable G
        set strings [regexp -inline -start $G(IDX)  -expanded $regexp  $G(STR)]
        set str [lindex $strings 0]
        set nc [string length $str]
        if { $nc > 0 } { _NEXT $nc }
        return $str
    }


     # returns 1 (true) if ch is in validChars , else 0 (false)
     #  (( just an syntactic sugar around [string first ..] ))
    proc _CharMatch { ch validChars } {
        expr {[string first $ch $validChars] >= 0}
    }

    proc _SkipWhites {} {
        variable G
        _Scan $G(RE_WHITES)
        return
    }


    proc _SkipWhitesOrComma {} {
        variable G
        _Scan $G(RE_WHITES_OR_COMMA)
        return
    }

     # return the scanned floating-point number
     # or raise an error
     # ASSERT:  [_CharMatch $G(CH) $G(FLOAT_INIT_SYMBOLS)]
    proc _GetFloat {} {
        variable G
        set numStr [_Scan $G(RE_FLOAT)]
        if { $numStr eq "" } {
            error "expected a number at pos $G(IDX)"
        } 
        return [expr {$numStr+0.0}] ; #convert to number
    }

     # return the scanned number-pair
     # or raise an error
     # ASSERT:  [_CharMatch $G(CH) $G(FLOAT_INIT_SYMBOLS)]
    proc _GetFloatPair {} {
        set n1 [_GetFloat]
        _SkipWhitesOrComma
        set n2 [_GetFloat]  ;# raise an errorif not found ...
        ##   if { $n2 == {} }    
        return [list $n1 $n2]
    }

    proc _GetSequenceOfFloats {} {
        variable G
        set L {}
        _SkipWhites
        while { [_CharMatch $G(CH) $G(FLOAT_INIT_SYMBOLS)] } {
            lappend L [_GetFloat]
            _SkipWhitesOrComma        
        }
        return $L
    }

     # raise an error if the number of parameters in $argList
     #  is not valid for command $cmd
    proc _CheckCmdArgs {pos cmd argList} {
        incr pos -1 ;  global position of the last scanned char
         # no diff between uppercase and lowercase commands
        set cmd [string toupper $cmd]
         # command is just 1 char
        set n [llength $argList]
        if { [_CharMatch $cmd "MLT"] } {
             # requires k pairs (i.e. 2*k numbers)
            if { $n==0 || $n % 2 != 0 } {
                error "command \"$cmd\" ending at position $pos requires k pairs of numbers"
            }
        } elseif { [_CharMatch $cmd "QS"] } {
             # requires 2*k pairs (i.e. 2*2*k numbers)
            if { $n==0 || $n % 4 != 0 } {
                error "command \"$cmd\" ending at position $Gpos requires 2*k pairs of numbers"
            }            
        } elseif { [_CharMatch $cmd "C"] } {
             # requires 3*k pairs (i.e. 2*3*k numbers)
            if { $n==0 || $n % 6 != 0 } {
                error "command \"$cmd\" ending at position $pos requires 3*k pairs of numbers"
            }            
        } elseif { [_CharMatch $cmd "HV"] } {
             # requires k>0 numbers
            if { $n==0 } {
                error "command \"$cmd\" ending at position $pos requires at least one number"
            }            
        } elseif { [_CharMatch $cmd "A"] } {
             # requires k>0 numbers
            if { $n==0 } {
                error "command \"$cmd\" ending at position $pos requires at least one number"
            }            
        } elseif { [_CharMatch $cmd "Z"] } {
             # requires 0 numbers
            if { $n>0 } {
                error "command \"$cmd\" ending at position $pos requires no parameters"
            }            
        } else {
                error "unknown command \"$cmd\" ending at position $pos"        
        }
        return
    }

     # return a two element list:
     #  1st elem is the cmd  (e.g. "M" ,"m", "Q" ..)
     #  2nd elem is a list with all the numeric ...  parameters
     # may raise errors
     #   .. invalid token or wrong number of parameters (depending on cmd)
     #  on EndOfString return {}      
    proc getCmdAndArgs {} {
        variable G

        _SkipWhites
        if { $G(CH) == "" } return [list ] ;# end of string found, return empty list
                
        if { ! [_CharMatch $G(CH) $G(PATHDATA_CMDS)] } {
            error "expected a Path-Data command at pos $G(IDX), found \"$G(CH)\""            
        }
        set cmd $G(CH)  ;  _NEXT
        set L [_GetSequenceOfFloats]
        _CheckCmdArgs $G(IDX) $cmd $L  ;# may raise an error
        return [list $cmd $L]
    }

}
