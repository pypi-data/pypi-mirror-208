from tkfly import *
from tkinter import *
from tkinter import ttk


if __name__ == '__main__':
    root = Tk()
    root.title("tkfly demos")

    try:
        from sv_ttk import toggle_theme, use_light_theme, use_dark_theme
    except:
        pass
    else:
        use_light_theme()

    tooltip_panel = ttk.Labelframe(root, labelanchor=N, labelwidget=Label(text="tkFlyToolTip"))

    label = ttk.Label(tooltip_panel, text="Hover me", anchor=CENTER)
    label.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    tooltip = FlyToolTip(root)
    tooltip.tooltip(label, "I`m a tooltip widget")

    tooltip_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

    datefield_panel = ttk.Labelframe(root, labelanchor=N, labelwidget=Label(text="tkFlyDateField"))

    datefield = FlyDateField(datefield_panel)
    datefield.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    datefield_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)


    try:
        import tkfly._telerik
    except:
        pass
    else:
        telerik_panel = ttk.Labelframe(root, labelanchor=N, labelwidget=Label(text="tkFlyTelerik (Only Windows)"))

        telerik_theme = FlyRadWin11Theme()

        menubar = FlyRadMenuBar(telerik_panel, theme=telerik_theme.name)
        menufile = FlyRadMenuItem("File")
        menufile_open = FlyRadMenuItem("Open..", lambda: print("FlyRadMenuItem is Clicked"))
        menufile.add(menufile_open)
        menubar.add(menufile)
        menubar.pack(fill="x", side="top")

        telerik_progressbar_panel = ttk.Labelframe(telerik_panel, labelanchor=N, labelwidget=Label(text="tkFlyRadProgressBar"))

        progressbar = FlyRadProgressBar(telerik_progressbar_panel, theme=telerik_theme.name)
        progressbar.configure(value1=50, value2=25)
        progressbar.pack(fill="x")

        telerik_progressbar_panel.pack(side="top", fill="x", padx=10, pady=10, ipadx=10, ipady=10)

        telerik_button_panel = ttk.Labelframe(telerik_panel, labelanchor=N, labelwidget=Label(text="tkFlyRadButton"))

        button = FlyRadButton(telerik_button_panel, theme=telerik_theme.name, text="Click me", tooltip="create DesktopAlert",
                             command=lambda: print("FlyRadButton is Clicked")
                             )
        button.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        telerik_button_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

        telerik_calc_panel = ttk.Labelframe(telerik_panel, labelanchor=N, labelwidget=Label(text="tkFlyRadCalculator"))

        calc = FlyRadCalculator(telerik_calc_panel, theme=telerik_theme.name)
        calc.bind("<<ValueChanged>>", lambda event: print("FlyRadCalculator`s Value is Changed"))
        calc.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        calc_dropdown = FlyRadCalculatorDropDown(telerik_calc_panel, theme=telerik_theme.name)
        calc_dropdown.pack(fill=X, padx=10, pady=10)

        telerik_calc_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

        telerik_clock_panel = ttk.Labelframe(telerik_panel, labelanchor=N, labelwidget=Label(text="tkFlyRadClock"))

        clock = FlyRadClock(telerik_clock_panel, theme=telerik_theme.name)
        clock.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        telerik_clock_panel.pack(side="right", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

        telerik_cale_panel = ttk.Labelframe(telerik_panel, labelanchor=N, labelwidget=Label(text="tkFlyRadCalendar"))

        cale = FlyRadCalendar(telerik_cale_panel, theme=telerik_theme.name)
        cale.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        telerik_cale_panel.pack(side="right", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

        telerik_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

    try:
        import tkfly._devexpress
    except:
        pass
    else:
        devexpress_panel = ttk.Labelframe(root, labelanchor=N, labelwidget=Label(text="tkFlyDevExpress (Only Windows)"))

        devexpress_skin = FlyXtraSkin()
        devexpress_skin.userskin("wxicompact-office-black")

        devexpress_button_panel = ttk.Labelframe(devexpress_panel, labelanchor=N, labelwidget=Label(text="tkFlyXtraButton"))

        button2 = FlyXtraButton(devexpress_button_panel, text="Click me", command=lambda: print("FlyXtraButton is Clicked"))
        button2.use_directX(True)
        button2.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        devexpress_button_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

        devexpress_panel.pack(side="right", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

    root.mainloop()