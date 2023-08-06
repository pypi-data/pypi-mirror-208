from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def load_history():
    _load_tklib()
    fly_load4("history", fly_local() + "\\_tklib\\history")


def history_init(widget: Widget, len: int = 30):
    load_history()
    fly_root().call("::history::init", widget, len)


def history_add(widget: Widget, line):
    load_history()
    fly_root().call("::history::add", widget, line)


def history_get(widget: Widget):
    load_history()
    return fly_root().call("::history::get", widget)


def history_up(widget: Widget):
    load_history()
    return fly_root().call("::history::up", widget)


def history_down(widget: Widget):
    load_history()
    return fly_root().call("::history::down", widget)


def history_clear(widget: Widget):
    load_history()
    return fly_root().call("::history::clear", widget)


def history_remove(widget: Widget):
    load_history()
    return fly_root().call("::history::remove", widget)


def history_alery(widget: Widget):
    load_history()
    return fly_root().call("::history::alert", widget)


class History(object):
    def __init__(self, widget: Widget, len: int = 30):
        """
namespace eval history {

    bind History <Up>   {::history::up %W}

    bind History <Down> {::history::down %W}

}
        """

        self._w = widget
        self.init(widget, len)

    def init(self, widget: Widget, len: int = 30):
        """
proc ::history::init {w {len 30}} {

    variable history

    variable prefs

    set bt [bindtags $w]

    if {[lsearch $bt History] > -1} { error "$w already has a history" }

    if {[set i [lsearch $bt $w]] < 0} { error "cant find $w in bindtags" }

    bindtags $w [linsert $bt [expr {$i + 1}] History]

    array set history [list $w,list {} $w,cur -1]

    set prefs(maxlen,$w) $len

    return $w

}

        :param widget: target widget
        :param len: list len
        :return:
        """
        history_init(self._w, len)

    def remove(self):
        """
proc ::history::remove {w} {

    variable history

    variable prefs

    set bt [bindtags $w]

    if {[set i [lsearch $bt History]] < 0} { error "$w has no history" }

    bindtags $w [lreplace $bt $i $i]

    unset prefs(maxlen,$w) history($w,list) history($w,cur)

}
        :return:
        """

        history_remove(self._w)

    def up(self):
        """
proc ::history::up {w} {

    variable history

    if {[lindex $history($w,list) [expr {$history($w,cur) + 1}]] != ""} {

        if {$history($w,cur) == -1} {

            set history($w,tmp) [$w get]

        }

        $w delete 0 end

        incr history($w,cur)

        $w insert end [lindex $history($w,list) $history($w,cur)]

    } else {

        alert $w

    }

}

        :return:
        """
        history_up(self._w)

    def down(self):
        """
proc ::history::down {w} {

    variable history

    if {$history($w,cur) != -1} {

        $w delete 0 end

        if {$history($w,cur) == 0} {

            $w insert end $history($w,tmp)

            set history($w,cur) -1

        } else {

            incr history($w,cur) -1

            $w insert end [lindex $history($w,list) $history($w,cur)]

        }

    } else {

        alert $w

    }

}

        :return: None
        """

        history_down(self._w)

    def add(self, line: str):
        """
proc ::history::add {w line} {

    variable history

    variable prefs

    if {$history($w,cur) > -1 && [lindex $history($w,list) $history($w,cur)] == $line} {

        set history($w,list) [lreplace $history($w,list) $history($w,cur) $history($w,cur)]

    }

    set history($w,list) [linsert $history($w,list) 0 $line]

    set history($w,list) [lrange $history($w,list) 0 $prefs(maxlen,$w)]

    set history($w,cur) -1

}

        :param line: a line strings
        :return:
        """

        history_add(self._w, line)

    def get(self):
        """
proc ::history::add {w line} {

    variable history

    variable prefs

    if {$history($w,cur) > -1 && [lindex $history($w,list) $history($w,cur)] == $line} {

        set history($w,list) [lreplace $history($w,list) $history($w,cur) $history($w,cur)]

    }

    set history($w,list) [linsert $history($w,list) 0 $line]

    set history($w,list) [lrange $history($w,list) 0 $prefs(maxlen,$w)]

    set history($w,cur) -1

}
        :return:
        """
        return history_get(self._w)

    def clear(self):
        """
proc ::history::clear {w} {

    variable history

    set history($w,cur) -1

    set history($w,list) {}

    unset -nocomplain history($w,tmp)

}
        """
        history_clear(self._w)

    def alert(self):

        """
proc ::history::alert {w} {bell}
        """

        history_alery(self._w)


if __name__ == '__main__':
    from tkinter import Tk, Entry, ttk

    root = Tk()

    entry = ttk.Entry()
    entry.pack()

    history = History(entry)
    history.add(114514)
    history.add(3.1415926)
    history.up()

    history.alert()

    print(history.get())
    print(type(history.get()))

    root.mainloop()
