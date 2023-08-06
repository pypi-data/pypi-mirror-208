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

        telerik_theme = FlyTKWin11Theme()

        telerik_button_panel = ttk.Labelframe(telerik_panel, labelanchor=N, labelwidget=Label(text="tkFlyTKButton"))

        button = FlyTKButton(telerik_button_panel, theme=telerik_theme.name, text="Click me to create DesktopAlert",
                             command=lambda: FlyTKDesktopAlert(theme=telerik_theme.name, title="tkFlyTKDesktopAlert", message="Hi w_w").show()
                             )
        button.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        telerik_button_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

        telerik_calc_panel = ttk.Labelframe(telerik_panel, labelanchor=N, labelwidget=Label(text="tkFlyTKCalculator"))

        calc = FlyTKCalculator(telerik_calc_panel, theme=telerik_theme.name)
        calc.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        calc_dropdown = FlyTKCalculatorDropDown(telerik_calc_panel, theme=telerik_theme.name)
        calc_dropdown.pack(fill=X, padx=10, pady=10)

        telerik_calc_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

        telerik_clock_panel = ttk.Labelframe(telerik_panel, labelanchor=N, labelwidget=Label(text="tkFlyTKClock"))

        clock = FlyTKClock(telerik_clock_panel, theme=telerik_theme.name)
        clock.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        telerik_clock_panel.pack(side="right", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

        telerik_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)

    root.mainloop()