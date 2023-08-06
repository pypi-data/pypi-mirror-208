from tkfly._tklib import _load_tklib
from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget


def load_plotchart():
    _load_tklib()
    fly_load4("Plotchart", fly_local() + "\\_tklib\\plotchart")


def notifywindow_notifywindow(message: str = "", image=None):
    load_plotchart()
    fly_root().call("::notifywindow::notifywindow", message, image)


def plotchart_demo():
    load_plotchart()
    fly_root().eval("""
canvas .c -background white -width 400 -height 200
pack   .c -fill both

#
# Create the plot with its x- and y-axes
#
set s [::Plotchart::createXYPlot .c {0.0 100.0 10.0} {0.0 100.0 20.0}]

foreach {x y} {0.0 32.0 10.0 50.0 25.0 60.0 78.0 11.0 } {
    $s plot series1 $x $y
}

$s title "Data series"
""")


def plotchart_createXYPlot(widget: Widget, xaxis: list = [], yaxis: list = []):
    load_plotchart()
    fly_root().call(f"::Plotchart::createXYPlot {widget} {'{' + ' '.join(xaxis) + '}'} {'{' + ' '.join(yaxis) + '}'}")


if __name__ == '__main__':
    from tkinter import Tk, Canvas, ttk

    root = Tk()

    canvas = Canvas()
    canvas.pack()

    print("{" + " ".join(["0.0", "100.0", "10.0"]) + "}")

    plotchart_createXYPlot(canvas, ["0.0", "100.0", "10.0"], ["0.0", "100.0", "20.0"])

    root.mainloop()
