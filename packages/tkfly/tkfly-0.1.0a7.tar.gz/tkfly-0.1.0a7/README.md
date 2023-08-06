# tkfly
基于`tkinter` `tcl / tk` `pythonnet / winforms`扩展的中型组件库

`tkfly`指`tkinter`插上翅膀飞翔，意为借助扩展的功能翱翔。

([tklib -大小约3.7MB](https://core.tcl-lang.org/tklib))

([twapi -大小约2.0MB](https://twapi.magicsplat.com/))

([blend2d -大小约7.6MB](https://wiki.tcl-lang.org/page/Blend2d))

([telerik]())

帮助你开发大型高级的程序

## 教程

### 开始
```bash
# 暂时处于预览版
python -m pip install tkfly --pre
```

### 工具提示
`tkfly`通过`tkinter`调用`tcl`导入`tklib`实现，可以实现`tklib`库所能实现的各种功能。
让我来运行一个最简单工具提示吧！
(基于[tklib/tooltip](https://core.tcl-lang.org/tklib/doc/trunk/embedded/md/tklib/files/modules/tooltip/tooltip.md))
```python
from tkinter import Tk, ttk
from tkfly import FlyToolTip

root = Tk()

tooltip = FlyToolTip()

button = ttk.Button()
tooltip.tooltip(button, "button1")
button.pack()

root.mainloop()
```

### 输入框小组件的历史记录功能
输入框没有历史记录功能一直是个遗憾，但是可以通过扩展组件实现
(基于[tklib/history](https://core.tcl-lang.org/tklib/doc/trunk/embedded/md/tklib/files/modules/history/tklib_history.md))
```python
from tkinter import Tk, Entry, ttk
from tkfly import FlyHistory

root = Tk()

entry = ttk.Entry()
entry.pack()

history = FlyHistory(entry)
history.add(114514)
history.add(3.1415926)
history.up()

root.mainloop()
```
你可以通过按键盘上下键切换历史记录文本。

#### 初始化
```python
history.init() 
```
初始化时会有一个必选参数`widget`和一个可选参数`len`，`widget`是目标组件，`len`是设定的长度。

初始化完成后，就可以通过上下键来切换了

#### 添加记录
```python
history.add() 
```
添加需要一行字串符参数，添加后可以用上下键切换找到记录

#### 获取历史记录列表
```python
history.get() 
```
你将会得到一个`元组`

### 日期输入框
可以通过上下键调整日期
```python
from tkinter import Tk
from tkfly import FlyDateField

root = Tk()

datefield = FlyDateField()
datefield.pack()

datefield2 = FlyDateField(format="%Y-%m-%d")
datefield2.pack()

root.mainloop()
```
#### 日期格式
可以通过`format`参数修改格式，示例`"%Y-%m-%d"`，其中%Y是年号，%m是月份，%d是天。

### 2D渲染
Blend2D是一个高性能的2D矢量图形引擎，通过调用可以生成图片为label组件设置图片显示

下面有个示例
```python
from tkinter import *
from tkfly import *

root = Tk()
blend2D = Fly2D()
surface = blend2D.create_image_surface(
    size=(500, 500)
)

print("Create ImageSurface", surface.image_name)

surface.surface.fill(
    blend2D.create_circle((150, 150), 50),
    blend2D.get_color("lightblue", alpha=0.5)
)

surface.surface.fill(
    blend2D.create_circle((250, 250), 60),
    blend2D.get_color("lightblue", alpha=1.0)
)

surface.surface.fill(
    blend2D.create_circle((350, 350), 55),
    blend2D.get_color("lightblue", alpha=0.75)
)

from tkfly.core import fly_local, fly_chdir

with fly_chdir(fly_local() + "\\blend2d"):
    fontface = blend2D.create_fontface(fontfile="HarmonyOS_Sans_Medium.ttf")
    font = blend2D.create_font(fontface=fontface, fontsize=20)

print("Create FontFace", fontface._name)
print("Create Font", font._name)

surface.surface.fill(
    blend2D.create_text((225, 257), string="Fly2D", font=font),
    blend2D.get_color("black")
)

surface.pack()

surface.surface.save("fly2d.png")

root.mainloop()
```

### 扩展组件
#### Document
这是类似`多文档窗口`类的组件，只是暂时布局没想到好的方案，会空下大部分的空间
```python
from tkinter import *
from tkinter import ttk
from tkfly import *

root = Tk()

document = FlyMkDocument()

button = ttk.Button(document)
button.pack(fill="both", expand="yes")

document.config(title="这是多文档窗口")

root.mainloop()
```

#### ToolBar
工具栏组件
```python
from tkinter import *
from tkfly import *

root = Tk()

toolbar = FlyMkToolBar()

button1 = toolbar.add(
    "button",
    command=lambda:
        print(f"toolbutton is {toolbar.get(button1)}")
)
button2 = toolbar.add("button", command=lambda: toolbar.delete(button2))


toolbar.pack(fill="x", side="top")

root.mainloop()
```


## tkscrollutil
实际上这就是作者我以前做过的一个项目。

### ScrolllArea
可以快速地为水平滚动、垂直滚动组件设置滚动条

#### 属性
`autohidescrollbars` 设置组件是否自动隐藏滚动条。布尔数值。默认`False`。也就是说，当你把鼠标指针放到滚动条上时，滚动条才会显示。 

`lockinterval` 设置组件滚动条地锁定间隔。整数数值。默认`300`.

`respectheader` 仅当将嵌入到组件内地`tablelist`版本为6.5及以上版本时才能使用，后续等开发出`tablelist`的扩展库时补充

`respecttitlecolumns` 仅当将嵌入到组件内地`tablelist`版本为6.5及以上版本时才能使用，后续等开发出`tablelist`的扩展库时补充

`xscrollbarmode` 设置水平滚动条的模式。可选值为`static` `dynamic` `none`。默认`none`。`static`为常驻滚动条；`dynamic`为自动滚动条；`none`为没有滚动条

`yscrollbarmode` 设置垂直滚动条的模式。可选值为`static` `dynamic` `none`。默认`static`。`static`为常驻滚动条；`dynamic`为自动滚动条；`none`为没有滚动条

#### 方法
`setwidget` 设置具有滚动条属性的组件，使组件快速设置滚动条。

#### 示例
```python
from tkinter import Tk, Listbox
from tkfly.tkscrollutil import ScrollArea

Window = Tk()

Area = ScrollArea(Window)
List = Listbox(Area)
for Item in range(50):
    List.insert(Item+1, Item+1)
Area.setwidget(List)
Area.pack(fill="both", expand="yes")

Window.mainloop()
```

#### ttkScrollArea
见上方。与`ScrollArea`不同的是，`ttkScrollArea`具有ttk组件的属性，并且`ScrollArea`和`ttkScrollArea`不能同时使用。

#### 示例
```python
from tkinter import Tk, Listbox
from tkfly.tkscrollutil import ttkScrollArea

Window = Tk()

Area = ttkScrollArea(Window)
List = Listbox(Area)
for Item in range(50):
    List.insert(Item+1, Item+1)
Area.setwidget(List)
Area.pack(fill="both", expand="yes")

Window.mainloop()
```

#### ScrollSync
同步滚动条，当其中一个滚动时，另一个也会跟随着移动起来。

#### 方法
`setwidgets` 设置同步滚动的组件。需输入列表，如 [widget1, widget2] 。

`widgets` 获取同步滚动的组件。

#### 示例
```python
from tkinter import Tk, Listbox, Frame
from tkfly.tkscrollutil import ScrollArea, ScrollSync
Window = Tk()

Frame = Frame()

Area = ScrollArea(Frame, yscrollbarmode="static")
Sync = ScrollSync(Area)
Area.setwidget(Sync)

Area.pack(fill="y", side="right")

List1 = Listbox()
List1.pack(fill="both", side="left", expand="yes")
List2 = Listbox()
List2.pack(fill="both", side="right", expand="yes")

for Item in range(300):
    List1.insert(Item, Item)
    List2.insert(Item, Item)

Sync.setwidgets([List1, List2])

Frame.pack(fill="both", expand="yes")

Window.mainloop()
```

#### ttkScrollSync
见上方。与`ScrollSync`不同的是，`ttkScrollSync`具有ttk组件的属性，并且`ScrollSync`和`ttkScrollSync`不能同时使用。

#### 示例
```python
from tkinter import Tk, Listbox, Frame
from tkfly.tkscrollutil import ttkScrollArea, ttkScrollSync
Window = Tk()

Frame = Frame()

Area = ttkScrollArea(Frame, yscrollbarmode="static")
Sync = ttkScrollSync(Area)
Area.setwidget(Sync)

Area.pack(fill="y", side="right")

List1 = Listbox()
List1.pack(fill="both", side="left", expand="yes")
List2 = Listbox()
List2.pack(fill="both", side="right", expand="yes")

for Item in range(300):
    List1.insert(Item, Item)
    List2.insert(Item, Item)

Sync.setwidgets([List1, List2])

Frame.pack(fill="both", expand="yes")

Window.mainloop()
```

#### ttkScrolledNoteBook
scrollutil本身不提供ScrolledNoteBook，只有ttk能够提供。
```python
from tkinter import Tk, Frame
from tkfly.tkscrollutil import ttkScrolledNoteBook, addclosetab
Window = Tk()

NoteBook = ttkScrolledNoteBook(Window)

addclosetab("TNotebook")

NoteBook.add(Frame(NoteBook), text="Hello World")
NoteBook.pack(fill="both", expand="yes")

Window.mainloop()
```