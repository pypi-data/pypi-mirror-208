from tkfly.core import fly_root
from tkinter import Toplevel, Widget


def load_samdi():
    fly_root().eval("""
set rcsId {$Id: stooop.tcl,v 1.1.1.1 1998/06/28 20:57:55 tregar Exp $}

package provide stooop 3.5

catch {rename proc _proc}            ;# rename proc before it is overloaded, ignore error in case of multiple inclusion of this file

namespace eval ::stooop {
    variable checkCode
    variable traceProcedureChannel
    variable traceProcedureFormat
    variable traceDataChannel
    variable traceDataFormat
    variable traceDataOperations

    set checkCode {}                                ;# no checking by default: use an empty instruction to avoid any performance hit
    if {[info exists ::env(STOOOPCHECKALL)]} {
        array set ::env {STOOOPCHECKPROCEDURES {} STOOOPCHECKDATA {}}
    }
    if {[info exists ::env(STOOOPCHECKPROCEDURES)]} {
        append checkCode {::stooop::checkProcedure;}
    }
    if {[info exists ::env(STOOOPTRACEALL)]} {                                                   ;# use same channel for both traces
        set ::env(STOOOPTRACEPROCEDURES) $::env(STOOOPTRACEALL)
        set ::env(STOOOPTRACEDATA) $::env(STOOOPTRACEALL)
    }
    if {[info exists ::env(STOOOPTRACEPROCEDURES)]} {
        set traceProcedureChannel $::env(STOOOPTRACEPROCEDURES)
        if {![regexp {^stdout|stderr$} $traceProcedureChannel]} {
            set traceProcedureChannel [open $::env(STOOOPTRACEPROCEDURES) w+]        ;# eventually truncate output file if it exists
        }
        set traceProcedureFormat {class: %C, procedure: %p, object: %O, arguments: %a}                             ;# default format
        catch {set traceProcedureFormat $::env(STOOOPTRACEPROCEDURESFORMAT)}         ;# eventually override with user defined format
        append checkCode {::stooop::traceProcedure;}
    }
    if {[info exists ::env(STOOOPTRACEDATA)]} {
        set traceDataChannel $::env(STOOOPTRACEDATA)
        if {![regexp {^stdout|stderr$} $traceDataChannel]} {
            set traceDataChannel [open $::env(STOOOPTRACEDATA) w+]                   ;# eventually truncate output file if it exists
        }
        # default format
        set traceDataFormat {class: %C, procedure: %p, array: %A, object: %O, member: %m, operation: %o, value: %v}
        catch {set traceDataFormat $::env(STOOOPTRACEDATAFORMAT)}                    ;# eventually override with user defined format
        set traceDataOperations rwu                                                               ;# trace all operations by default
        catch {set traceDataOperations $::env(STOOOPTRACEDATAOPERATIONS)}        ;# eventually override with user defined operations
    }

    namespace export class virtual new delete classof                                                      ;# export public commands

    if {![info exists newId]} {
        variable newId 0                        ;# initialize object id counter only once even if this file is sourced several times
    }

    _proc new {classOrId args} {                                   ;# create an object of specified class or copy an existing object
        variable newId
        variable fullClass

        # use local variable for identifier because new can be invoked recursively
        if {[scan $classOrId %u dummy]==0} {                                                            ;# first argument is a class
            set constructor ${classOrId}::[namespace tail $classOrId]                                   ;# generate constructor name
            # generate fully qualified class namespace name
            set fullName [namespace qualifiers [uplevel namespace which -command $constructor]]
            # we could detect here whether class was ever declared but that would prevent stooop packages to load properly, because
            # constructor would not be invoked and thus class source file never sourced
            set fullClass([set id [incr newId]]) $fullName
            # invoke the constructor for the class with optional arguments in caller's variable context so that object creation is
            # transparent and that array names as constructor parameters work with a simple upvar
            uplevel $constructor $id $args
        } else {  ;# first argument is an object identifier (unsigned integer) , copy source object to new object of identical class
            if {[catch {set fullClass([set id [incr newId]]) $fullClass($classOrId)}]} {
                error "invalid object identifier $classOrId"
            }
            # invoke the copy constructor for the class in caller's variable context so that object copy is transparent (see above)
            uplevel $fullClass($classOrId)::_copy $id $classOrId
        }
        return $id                                                                              ;# return a unique object identifier
    }

    _proc delete {args} {                                                                              ;# delete one or more objects
        variable fullClass

        foreach id $args {                           ;# destruct in caller's variable context so that object deletion is transparent
            uplevel ::stooop::deleteObject $fullClass($id) $id
            unset fullClass($id)
        }
    }

    # delete object data starting at specified class layer and going up the base class hierarchy if any
    # invoke the destructor for the object class and unset all the object data members for the class
    # the destructor will in turn delete the base classes layers
    _proc deleteObject {fullClass id} {
        # invoke the destructor for the class in caller's variable context so that object deletion is transparent
        uplevel ${fullClass}::~[namespace tail $fullClass] $id
        # delete all this object data members if any (assume that they were stored as ${class}::($id,memberName))
        foreach name [array names ${fullClass}:: $id,*] {
            unset ${fullClass}::($name)
        }
        # data member arrays deletion is left to the user
    }

    _proc classof {id} {
        variable fullClass

        return $fullClass($id)                                                                             ;# return class of object
    }

    _proc copy {fullClass from to} {                                          ;# copy object data members from one object to another
        set index [string length $from]
        foreach name [array names ${fullClass}:: $from,*] {                                             ;# copy regular data members
            set ${fullClass}::($to[string range $name $index end]) [set ${fullClass}::($name)]
        }
        # if any, array data members copy is left to the class programmer through the then mandatory copy constructor
    }
}

_proc ::stooop::class {args} {
    variable declared

    set class [lindex $args 0]
    set declared([uplevel namespace eval $class {namespace current}]) {}            ;# register class using its fully qualified name
    # create the empty name array used to hold all class objects so that static members can be directly initialized within the class
    # declaration but outside member procedures
    uplevel namespace eval $class [list "::variable {}\n[lindex $args end]"]
}

# if procedure is a member of a known class, class and procedure names are set and true is returned, otherwise false is returned
_proc ::stooop::parseProcedureName {namespace name fullClassVariable procedureVariable messageVariable} {
    # namespace argument is the current namespace (fully qualified) in which the procedure is defined
    variable declared
    upvar $fullClassVariable fullClass $procedureVariable procedure $messageVariable message

    if {[info exists declared($namespace)]&&([string length [namespace qualifiers $name]]==0)} {
        # a member procedure is being defined inside a class namespace
        set fullClass $namespace
        set procedure $name                                                                    ;# member procedure name is full name
        return 1
    } else {                                                 ;# procedure is either a member of a known class or a regular procedure
        if {![string match ::* $name]} {                                                  ;# eventually fully qualify procedure name
            if {[string compare $namespace ::]==0} {                                                ;# global namespace special case
                set name ::$name
            } else {
                set name ${namespace}::$name
            }
        }
        set fullClass [namespace qualifiers $name]                                            ;# eventual class name is leading part
        if {[info exists declared($fullClass)]} {                                                               ;# if class is known
            set procedure [namespace tail $name]                                                     ;# procedure always is the tail
            return 1
        } else {                                                                                           ;# not a member procedure
            if {[string length $fullClass]==0} {
                set message "procedure $name class name is empty"
            } else {
                set message "procedure $name class $fullClass is unknown"
            }
            return 0
        }
    }
}

# virtual operator, to be placed before proc
# virtualize a member procedure, determine whether it is a pure virtual, check for procedures that cannot be virtualized
_proc ::stooop::virtual {keyword name arguments args} {
    variable pureVirtual     ;# set a flag so that proc knows it is acting upon a virtual procedure, also serves as a pure indicator

    if {[string compare [uplevel namespace which -command $keyword] ::proc]!=0} {
        error "virtual operator works only on proc, not $keyword"
    }
    if {![parseProcedureName [uplevel namespace current] $name fullClass procedure message]} {
        error $message                                                                       ;# not in a member procedure definition
    }
    set class [namespace tail $fullClass]
    if {[string compare $class $procedure]==0} {
        error "cannot make class $fullClass constructor virtual"
    }
    if {[string compare ~$class $procedure]==0} {
        error "cannot make class $fullClass destructor virtual"
    }
    if {[string compare [lindex $arguments 0] this]!=0} {
        error "cannot make static procedure $procedure of class $fullClass virtual"
    }
    set pureVirtual [expr {[llength $args]==0}]                                              ;# no procedure body means pure virtual
    # process procedure declaration, body being empty for pure virtual procedure
    uplevel ::proc [list $name $arguments [lindex $args 0]]                             ;# make virtual transparent by using uplevel
    unset pureVirtual
}

_proc proc {name arguments args} {
    if {![::stooop::parseProcedureName [uplevel namespace current] $name fullClass procedure message]} {
        # not in a member procedure definition, fall back to normal procedure declaration
        # uplevel is required instead of eval here otherwise tcl seems to forget the procedure namespace if it exists
        uplevel _proc [list $name $arguments] $args
        return
    }
    if {[llength $args]==0} {                                                                   ;# check for procedure body presence
        error "missing body for ${fullClass}::$procedure"
    }
    set class [namespace tail $fullClass]
    if {[string compare $class $procedure]==0} {                                                     ;# class constructor definition
        if {[string compare [lindex $arguments 0] this]!=0} {
            error "class $fullClass constructor first argument must be this"
        }
        if {[string compare [lindex $arguments 1] copy]==0} {                            ;# user defined copy constructor definition
            if {[llength $arguments]!=2} {
                error "class $fullClass copy constructor must have 2 arguments exactly"
            }
            if {[catch {info body ::${fullClass}::$class}]} {                               ;# make sure of proper declaration order
                error "class $fullClass copy constructor defined before constructor"
            }
            eval ::stooop::constructorDeclaration $fullClass $class 1 \{$arguments\} $args
        } else {                                                                                                 ;# main constructor
            eval ::stooop::constructorDeclaration $fullClass $class 0 \{$arguments\} $args
            ::stooop::generateDefaultCopyConstructor $fullClass                          ;# always generate default copy constructor
        }
    } elseif {[string compare ~$class $procedure]==0} {                                              ;# class destructor declaration
        if {[llength $arguments]!=1} {
            error "class $fullClass destructor must have 1 argument exactly"
        }
        if {[string compare [lindex $arguments 0] this]!=0} {
            error "class $fullClass destructor argument must be this"
        }
        if {[catch {info body ::${fullClass}::$class}]} {                      ;# use fastest method for testing procedure existence
            error "class $fullClass destructor defined before constructor"                  ;# make sure of proper declaration order
        }
        ::stooop::destructorDeclaration $fullClass $class $arguments [lindex $args 0]
    } else {                                           ;# regular member procedure, may be static if there is no this first argument
        if {[catch {info body ::${fullClass}::$class}]} {                                   ;# make sure of proper declaration order
            error "class $fullClass member procedure $procedure defined before constructor"
        }
        ::stooop::memberProcedureDeclaration $fullClass $class $procedure $arguments [lindex $args 0]
    }
}

_proc ::stooop::constructorDeclaration {fullClass class copy arguments args} { ;# copy flag is set for user defined copy constructor
    variable checkCode
    variable fullBases
    variable variable

    set number [llength $args]
    if {($number%2)==0} {                                                    ;# check that each base class constructor has arguments
        error "bad class $fullClass constructor declaration, a base class, contructor arguments or body may be missing"
    }
    if {[string compare [lindex $arguments end] args]==0} {
        set variable($fullClass) {}                    ;# remember that there is a variable number of arguments in class constructor
    }
    if {!$copy} {
        # do not initialize (or reinitialize in case of multiple class file source statements) base classes for copy constructor
        set fullBases($fullClass) {}
    }
    foreach {base baseArguments} [lrange $args 0 [expr {$number-2}]] {         ;# check base classes and their constructor arguments
        # fully qualify base class namespace by looking up constructor, which must exist
        set constructor ${base}::[namespace tail $base]
        # in case base class is defined in a file that is part of a package, make sure that file is sourced through the tcl
        # package auto-loading mechanism by directly invoking the base class constructor while ignoring the resulting error
        catch {$constructor}
        # determine fully qualified base class name in user invocation level (up 2 levels from here since this procedure is invoked
        # exclusively by proc)
        set fullBase [namespace qualifiers [uplevel 2 namespace which -command $constructor]]
        if {[string length $fullBase]==0} {                                                       ;# base constructor is not defined
            if {[string match *$base $fullClass]} {
                # if the specified base class name is included last in the fully qualified class name, assume that it was meant to
                # be the same
                error "class $fullClass cannot be derived from itself"
            } else {
                error "class $fullClass constructor defined before base class $base constructor"
            }
        }
        if {!$copy} {                                     ;# check and save base classes only for main constructor that defines them
            if {[lsearch -exact $fullBases($fullClass) $fullBase]>=0} {
                error "class $fullClass directly inherits from class $fullBase more than once"
            }
            lappend fullBases($fullClass) $fullBase
        }
        # remove new lines in base arguments part in case user has formatted long declarations with new lines
        regsub -all \n $baseArguments {} constructorArguments($fullBase)
    }
    # setup access to class data (an empty named array)
    # fully qualify tcl variable command for it may have been redefined within the class namespace
    # since constructor is directly invoked by new, the object identifier must be valid, so debugging the procedure is pointless
    set constructorBody \
"::variable {}
$checkCode
"
    if {[llength $fullBases($fullClass)]>0} {                                                 ;# base class(es) derivation specified
        # invoke base class constructors before evaluating constructor body
        # then set base part hidden derived member so that virtual procedures are invoked at base class level as in C++
        if {[info exists variable($fullClass)]} {                       ;# variable number of arguments in derived class constructor
            foreach fullBase $fullBases($fullClass) {
                if {![info exists constructorArguments($fullBase)]} {
                    error "missing base class $fullBase constructor arguments from class $fullClass constructor"
                }
                set baseConstructor ${fullBase}::[namespace tail $fullBase]
                if {[info exists variable($fullBase)]&&([string first {$args} $constructorArguments($fullBase)]>=0)} {
                    # variable number of arguments in base class constructor and in derived class base class constructor arguments
                    # use eval so that base class constructor sees arguments instead of a list
                    # only the last argument of the base class constructor arguments is considered as a variable list
                    # (it usually is $args but could be a procedure invocation, such as [filter $args])
                    # fully qualify tcl commands such as set, for they may have been redefined within the class namespace
                    append constructorBody \
"::set _list \[::list $constructorArguments($fullBase)\]
::eval $baseConstructor \$this \[::lrange \$_list 0 \[::expr {\[::llength \$_list\]-2}\]\] \[::lindex \$_list end\]
::unset _list
::set ${fullBase}::(\$this,_derived) $fullClass
"
                } else {
                    # no special processing needed
                    # variable number of arguments in base class constructor or
                    # variable arguments list passed as is to base class constructor
                    append constructorBody \
"$baseConstructor \$this $constructorArguments($fullBase)
::set ${fullBase}::(\$this,_derived) $fullClass
"
                }
            }
        } else {                                                                                     ;# constant number of arguments
            foreach fullBase $fullBases($fullClass) {
                if {![info exists constructorArguments($fullBase)]} {
                    error "missing base class $fullBase constructor arguments from class $fullClass constructor"
                }
                set baseConstructor ${fullBase}::[namespace tail $fullBase]
                append constructorBody \
"$baseConstructor \$this $constructorArguments($fullBase)
::set ${fullBase}::(\$this,_derived) $fullClass
"
            }
        }
    }                                                                                     ;# else no base class derivation specified
    if {$copy} {                                        ;# for user defined copy constructor, copy derived class member if it exists
        append constructorBody \
"::catch {::set ${fullClass}::(\$this,_derived) \[::set ${fullClass}::(\$[::lindex $arguments 1],_derived)\]}
"
    }
    append constructorBody [lindex $args end]                                          ;# finally append user defined procedure body
    if {$copy} {
        _proc ${fullClass}::_copy $arguments $constructorBody
    } else {
        _proc ${fullClass}::$class $arguments $constructorBody
    }
}

_proc ::stooop::destructorDeclaration {fullClass class arguments body} {
    variable checkCode
    variable fullBases

    # setup access to class data
    # since the object identifier is always valid at this point, debugging the procedure is pointless
    set body \
"::variable {}
$checkCode
$body
"
    # if there are any, delete base classes parts in reverse order of construction
    for {set index [expr {[llength $fullBases($fullClass)]-1}]} {$index>=0} {incr index -1} {
        set fullBase [lindex $fullBases($fullClass) $index]
        append body \
"::stooop::deleteObject $fullBase \$this
"
    }
    _proc ${fullClass}::~$class $arguments $body
}

_proc ::stooop::memberProcedureDeclaration {fullClass class procedure arguments body} {
    variable checkCode
    variable pureVirtual

    if {[info exists pureVirtual]} {                                                                          ;# virtual declaration
        if {$pureVirtual} {                                                                              ;# pure virtual declaration
            # setup access to class data
            # evaluate derived procedure which must exists. derived procedure return value is automatically returned
            _proc ${fullClass}::$procedure $arguments \
"::variable {}
$checkCode
::eval \$${fullClass}::(\$this,_derived)::$procedure \[::lrange \[::info level 0\] 1 end\]
"
        } else {                                                                                      ;# regular virtual declaration
            # setup access to class data
            # evaluate derived procedure and return if it exists
            # else evaluate the base class procedure which can be invoked from derived class procedure by prepending _
            _proc ${fullClass}::_$procedure $arguments \
"::variable {}
$checkCode
$body
"
            _proc ${fullClass}::$procedure $arguments \
"::variable {}
$checkCode
if {!\[::catch {::info body \$${fullClass}::(\$this,_derived)::$procedure}\]} {
::return \[::eval \$${fullClass}::(\$this,_derived)::$procedure \[::lrange \[::info level 0\] 1 end\]\]
}
::eval ${fullClass}::_$procedure \[::lrange \[::info level 0\] 1 end\]
"
        }
    } else {                                                                                              ;# non virtual declaration
        # setup access to class data
        _proc ${fullClass}::$procedure $arguments \
"::variable {}
$checkCode
$body
"
    }
}

# generate default copy procedure which may be overriden by the user for any class layer
_proc ::stooop::generateDefaultCopyConstructor {fullClass} {
    variable fullBases

    foreach fullBase $fullBases($fullClass) {   ;# generate code for cloning base classes layers if there is at least one base class
        append body \
"${fullBase}::_copy \$this \$sibling
"
    }
    append body \
"::stooop::copy $fullClass \$sibling \$this
"
    _proc ${fullClass}::_copy {this sibling} $body
}


if {[llength [array names ::env STOOOP*]]>0} {             ;# if one or more environment variables are set, we are in debugging mode

    catch {rename ::stooop::class ::stooop::_class}                              ;# gracefully handle multiple sourcing of this file
    _proc ::stooop::class {args} {                     ;# use a new class procedure instead of adding debugging code to existing one
        variable traceDataOperations

        set class [lindex $args 0]
        if {[info exists ::env(STOOOPCHECKDATA)]} {      ;# check write and unset operations on empty named array holding class data
            uplevel namespace eval $class [list {::trace variable {} wu ::stooop::checkData}]
        }
        if {[info exists ::env(STOOOPTRACEDATA)]} {      ;# trace write and unset operations on empty named array holding class data
            uplevel namespace eval $class [list "::trace variable {} $traceDataOperations ::stooop::traceData"]
        }
        uplevel ::stooop::_class $args
    }

    if {[info exists ::env(STOOOPCHECKPROCEDURES)]} {                ;# prevent the creation of any object of a pure interface class
        # use a new virtual procedure instead of adding debugging code to existing one
        catch {rename ::stooop::virtual ::stooop::_virtual}                      ;# gracefully handle multiple sourcing of this file
        _proc ::stooop::virtual {keyword name arguments args} {
            variable interface                     ;# keep track of interface classes (which have at least 1 pure virtual procedure)

            uplevel ::stooop::_virtual [list $keyword $name $arguments] $args
            parseProcedureName [uplevel namespace current] $name fullClass procedure message
            if {[llength $args]==0} {                                                        ;# no procedure body means pure virtual
                set interface($fullClass) {}
            }
        }

        catch {rename ::stooop::new ::stooop::_new}                              ;# gracefully handle multiple sourcing of this file
        _proc ::stooop::new {classOrId args} {           ;# use a new new procedure instead of adding debugging code to existing one
            variable fullClass
            variable interface

            if {[scan $classOrId %u dummy]==0} {                                                        ;# first argument is a class
                set constructor ${classOrId}::[namespace tail $classOrId]                               ;# generate constructor name
                set fullName [namespace qualifiers [uplevel namespace which -command $constructor]]
            } else {                                                                       ;# first argument is an object identifier
                set fullName $fullClass($classOrId)
            }
            if {[info exists interface($fullName)]} {
                error "class $fullName with pure virtual procedures should not be instanciated"
            }
            return [uplevel ::stooop::_new $classOrId $args]
        }
    }

    _proc ::stooop::ancestors {fullClass} {                              ;# return the unsorted list of ancestors in class hierarchy
        variable ancestors                                                                             ;# use a cache for efficiency
        variable fullBases

        if {[info exists ancestors($fullClass)]} {
            return $ancestors($fullClass)                                                                      ;# found in the cache
        }
        set list {}
        foreach class $fullBases($fullClass) {
            set list [concat $list [list $class] [ancestors $class]]
        }
        set ancestors($fullClass) $list                                                                             ;# save in cache
        return $list
    }

    # since this procedure is always invoked from a debug procedure, take the extra level in the stack frame into account
    # parameters (passed as references) that cannot be determined are not set
    _proc ::stooop::debugInformation {className fullClassName procedureName fullProcedureName thisParameterName} {
        upvar $className class $fullClassName fullClass $procedureName procedure $fullProcedureName fullProcedure\
            $thisParameterName thisParameter
        variable declared

        set namespace [uplevel 2 namespace current]
        if {[lsearch -exact [array names declared] $namespace]<0} return                                 ;# not in a class namespace
        set fullClass [string trimleft $namespace :]                                            ;# remove redundant global qualifier
        set class [namespace tail $fullClass]                                                                          ;# class name
        set list [info level -2]
        if {[llength $list]==0} return                                                     ;# not in a procedure, nothing else to do
        set procedure [lindex $list 0]
        set fullProcedure [uplevel 3 namespace which -command $procedure]            ;# procedure must be known at the invoker level
        set procedure [namespace tail $procedure]                                                            ;# strip procedure name
        if {[string compare $class $procedure]==0} {                                                                  ;# constructor
            set procedure constructor
        } elseif {[string compare ~$class $procedure]==0} {                                                            ;# destructor
            set procedure destructor
        }
        if {[string compare [lindex [info args $fullProcedure] 0] this]==0} {                                ;# non static procedure
            set thisParameter [lindex $list 1]                                                ;# object identifier is first argument
        }
    }

    _proc ::stooop::checkProcedure {} {                       ;# check that member procedure is valid for object passed as parameter
        variable fullClass

        debugInformation class qualifiedClass procedure qualifiedProcedure this
        if {![info exists this]} return                                                    ;# static procedure, no checking possible
        if {![info exists fullClass($this)]} {
            error "$this is not a valid object identifier"
        }
        set fullName [string trimleft $fullClass($this) :]
        if {[string compare $fullName $qualifiedClass]==0} return                              ;# procedure and object classes match
        # restore global qualifiers to compare with internal full class array data
        if {[lsearch -exact [ancestors ::$fullName] ::$qualifiedClass]<0} {
            error "class $qualifiedClass of $qualifiedProcedure procedure not an ancestor of object $this class $fullName"
        }
    }

    _proc ::stooop::traceProcedure {} {          ;# gather current procedure data, perform substitutions and output to trace channel
        variable traceProcedureChannel
        variable traceProcedureFormat

        debugInformation class qualifiedClass procedure qualifiedProcedure this
        # all debug data is available since we are for sure in a class procedure
        set text $traceProcedureFormat
        regsub -all %C $text $qualifiedClass text                                                      ;# fully qualified class name
        regsub -all %c $text $class text
        regsub -all %P $text $qualifiedProcedure text                                              ;# fully qualified procedure name
        regsub -all %p $text $procedure text
        if {[info exists this]} {                                                                            ;# non static procedure
            regsub -all %O $text $this text
            regsub -all %a $text [lrange [info level -1] 2 end] text                                          ;# remaining arguments
        } else {                                                                                                 ;# static procedure
            regsub -all %O $text {} text
            regsub -all %a $text [lrange [info level -1] 1 end] text                                          ;# remaining arguments
        }
        puts $traceProcedureChannel $text
    }

    # check that class data member is accessed within procedure of identical class
    # then if procedure is not static, check that only data belonging to the object passed as parameter is accessed
    _proc ::stooop::checkData {array name operation} {
        scan $name %u,%s identifier member
        if {[info exists member]&&([string compare $member _derived]==0)} return                ;# ignore internally defined members

        debugInformation class qualifiedClass procedure qualifiedProcedure this
        if {![info exists class]} return                                     ;# no checking can be done outside of a class namespace
        set array [uplevel [list namespace which -variable $array]]                                     ;# determine array full name
        if {![info exists procedure]} {                                                                  ;# inside a class namespace
            if {[string compare $array ::${qualifiedClass}::]!=0} {           ;# compare with empty named array fully qualified name
                # trace command error message is automatically prepended and indicates operation
                error "class access violation in class $qualifiedClass namespace"
            }
            return                                                                                                           ;# done
        }
        if {[string compare $qualifiedProcedure ::stooop::copy]==0} return                         ;# ignore internal copy procedure
        if {[string compare $array ::${qualifiedClass}::]!=0} {               ;# compare with empty named array fully qualified name
            # trace command error message is automatically prepended and indicates operation
            error "class access violation in procedure $qualifiedProcedure"
        }
        if {![info exists this]} return                                             ;# static procedure, all objects can be accessed
        if {![info exists identifier]} return                                                 ;# static data members can be accessed
        if {$this!=$identifier} {                                                 ;# check that accessed data belongs to this object
            error "object $identifier access violation in procedure $qualifiedProcedure acting on object $this"
        }
    }

    # gather accessed data member information, perform substitutions and output to trace channel
    _proc ::stooop::traceData {array name operation} {
        variable traceDataChannel
        variable traceDataFormat

        scan $name %u,%s identifier member
        if {[info exists member]&&([string compare $member _derived]==0)} return                ;# ignore internally defined members

        # ignore internal destruction
        if {![catch {lindex [info level -1] 0} procedure]&&([string compare ::stooop::deleteObject $procedure]==0)} return
        set class {}                                                                               ;# in case we are outside a class
        set qualifiedClass {}
        set procedure {}                                                                 ;# in case we are outside a class procedure
        set qualifiedProcedure {}

        debugInformation class qualifiedClass procedure qualifiedProcedure this
        set text $traceDataFormat
        regsub -all %C $text $qualifiedClass text                                                      ;# fully qualified class name
        regsub -all %c $text $class text
        if {[info exists member]} {
            regsub -all %m $text $member text
        } else {
            regsub -all %m $text $name text                                                                         ;# static member
        }
        regsub -all %P $text $qualifiedProcedure text                                              ;# fully qualified procedure name
        regsub -all %p $text $procedure text
        # fully qualified array name with global qualifiers stripped
        regsub -all %A $text [string trimleft [uplevel [list namespace which -variable $array]] :] text
        if {[info exists this]} {                                                                            ;# non static procedure
            regsub -all %O $text $this text
        } else {                                                                                                 ;# static procedure
            regsub -all %O $text {} text
        }
        array set string {r read w write u unset}
        regsub -all %o $text $string($operation) text
        if {[string compare $operation u]==0} {
            regsub -all %v $text {} text                                                                  ;# no value when unsetting
        } else {
            regsub -all %v $text [uplevel set ${array}($name)] text
        }
        puts $traceDataChannel $text
    }
}
namespace import stooop::*
# saMDI.tcl version 1.0a2
# Copyright (C) 1998  Sam Tregar (sam@tregar.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version. 
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# See README for usage details and contact information

package require stooop 3

# class mdi --
#
#   This class controls the main MDI window
#
# Arguments (can be abreviated uniquely):
#  Required:
#   -title - title to be displayed by the main MDI window
#   -height - height of the MDI window
#   -width - width of the MDI window
#
#  Optional:
#   -foreground and -background - the foreground and background
#       of the main window, inherited by slaves
#       default to white on blue
#   -clicktofocus - 1 is like Windows and Mac, 0 is like some Unix.
#       default is platform specific
#   -toplevel (optional) - an empty toplevel to use, if not specified mdi
#       creates its own.
#   -repositionIconsOnResize (optional) - Should I reshuffle the icons when 
#       the user resizes the mdi main window?  Defaults to 1.  If not icon
#       position can end up off the screen.
#
# Results:
#   Returns the object ID for the MDI window that is used in all future
#   calls to ::mdi functions and variables.
#   displays MDI window
class mdi {
    proc mdi {this args} {
        global tcl_platform

        if ![info exists mdi::(globalInitDone)] {
            mdi::globalInit
        }

        set mdi::($this,usetoplevel) ""
        set mdi::($this,title) ""
        set mdi::($this,height) ""
        set mdi::($this,width) ""
        set mdi::($this,foreground) white
        set mdi::($this,background) blue
        set mdi::($this,repositionIconsOnResize) 1

        if [info exists DEBUG-FORCE-PLATFORM] {
            set mdi::($this,platform) $DEBUG-FORCE-PLATFORM
        } else {
            set mdi::($this,platform) $tcl_platform(os)
        }

        switch -glob -- $mdi::($this,platform) {
            "Win*" {
                set mdi::($this,clicktofocus) 1
            }
            "Mac*" {
                set mdi::($this,clicktofocus) 1
            }
            default {
                # Unix and others
                set mdi::($this,clicktofocus) 0
            }
        }


        foreach {name value} $args {
            switch -glob -- $name {
                "-b*" {set mdi::($this,background) $value}
                "-click*" {set mdi::($this,clicktofocus) $value}
                "-f*" {set mdi::($this,foreground) $value}
                "-h*" {set mdi::($this,height) $value}
                "-r*" {set mdi::($this,repositionIconsOnResize) $value}
                "-ti*" {set mdi::($this,title) $value}
                "-to*" {set mdi::($this,usetoplevel) $value}
                "-w*" {set mdi::($this,width) $value}
                default {bgerror "::mdi class constructor : Unknown option ${name}!"}
            }
        }
        foreach name "title height width" {
            if ![info exists mdi::($this,$name)] {
                bgerror "::mdi class constructor : No value specified for required option ${name}!"
                return 0
            }
        }
        mdi::init $this
    }
    proc ~mdi {this} {
        foreach slave $mdi::($this,slaves) {
            delete $slave
        }
        destroy $mdi::($this,toplevel)
    }
}

# mdi::init --
#
#   Internal function to initialize an mdi instance.
#
# Arguments:
#   this
# Results:
#   mdi is initialized
#
proc mdi::init {this} {
    if ![string length $mdi::($this,usetoplevel)] {
        set mdi::($this,toplevel) [toplevel .mdi$this -background $mdi::($this,background) -height $mdi::($this,height) -width $mdi::($this,width)]
    } else {
        set mdi::($this,toplevel) $mdi::($this,usetoplevel)
        $mdi::($this,usetoplevel) configure -background $mdi::($this,background) -height $mdi::($this,height) -width $mdi::($this,width)
    }
    mdi::hide $this
    wm title $mdi::($this,toplevel) $mdi::($this,title)
    wm geometry $mdi::($this,toplevel) $mdi::($this,width)x$mdi::($this,height)+10+10
    set mdi::($this,core) [canvas $mdi::($this,toplevel).core -background $mdi::($this,background) -height $mdi::($this,height) -width $mdi::($this,width)]
    
    grid $mdi::($this,core) -row 0 -column 0 -sticky nswe
    grid rowconfigure $mdi::($this,toplevel) 0 -weight 1
    grid columnconfigure $mdi::($this,toplevel) 0 -weight 1

    bind $mdi::($this,toplevel) <Configure> "mdi::resizeHandler $this %h %w %W"
    mdi::show $this
}

# mdi::hide --
#
#   internal function - hides an MDI window
#
# Arguments:
#   this
# Results:
#   mdi window is unmapped from the display
#
proc mdi::hide {this} {
    wm withdraw $mdi::($this,toplevel)
}

# mdi::show --
#
#   Internal function - displays mdi window
#
# Arguments:
#   this
# Results:
#   mdi window is displayed on the screen
#
proc mdi::show {this} {
    wm deiconify $mdi::($this,toplevel)
    raise $mdi::($this,toplevel)
    update idletasks
}


# mdi::showSlave --
#
#   Internal function - displays mdiSlave window
#
# Arguments:
#   this
# Results:
#   mdiSlave window is displayed on the screen
#
proc mdi::showSlave {this slave} {
    set mdiSlave::($slave,window) [set mdi::($this,slaveWindow,$slave) [$mdi::($this,core) create window $mdiSlave::($slave,x) $mdiSlave::($slave,y) -window $mdiSlave::($slave,outerFrame) -anchor nw -tags [list slaveWindow mdiSlave$this]]]

    # Hm.  How to make this work...
    #if $mdiSlave::($slave,maximized) {
    #    mdiSlave::maximize $slave
    #}

    update
}

# mdi::resizeHandler --
#
#   Internal proc - Handles <Configure> events in the main window.
#
# Arguments:
#   this height width window
# Results:
#   Repositions icons (not done yet)
#
proc mdi::resizeHandler {this height width window} {
    if [string compare $mdi::($this,toplevel) $window] {
        return
    }
    if {($width == $mdi::($this,width)) && ($height == $mdi::($this,height))} {
        return
    }
    set mdi::($this,width) $width
    set mdi::($this,height) $height
    catch {unset mdi::($this,iconSpots)}
    if {$mdi::($this,repositionIconsOnResize)} {
        foreach slave $mdi::($this,slaves) {
            if {$mdiSlave::($slave,iconized)} {
                foreach {x y} [mdiSlave::findIconSpot $slave] {}
                $mdi::($this,core) coords icon$slave $x $y
                $mdi::($this,core) delete iconText$slave
                $mdi::($this,core) create text [expr $x + 25] [expr $y + 60] -anchor n -fill $mdi::($this,foreground) -text $mdiSlave::($slave,title) -tags iconText$slave -width 80
            }
        }
    }
            
}



# class mdiSlave --
#
#   Slave window class.  Creates a slave window in the mdi slave.
#
# Arguments (can be abreviated uniquely):
#
# Required:
#   -master - return value from [new mdi] of main window
#   -title - title to be displayed in title bar
#   -height - height of the MDI slave
#   -width - width of the MDI slave
#
# Optional:
#   -foreground and -background - the foreground and background
#       of the main window.  inherited.
#   -clicktofocus (optional) - 1 is like Windows and Mac, 0 is like some Unix.
#       inherited.
#
# Results:
#   creates new mdiSlave
class mdiSlave {
    proc mdiSlave {this args} {
        foreach {name value} $args {
            switch -glob -- $name {
                "-b*" {set mdiSlave::($this,background) $value}
                "-c*" {set mdiSlave::($this,clicktofocus) $value}
                "-f*" {set mdiSlave::($this,foreground) $value}
                "-h*" {set mdiSlave::($this,height) $value}
                "-m*" {set mdiSlave::($this,master) $value}
                "-t*" {set mdiSlave::($this,title) $value}
                "-w*" {set mdiSlave::($this,width) $value}
                "-x" {set mdiSlave::($this,x) $value}
                "-y" {set mdiSlave::($this,y) $value}
                default {bgerror "::mdiSlave class constructor : Unknown option ${name}!"}
            }
        }
        foreach name "title height width master x y" {
            if ![info exists mdiSlave::($this,$name)] {
                bgerror "::mdiSlave class constructor : No value specified for required option ${name}!"
                return 0
            }
        }
        foreach name "background clicktofocus foreground" {
            if ![info exists mdiSlave::($this,$name)] {
                set mdiSlave::($this,$name) $mdi::($mdiSlave::($this,master),$name)
            }
        }
        mdiSlave::init $this
        lappend mdi::($mdiSlave::($this,master),slaves) $this
        mdi::showSlave $mdiSlave::($this,master) $this
    }


    proc ~mdiSlave {this} {
        $mdi::($mdiSlave::($this,master),core) delete $mdiSlave::($this,window)
        destroy $mdiSlave::($this,outerFrame)
        set index [lsearch $mdi::($mdiSlave::($this,master),slaves) $this]
        set mdi::($mdiSlave::($this,master),slaves) [lreplace $mdi::($mdiSlave::($this,master),slaves) $index $index]
    }
}

#  -- mdiSlave::init
#
#   Internal procedure to initialize an mdiSlave
#
# Arguments:
#   this
# Results:
#   mdiSlave is initialized and displayed
#
proc mdiSlave::init {this} {
    image create bitmap close-button-$this -data $mdi::(images,x) -foreground white -background black
    image create bitmap max-button-$this -data $mdi::(images,max) -foreground white -background black
    image create bitmap min-button-$this  -data $mdi::(images,min) -foreground white -background black
    image create bitmap menu-button-$this -data $mdi::(images,menu) -foreground white -background black
    image create bitmap normal-button-$this -data $mdi::(images,normal)  -foreground white -background black

    set parent $mdi::($mdiSlave::($this,master),core)
    set mdiSlave::($this,outerFrame) [frame $parent.outerFrame$this -background $mdiSlave::($this,background) -width $mdiSlave::($this,width) -height $mdiSlave::($this,height) -border 0]

# Resize handles:

    set mdiSlave::($this,ridge,topleft) [frame $mdiSlave::($this,outerFrame).topleft -background $mdiSlave::($this,foreground) -height 8 -border 2 -relief raised]
    set mdiSlave::($this,ridge,top) [frame $mdiSlave::($this,outerFrame).top -background $mdiSlave::($this,foreground) -height 8 -border 2 -relief raised]
    set mdiSlave::($this,ridge,topright) [frame $mdiSlave::($this,outerFrame).topright -background $mdiSlave::($this,foreground) -height 8 -border 2 -relief raised]

    set mdiSlave::($this,ridge,bottomleft) [frame $mdiSlave::($this,outerFrame).bottomleft -background $mdiSlave::($this,foreground) -height 8 -border 2 -relief raised]
    set mdiSlave::($this,ridge,bottom) [frame $mdiSlave::($this,outerFrame).bottom -background $mdiSlave::($this,foreground) -height 8 -border 2 -relief raised]
    set mdiSlave::($this,ridge,bottomright) [frame $mdiSlave::($this,outerFrame).bottomright -background $mdiSlave::($this,foreground) -height 8 -border 2 -relief raised]

    set mdiSlave::($this,ridge,lefttop) [frame $mdiSlave::($this,outerFrame).lefttop -background $mdiSlave::($this,foreground) -width 8 -border 2 -relief raised]
    set mdiSlave::($this,ridge,left) [frame $mdiSlave::($this,outerFrame).left -background $mdiSlave::($this,foreground) -width 8 -border 2 -relief raised]
    set mdiSlave::($this,ridge,leftbottom) [frame $mdiSlave::($this,outerFrame).leftbottom -background $mdiSlave::($this,foreground) -width 8 -border 2 -relief raised]

    set mdiSlave::($this,ridge,righttop) [frame $mdiSlave::($this,outerFrame).righttop -background $mdiSlave::($this,foreground) -width 8 -border 2 -relief raised]
    set mdiSlave::($this,ridge,right) [frame $mdiSlave::($this,outerFrame).right -background $mdiSlave::($this,foreground) -width 8 -border 2 -relief raised]
    set mdiSlave::($this,ridge,rightbottom) [frame $mdiSlave::($this,outerFrame).rightbottom -background $mdiSlave::($this,foreground) -width 8 -border 2 -relief raised]

    grid $mdiSlave::($this,ridge,topleft) -row 0 -column 0 -sticky ew -columnspan 2
    grid $mdiSlave::($this,ridge,top) -row 0 -column 2 -sticky ew
    grid $mdiSlave::($this,ridge,topright) -row 0 -column 3 -columnspan 2 -sticky ew

    grid $mdiSlave::($this,ridge,bottomleft) -row 5 -column 0 -columnspan 2 -sticky ew -columnspan 2
    grid $mdiSlave::($this,ridge,bottom) -row 5 -column 2 -sticky ew
    grid $mdiSlave::($this,ridge,bottomright) -row 5 -column 3 -columnspan 2 -sticky ew

    grid $mdiSlave::($this,ridge,lefttop) -row 1 -column 0 -sticky ns
    grid $mdiSlave::($this,ridge,left) -row 2 -column 0 -sticky ns -rowspan 2
    grid $mdiSlave::($this,ridge,leftbottom) -row 4 -column 0 -sticky ns

    grid $mdiSlave::($this,ridge,righttop) -row 1 -column 4 -sticky ns
    grid $mdiSlave::($this,ridge,right) -row 2 -column 4 -sticky ns -rowspan 2
    grid $mdiSlave::($this,ridge,rightbottom) -row 4 -column 4 -sticky ns

    # Resize bindings!  Good god!

    bind $mdiSlave::($this,ridge,top) <B1-Motion> "mdiSlave::resize $this top %x %y"
    bind $mdiSlave::($this,ridge,top) <Button-1> "mdiSlave::startResize $this top %x %y"
    bind $mdiSlave::($this,ridge,top) <B1-ButtonRelease> "mdiSlave::stopResize $this top %x %y"
    bind $mdiSlave::($this,ridge,top) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor top_side"
    bind $mdiSlave::($this,ridge,top) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"

    bind $mdiSlave::($this,ridge,topright) <B1-Motion> "mdiSlave::resize $this topright %x %y"
    bind $mdiSlave::($this,ridge,topright) <Button-1> "mdiSlave::startResize $this topright %x %y"
    bind $mdiSlave::($this,ridge,topright) <B1-ButtonRelease> "mdiSlave::stopResize $this topright %x %y"
    bind $mdiSlave::($this,ridge,topright) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor top_right_corner"
    bind $mdiSlave::($this,ridge,topright) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"


    bind $mdiSlave::($this,ridge,topleft) <B1-Motion> "mdiSlave::resize $this topleft %x %y"
    bind $mdiSlave::($this,ridge,topleft) <Button-1> "mdiSlave::startResize $this topleft %x %y"
    bind $mdiSlave::($this,ridge,topleft) <B1-ButtonRelease> "mdiSlave::stopResize $this topleft %x %y"
    bind $mdiSlave::($this,ridge,topleft) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor top_left_corner"
    bind $mdiSlave::($this,ridge,topleft) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"


    bind $mdiSlave::($this,ridge,bottom) <B1-Motion> "mdiSlave::resize $this bottom %x %y"
    bind $mdiSlave::($this,ridge,bottom) <Button-1> "mdiSlave::startResize $this bottom %x %y"
    bind $mdiSlave::($this,ridge,bottom) <B1-ButtonRelease> "mdiSlave::stopResize $this bottom %x %y"
    bind $mdiSlave::($this,ridge,bottom) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor bottom_side"
    bind $mdiSlave::($this,ridge,bottom) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"


    bind $mdiSlave::($this,ridge,bottomright) <B1-Motion> "mdiSlave::resize $this bottomright %x %y"
    bind $mdiSlave::($this,ridge,bottomright) <Button-1> "mdiSlave::startResize $this bottomright %x %y"
    bind $mdiSlave::($this,ridge,bottomright) <B1-ButtonRelease> "mdiSlave::stopResize $this bottomright %x %y"
    bind $mdiSlave::($this,ridge,bottomright) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor bottom_right_corner"
    bind $mdiSlave::($this,ridge,bottomright) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"


    bind $mdiSlave::($this,ridge,bottomleft) <B1-Motion> "mdiSlave::resize $this bottomleft %x %y"
    bind $mdiSlave::($this,ridge,bottomleft) <Button-1> "mdiSlave::startResize $this bottomleft %x %y"
    bind $mdiSlave::($this,ridge,bottomleft) <B1-ButtonRelease> "mdiSlave::stopResize $this bottomleft %x %y"
    bind $mdiSlave::($this,ridge,bottomleft) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor bottom_left_corner"
    bind $mdiSlave::($this,ridge,bottomleft) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"


    bind $mdiSlave::($this,ridge,left) <B1-Motion> "mdiSlave::resize $this left %x %y"
    bind $mdiSlave::($this,ridge,left) <Button-1> "mdiSlave::startResize $this left %x %y"
    bind $mdiSlave::($this,ridge,left) <B1-ButtonRelease> "mdiSlave::stopResize $this left %x %y"
    bind $mdiSlave::($this,ridge,left) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor left_side"
    bind $mdiSlave::($this,ridge,left) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"

    bind $mdiSlave::($this,ridge,lefttop) <B1-Motion> "mdiSlave::resize $this lefttop %x %y"
    bind $mdiSlave::($this,ridge,lefttop) <Button-1> "mdiSlave::startResize $this lefttop %x %y"
    bind $mdiSlave::($this,ridge,lefttop) <B1-ButtonRelease> "mdiSlave::stopResize $this lefttop %x %y"
    bind $mdiSlave::($this,ridge,lefttop) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor top_left_corner"
    bind $mdiSlave::($this,ridge,lefttop) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"

    bind $mdiSlave::($this,ridge,leftbottom) <B1-Motion> "mdiSlave::resize $this leftbottom %x %y"
    bind $mdiSlave::($this,ridge,leftbottom) <Button-1> "mdiSlave::startResize $this leftbottom %x %y"
    bind $mdiSlave::($this,ridge,leftbottom) <B1-ButtonRelease> "mdiSlave::stopResize $this leftbottom %x %y"
    bind $mdiSlave::($this,ridge,leftbottom) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor bottom_left_corner"
    bind $mdiSlave::($this,ridge,leftbottom) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"


    bind $mdiSlave::($this,ridge,right) <B1-Motion> "mdiSlave::resize $this right %x %y"
    bind $mdiSlave::($this,ridge,right) <Button-1> "mdiSlave::startResize $this right %x %y"
    bind $mdiSlave::($this,ridge,right) <B1-ButtonRelease> "mdiSlave::stopResize $this right %x %y"
    bind $mdiSlave::($this,ridge,right) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor right_side"
    bind $mdiSlave::($this,ridge,right) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"

    bind $mdiSlave::($this,ridge,righttop) <B1-Motion> "mdiSlave::resize $this righttop %x %y"
    bind $mdiSlave::($this,ridge,righttop) <Button-1> "mdiSlave::startResize $this righttop %x %y"
    bind $mdiSlave::($this,ridge,righttop) <B1-ButtonRelease> "mdiSlave::stopResize $this righttop %x %y"
    bind $mdiSlave::($this,ridge,righttop) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor top_right_corner"
    bind $mdiSlave::($this,ridge,righttop) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"

    bind $mdiSlave::($this,ridge,rightbottom) <B1-Motion> "mdiSlave::resize $this rightbottom %x %y"
    bind $mdiSlave::($this,ridge,rightbottom) <Button-1> "mdiSlave::startResize $this rightbottom %x %y"
    bind $mdiSlave::($this,ridge,rightbottom) <B1-ButtonRelease> "mdiSlave::stopResize $this rightbottom %x %y"
    bind $mdiSlave::($this,ridge,rightbottom) <Enter> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor bottom_right_corner"
    bind $mdiSlave::($this,ridge,rightbottom) <Leave> "$mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}"

    set mdiSlave::($this,bar) [frame $mdiSlave::($this,outerFrame).bar -background $mdiSlave::($this,foreground) -height 20 -relief raised -border 2]
    menu-button-$this configure -background $mdiSlave::($this,foreground) -foreground $mdiSlave::($this,background)
    set leftMenu  [menubutton $mdiSlave::($this,outerFrame).leftMenu -image menu-button-$this -menu $mdiSlave::($this,outerFrame).leftMenu.wmMenu -foreground $mdiSlave::($this,background) -background $mdiSlave::($this,foreground) -padx 0 -pady 0 -border 2 -relief raised -height 20 -width 20]
    set mdiSlave::($this,menu) [menu $leftMenu.wmMenu -background $mdiSlave::($this,foreground) -foreground $mdiSlave::($this,background) -tearoff 0]
    $mdiSlave::($this,menu) add command -label "Minimize" -command "mdiSlave::iconize $this"
    $mdiSlave::($this,menu) add command -label "Maximize" -command "mdiSlave::maximize $this"
    $mdiSlave::($this,menu) add command -label "Close" -command "delete $this"

    min-button-$this configure -background $mdiSlave::($this,foreground) -foreground $mdiSlave::($this,background)
    set minimize [button $mdiSlave::($this,bar).minimize -image min-button-$this -command "mdiSlave::iconize $this" -foreground $mdiSlave::($this,background) -background $mdiSlave::($this,foreground) -padx 0 -pady 0]
    max-button-$this configure -background $mdiSlave::($this,foreground) -foreground $mdiSlave::($this,background)
    set maximize [button $mdiSlave::($this,bar).maximize -image max-button-$this -command {} -foreground $mdiSlave::($this,background) -background $mdiSlave::($this,foreground) -command "mdiSlave::maximize $this" -padx 0 -pady 0]
    close-button-$this configure -background $mdiSlave::($this,foreground) -foreground $mdiSlave::($this,background)
    set close [button $mdiSlave::($this,outerFrame).close -image close-button-$this -command "delete $this" -foreground $mdiSlave::($this,background) -background $mdiSlave::($this,foreground) -padx 0 -pady 0]
    set title [label $mdiSlave::($this,bar).title -text $mdiSlave::($this,title) -foreground $mdiSlave::($this,background) -background $mdiSlave::($this,foreground) -pady 0]

    grid $leftMenu -row 1 -column 1 -sticky nwes

    grid $title -row 0 -column 1 -sticky nsew
    grid $minimize -row 0 -column 2 -sticky ne
    grid $maximize -row 0 -column 3 -sticky ne

    grid $close -row 1 -column 3 -sticky nse

    grid rowconfigure $mdiSlave::($this,bar) 0 -weight 0
    grid columnconfigure $mdiSlave::($this,bar) 1 -weight 1

    bind $title <B1-Motion> "mdiSlave::move $this %x %y; break;"
    bind $title <Button-1> "mdiSlave::startMove $this %x %y; break;"
    bind $title <B1-ButtonRelease> "mdiSlave::stopMove $this; break;"
    bind $title <Button-3> "mdiSlave::lower $this; break;"

    set mdiSlave::($this,frame) [frame $mdiSlave::($this,outerFrame).frame -background $mdiSlave::($this,background) -width $mdiSlave::($this,width) -height $mdiSlave::($this,height)]

    grid $mdiSlave::($this,bar) -row 1 -column 2 -sticky new
    grid $mdiSlave::($this,frame) -row 3 -column 2 -sticky nsew -rowspan 2
   
    grid rowconfigure $mdiSlave::($this,outerFrame) 0 -weight 0
    grid rowconfigure $mdiSlave::($this,outerFrame) 1 -weight 0
    grid rowconfigure $mdiSlave::($this,outerFrame) 2 -weight 0
    grid rowconfigure $mdiSlave::($this,outerFrame) 3 -weight 1
    grid rowconfigure $mdiSlave::($this,outerFrame) 4 -weight 0 -minsize 20
    grid rowconfigure $mdiSlave::($this,outerFrame) 5 -weight 0

    grid columnconfigure $mdiSlave::($this,outerFrame) 0 -weight 0
    grid columnconfigure $mdiSlave::($this,outerFrame) 1 -weight 0
    grid columnconfigure $mdiSlave::($this,outerFrame) 2 -weight 1
    grid columnconfigure $mdiSlave::($this,outerFrame) 3 -weight 0
    grid columnconfigure $mdiSlave::($this,outerFrame) 4 -weight 0

    set mdiSlave::($this,maximized) 0
    set mdiSlave::($this,iconized) 0
    update
}

#  -- mdiSlave::iconize
#
#   Iconizes an mdiSlave object.
#
# Arguments:
#   this
# Results:
#   mdiSlave is iconized
#
proc mdiSlave::iconize {this} {
    foreach {x y} [mdiSlave::findIconSpot $this] {}

    image create bitmap icon-$this -data $mdi::(images,icon) -foreground $mdiSlave::($this,background) -background $mdiSlave::($this,foreground) 

    $mdi::($mdiSlave::($this,master),core) create image $x $y -image icon-$this -anchor nw -tags icon$this
    $mdi::($mdiSlave::($this,master),core) create text [expr $x + 25] [expr $y + 60] -anchor n -fill $mdi::($mdiSlave::($this,master),foreground) -text $mdiSlave::($this,title) -tags iconText$this -width 80
    $mdi::($mdiSlave::($this,master),core) delete $mdiSlave::($this,window)

    $mdi::($mdiSlave::($this,master),core) bind icon$this <B1-Motion> "mdiSlave::iconMove $this %x %y; break;"
    $mdi::($mdiSlave::($this,master),core) bind icon$this <Button-1> "mdiSlave::startIconMove $this %x %y; break;"
    $mdi::($mdiSlave::($this,master),core) bind icon$this <B1-ButtonRelease> "mdiSlave::stopIconMove $this; break;"
    set mdiSlave::($this,iconized) 1
}

# mdiSlave::startIconMove --
#
#   internal proc - helps icon move
#
# Arguments:
#   this x y
# Results:
#   icon moves!
#
proc mdiSlave::startIconMove {this x y} {
    set c $mdi::($mdiSlave::($this,master),core)
    foreach {windowx windowy windowx2 windowy2} [$c bbox icon$this] {}
    $c create rectangle $windowx $windowy $windowx2 $windowy2 -outline $mdi::($mdiSlave::($this,master),foreground) -tags moveRect$this
    set mdiSlave::($this,lastIconx) $windowx
    set mdiSlave::($this,lastIcony) $windowy
    set mdiSlave::($this,moveSizeIconX) [expr $windowx2 - $windowx]
    set mdiSlave::($this,moveSizeIconY) [expr $windowy2 - $windowy]
    set mdiSlave::($this,offsetIconX) [expr $x - $windowx]
    set mdiSlave::($this,offsetIconY) [expr $y - $windowy]
}

# mdiSlave::iconMove --
#
#   internal proc - helps icon move
#
# Arguments:
#   this x y
# Results:
#   icon moves!
#
proc mdiSlave::iconMove {this x y} {
    set c $mdi::($mdiSlave::($this,master),core)
    set x [expr $x - $mdiSlave::($this,offsetIconX)]
    set y [expr $y - $mdiSlave::($this,offsetIconY)]
    $c coords moveRect$this $x $y [expr $x + $mdiSlave::($this,moveSizeIconX)] [expr $y + $mdiSlave::($this,moveSizeIconY)]
}

# mdiSlave::startIconMove --
#
#   internal proc - helps icon move
#
# Arguments:
#   this x y
# Results:
#   icon moves!
#
proc mdiSlave::stopIconMove {this} {
    set c $mdi::($mdiSlave::($this,master),core)
    foreach {newx newy trash1 trash2} [$c coords moveRect$this] {}
    if {($mdiSlave::($this,lastIconx) == $newx) && ($mdiSlave::($this,lastIcony) == $newy)} {
        mdi::showSlave $mdiSlave::($this,master) $this
        mdiSlave::raise $this
        $c delete icon$this
        $c delete iconText$this
        $c delete moveRect$this
        mdiSlave::freeIconSpot $this
        set mdiSlave::($this,iconized) 0
        return
    }
    $c delete moveRect$this
    $c delete iconText$this
    $c coords icon$this $newx $newy
    $c create text [expr $newx + 25] [expr $newy + 60] -anchor n -fill $mdi::($mdiSlave::($this,master),foreground) -text $mdiSlave::($this,title) -tags iconText$this -width 80
}

# mdiSlave::freeIconSpot --
#
#   Notifies the icon spot allocator that "this" slave is done with its spot.
#
# Arguments:
#   this
# Results:
#   Nothing
#
proc mdiSlave::freeIconSpot {this} {
    set master $mdiSlave::($this,master)
    lappend mdi::($master,iconSpots) $mdi::($master,$this,iconLoc)
    unset mdi::($master,$this,iconLoc)
}


# mdiSlave::findIconSpot --
#
#   Finds a place to put an icon.
#
# Arguments:
#   this
# Results:
#   [list x y]  : place to put the icon
#
proc mdiSlave::findIconSpot {this} {
    set master $mdiSlave::($this,master)
    set c $mdi::($master,core)

    if ![info exists mdi::($master,iconSpots)] {
        update
        for {set ySize [winfo height $c]; set y 0} {$y <= [expr $ySize - 100]} {incr y 100} {
            for {set xSize [winfo width $c]; set x [expr $xSize - 90] } {$x >= 10} {incr x -100} {
                lappend mdi::($master,iconSpots) [list $x $y]
            }
        }
        if ![info exists mdi::($master,iconSpots)] {
            set mdi::($master,iconSpots) [list [list 0 0]]
        }
    }

    if {[llength $mdi::($master,iconSpots)] == 1} {
        set mdi::($master,$this,iconLoc) [list [list 0 0]]
        return [list 0 0]
    } else {
        set mdi::($master,$this,iconLoc) [lindex $mdi::($master,iconSpots) end]
        set mdi::($master,iconSpots) [lrange $mdi::($master,iconSpots) 0 [expr [llength $mdi::($master,iconSpots)] - 2]]
        return $mdi::($master,$this,iconLoc)
    }

}

# mdiSlave::startResize --
#
#   Internal procedure - handles user resize.
#
# Arguments:
#   this...
# Results:
#   handles resizing.
#
proc mdiSlave::startResize {this which x y} {
    $mdi::($mdiSlave::($this,master),toplevel) configure -cursor sizing
    mdiSlave::raise $this
    set c $mdi::($mdiSlave::($this,master),core)
    foreach {windowx1 windowy1 windowx2 windowy2} [$c bbox $mdiSlave::($this,window)] {}
    $c create rectangle $windowx1 $windowy1 $windowx2 $windowy2 -outline $mdi::($mdiSlave::($this,master),foreground) -tags resizeRect$this
    set mdiSlave::($this,lastx1) $windowx1
    set mdiSlave::($this,lasty1) $windowy1
    set mdiSlave::($this,lastx2) $windowx2
    set mdiSlave::($this,lasty2) $windowy2
    set mdiSlave::($this,offsetX1) [expr $x - $windowx1]
    set mdiSlave::($this,offsetY1) [expr $y - $windowy1]
    set mdiSlave::($this,offsetX2) [expr $x - $windowx2]
    set mdiSlave::($this,offsetY2) [expr $y - $windowy2]
}
# mdiSlave::resize --
#
#   Internal procedure - handles user resize.
#
# Arguments:
#   this...
# Results:
#   handles resizing.
#
proc mdiSlave::resize {this which x y} {
    $mdi::($mdiSlave::($this,master),toplevel) configure -cursor sizing
    set c $mdi::($mdiSlave::($this,master),core)
    set x1 $mdiSlave::($this,lastx1)
    set x2 $mdiSlave::($this,lastx2)
    set y1 $mdiSlave::($this,lasty1)
    set y2 $mdiSlave::($this,lasty2)
    if {[string match "topleft" $which] || [string match "lefttop" $which]} {
        set x1 [expr $x - $mdiSlave::($this,offsetX1)]
        set y1 [expr $y - $mdiSlave::($this,offsetY1)]
    } elseif {[string match "topright" $which] || [string match "righttop" $which]} {
        set x2 [expr $x - $mdiSlave::($this,offsetX2)]
        set y1 [expr $y - $mdiSlave::($this,offsetY1)]
    } elseif  {[string match "rightbottom" $which] || [string match "bottomright" $which]} {
        set x2 [expr $x - $mdiSlave::($this,offsetX2)]
        set y2 [expr $y - $mdiSlave::($this,offsetY2)]
    } elseif  {[string match "leftbottom" $which] || [string match "bottomleft" $which] } {
        set x1 [expr $x - $mdiSlave::($this,offsetX1)]
        set y2 [expr $y - $mdiSlave::($this,offsetY1)]
    } elseif {[string match "top" $which]} {
        set y1 [expr $y - $mdiSlave::($this,offsetY1)]
    } elseif {[string match "bottom" $which]} {
        set y2 [expr $y - $mdiSlave::($this,offsetY2)]
    } elseif {[string match "left" $which]} {
        set x1 [expr $x - $mdiSlave::($this,offsetX1)]
    } elseif {[string match "right" $which]} {
        set x2 [expr $x - $mdiSlave::($this,offsetX2)]
    }
    $c coords resizeRect$this $x1 $y1 $x2 $y2
}

# mdiSlave::stopResize --
#
#   Internal procedure - handles user resize.
#
# Arguments:
#   this...
# Results:
#   handles resizing.
#
proc mdiSlave::stopResize {this which x y} {
    $mdi::($mdiSlave::($this,master),toplevel) configure -cursor {}
    set c $mdi::($mdiSlave::($this,master),core)
    foreach {x1 y1 x2 y2} [$c coords resizeRect$this] {}
    $c delete resizeRect$this
    mdiSlave::changecoords $this $x1 $y1
    mdiSlave::changesize $this [expr $x2 - $x1] [expr $y2 - $y1]
    set mdiSlave::($this,height) [expr $y2 - $y1]
    set mdiSlave::($this,width) [expr $x2 - $x1]
    set mdiSlave::($this,x) $x1
    set mdiSlave::($this,y) $y1
}

    
# mdiSlave::startMove --
#
#   Internal procedure, helps user move mdiSlave
#
# Arguments:
#   this...
# Results:
#   user moves window!
#
proc mdiSlave::startMove {this x y} {
    if $mdiSlave::($this,clicktofocus) {
        mdiSlave::raise $this
    }
    set c $mdi::($mdiSlave::($this,master),core)
    foreach {windowx windowy windowx2 windowy2} [$c bbox $mdiSlave::($this,window)] {}
    $c create rectangle $windowx $windowy $windowx2 $windowy2 -outline $mdi::($mdiSlave::($this,master),foreground) -tags moveRect$this
    set mdiSlave::($this,lastx) $windowx
    set mdiSlave::($this,lasty) $windowy
    set mdiSlave::($this,moveSizeX) [expr $windowx2 - $windowx]
    set mdiSlave::($this,moveSizeY) [expr $windowy2 - $windowy]
    set mdiSlave::($this,offsetX) [expr $x - $windowx]
    set mdiSlave::($this,offsetY) [expr $y - $windowy]
}

# mdiSlave::move --
#
#   Internal procedure, helps user move mdiSlave
#
# Arguments:
#   this...
# Results:
#   user moves window!
#
proc mdiSlave::move {this x y} {
    set c $mdi::($mdiSlave::($this,master),core)
    set x [expr $x - $mdiSlave::($this,offsetX)]
    set y [expr $y - $mdiSlave::($this,offsetY)]
    $c coords moveRect$this $x $y [expr $x + $mdiSlave::($this,moveSizeX)] [expr $y + $mdiSlave::($this,moveSizeY)]
}

# mdiSlave::stopMove --
#
#   Internal procedure, helps user move mdiSlave
#
# Arguments:
#   this...
# Results:
#   user moves window!
#
proc mdiSlave::stopMove {this} {
    set c $mdi::($mdiSlave::($this,master),core)
    foreach {newx newy trash1 trash2} [$c coords moveRect$this] {}
    if {($mdiSlave::($this,lastx) == $newx) && ($mdiSlave::($this,lasty) == $newy)} {
        if !$mdiSlave::($this,clicktofocus) {
            mdiSlave::raise $this
        }
    }
    $c delete moveRect$this
    $c coords $mdiSlave::($this,window) $newx $newy
    set mdiSlave::($this,x) $newx
    set mdiSlave::($this,y) $newy
}

#  -- mdiSlave::raise
#
#   raises an mdiSlave window
#
# Arguments:
#   this
# Results:
#   window is above all others
#
proc mdiSlave::raise {this} {
    ::raise $mdiSlave::($this,outerFrame)
    focus $mdiSlave::($this,frame)
}

#  -- mdiSlave::lower
#
#   lower an mdiSlave window
#
# Arguments:
#   this
# Results:
#   window is below all others
#
 proc mdiSlave::lower {this} {
    ::lower $mdiSlave::($this,outerFrame)
}

#  -- mdiSlave::maximize
#
#   makes mdiSlave fill screen
#
# Arguments:
#   this
# Results:
#   mdiSlave fills screen
#
proc mdiSlave::maximize {this} {
    set mdiSlave::($this,oldHeight) [winfo height $mdiSlave::($this,outerFrame)]
    set mdiSlave::($this,oldWidth) [winfo width $mdiSlave::($this,outerFrame)]
    $mdi::($mdiSlave::($this,master),core) coords $mdiSlave::($this,window) 0 0
    $mdi::($mdiSlave::($this,master),core) itemconfigure $mdiSlave::($this,window) -width [winfo width $mdi::($mdiSlave::($this,master),core)] -height [winfo height $mdi::($mdiSlave::($this,master),core)]
    $mdiSlave::($this,outerFrame) configure -width [winfo width $mdi::($mdiSlave::($this,master),core)] -height [winfo height $mdi::($mdiSlave::($this,master),core)]
    normal-button-$this configure -background $mdiSlave::($this,foreground) -foreground $mdiSlave::($this,background)
    $mdiSlave::($this,bar).maximize configure -image normal-button-$this -command "mdiSlave::unmaximize $this"

    set mdiSlave::($this,oldX) $mdiSlave::($this,x)
    set mdiSlave::($this,oldY) $mdiSlave::($this,y)

    set mdiSlave::($this,height) [winfo height $mdi::($mdiSlave::($this,master),core)]
    set mdiSlave::($this,width) [winfo width $mdi::($mdiSlave::($this,master),core)]
    set mdiSlave::($this,x) 0
    set mdiSlave::($this,y) 0

    set mdiSlave::($this,maximized) 1

    mdiSlave::raise $this
}

# mdiSlave::unmaximize --
#
#   unMaximizes (see above) mdiSlave window
#
# Arguments:
#   this
# Results:
#   mdiSlave returns to previous size
#
proc mdiSlave::unmaximize {this} {
    $mdi::($mdiSlave::($this,master),core) coords $mdiSlave::($this,window) $mdiSlave::($this,oldX) $mdiSlave::($this,oldY)
    $mdi::($mdiSlave::($this,master),core) itemconfigure $mdiSlave::($this,window) -width $mdiSlave::($this,oldWidth) -height $mdiSlave::($this,oldHeight)
    $mdiSlave::($this,outerFrame) configure -width $mdiSlave::($this,oldWidth) -height $mdiSlave::($this,oldHeight)
    max-button-$this configure -background $mdiSlave::($this,foreground) -foreground $mdiSlave::($this,background)
    $mdiSlave::($this,bar).maximize configure -image max-button-$this -command "mdiSlave::maximize $this"

    set mdiSlave::($this,height) $mdiSlave::($this,oldHeight)
    set mdiSlave::($this,width) $mdiSlave::($this,oldWidth)
    set mdiSlave::($this,x) $mdiSlave::($this,oldX)
    set mdiSlave::($this,y) $mdiSlave::($this,oldY)

    set mdiSlave::($this,maximized) 0

    mdiSlave::raise $this
}

# mdiSlave::changecoords --
#
#   Internal proc - changs coords of mdiSlave
#
# Arguments:
#   this x y
# Results:
#   mdiSlave moves!
#
proc mdiSlave::changecoords {this x y} {
    $mdi::($mdiSlave::($this,master),core) coords $mdiSlave::($this,window) $x $y
}

# mdiSlave::changesize --
#
#   Internal proc - changs size of mdiSlave
#
# Arguments:
#   this x y
# Results:
#   mdiSlave resizes!
#
proc mdiSlave::changesize {this sizex sizey} {
    $mdi::($mdiSlave::($this,master),core) itemconfigure $mdiSlave::($this,window) -width $sizex -height $sizey
    $mdiSlave::($this,outerFrame) configure -width $sizex -height $sizey
}

# mdi::globalInit --
#
#   Internal procedure to initialize global data.  Currently just bitmaps.
#
# Arguments:
#   None.
# Results:
#   ::mdi class globals are initialized
#
proc mdi::globalInit {} {
    set mdi::(globalInitDone) 1
    set mdi::(images,x) {
#define x_width 16
#define x_height 16
static unsigned char x_bits[] = {
   0x07, 0xe0, 0x0f, 0xf0, 0x1e, 0x78, 0x3c, 0x3c, 0x78, 0x1e, 0xf0, 0x0f,
   0xe0, 0x07, 0xc0, 0x03, 0xe0, 0x07, 0xf0, 0x0f, 0x78, 0x1e, 0x3c, 0x3c,
   0x1e, 0x78, 0x0f, 0xf0, 0x07, 0xe0, 0x03, 0xc0};
}
   set mdi::(images,max) {
#define max_width 16
#define max_height 16
static unsigned char max_bits[] = {
   0x00, 0x00, 0xfe, 0x7f, 0xfe, 0x7f, 0x06, 0x70, 0x06, 0x70, 0x06, 0x70,
   0x06, 0x70, 0x06, 0x70, 0x06, 0x70, 0x06, 0x70, 0x06, 0x70, 0x06, 0x70,
   0xfe, 0x7f, 0xfe, 0x7f, 0xfe, 0x7f, 0x00, 0x00};
    }
    set mdi::(images,min) {
#define min.xbm_width 16
#define min.xbm_height 16
static unsigned char min.xbm_bits[] = {
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0x07, 0x20, 0x06,
   0x20, 0x06, 0x20, 0x06, 0xe0, 0x07, 0xe0, 0x07, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
    }
    set mdi::(images,menu) {
#define menu.xbm_width 16
#define menu.xbm_height 16
static unsigned char menu.xbm_bits[] = {
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0xfe, 0x3f, 0x02, 0x60, 0xfe, 0x7f, 0xfc, 0x7f, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
    }
    set mdi::(images,normal) {
#define normal_width 16
#define normal_height 16
static unsigned char normal_bits[] = {
   0x00, 0x00, 0xf0, 0x7f, 0x10, 0x60, 0x10, 0x60, 0x10, 0x60, 0x10, 0x60,
   0x1e, 0x60, 0xf2, 0x7f, 0xf2, 0x7f, 0x02, 0x0c, 0x02, 0x0c, 0x02, 0x0c,
   0x02, 0x0c, 0xfe, 0x0f, 0xfe, 0x0f, 0x00, 0x00};
    }
    set mdi::(images,icon) {
#define icon_width 50
#define icon_height 50
static unsigned char icon_bits[] = {
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xfe, 0xff, 0xff,
   0xff, 0xff, 0xff, 0x01, 0x42, 0x00, 0x00, 0x00, 0x42, 0x98, 0x01, 0x5a,
   0xf0, 0xff, 0x7f, 0x42, 0x2b, 0x01, 0x42, 0xf0, 0xff, 0x7f, 0x52, 0x4b,
   0x01, 0x42, 0x00, 0x00, 0x00, 0x42, 0x98, 0x01, 0xfe, 0xff, 0xff, 0xff,
   0xff, 0xff, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
   0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
   0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
   0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x01, 0xfe, 0xff, 0xff, 0xff, 0xff, 0xff, 0x01,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00};
    }
}
    """)


def radint_id():
    from random import randint
    return str(
        randint(0, 9999) + randint(0, 9999) + randint(0, 9999) + randint(0, 9999) - randint(0, 9999) - randint(
            0, 9999))


class MDIWindow(object):
    def __init__(self, clicktofocus=0, toplevel=".", title: str = "", width: int = 500, height: int = 500, bg="black", fg="white"):
        load_samdi()

        self._w = f".mdi{radint_id()}"

        fly_root().eval(f'set {self._w} '
                        f'[new mdi -clicktofocus {clicktofocus} -toplevel {toplevel} -title "{title}" -width {width} -height {height} -bg {bg} -fg {fg}]')


class MDISlave(object):
    def __init__(self, master=None, x: int=0, y: int=0, title: str = "", width: int = 500, height: int = 500, bg="black", fg="white"):
        load_samdi()

        self._w = f".mdiSlave{radint_id()}"

        fly_root().eval(f'set {self._w} '
                        f'[new mdiSlave -master ${master._w} -x {x} -y {y} -title "{title}" -bg {bg} -fg {fg}]')


def demo():
    load_samdi()
    fly_root().eval("""
    # create new mdi window
    set m [new mdi -clicktofocus 0 -toplevel . -title "MDI Test" -width 500 -height 500 -bg black -fg white]
    # create first slave window
    set slave [new mdiSlave -master $m -x 100 -y 100 -title "FirstWindow" -width 300 -height 100 -fg navy -bg white]
    # create second slave window
    set slave [new mdiSlave -m $m -x 150 -y 100 -t "OtherWindow" -w 400 -h 300]

    # create a button bar window
    set buttons [new mdiSlave -master $m -x 200 -y 200 -t "Buttons" -w 100 -h 500 -fg black -bg white]
    set button1 [button $mdiSlave::($buttons,frame).b1 -text "Button 1" -command {}]
    set button2 [button $mdiSlave::($buttons,frame).b2 -text "Button 2" -command {}]
    set button3 [button $mdiSlave::($buttons,frame).b3 -text "Button 3" -command {}]
    pack $button1 $button2 $button3 -side top

    """)


if __name__ == '__main__':
    from tkinter import *

    root = Tk()
    demo()
    root.mainloop()