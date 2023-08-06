from tkfly.core import fly_load4, fly_root, fly_local, fly_chdir
from tkinter import Widget, Image, Label
from enum import Enum


def load_blend2d():
    fly_load4("Blend2d", fly_local() + "\\_blend2d")


LINEAR = "LINEAR"
RADIAL = "RADIAL"
CONICAL = "CONICAL"


class GRADIENT_TYPE(Enum):
    LINEAR = "LINEAR"
    RADIAL = "RADIAL"
    CONICAL = "CONICAL"


def color(color_name, alpha: float = 1.0):
    return f"BL::color {color_name} {alpha}"


def rgb(RR=0, GG=0, BB=0, alpha: float = 1.0):
    return f"BL::rgb {RR} {GG} {BB} {alpha}"


def gradient(type: GRADIENT_TYPE, values, stopList):
    return f"BL::gradient {type} {values} [list {stopList}]"


def circle(circlex, circley, r=50):
    return "BL::circle" + " {" + str(circlex) + " " + str(circley) + "} " + str(r)


def rect(x, y, width, height):
    return "BL::rect" + f" {str(x)} {str(y)} {str(width)} {str(height)}"


def roundrect(x, y, width, height, rx, ry=""):
    return "BL::roundrect" + f" {str(x)} {str(y)} {str(width)} {str(height)} {str(rx)} {str(ry)}"


def text(cx, cy, font, string: str = ""):
    return "BL::text" + " {" + str(cx) + " " + str(cy) + "} " + str(font) + " " + f'"{str(string)}"'


def classes():
    load_blend2d()
    return fly_root().call("BL::classes")


def libinfo():
    load_blend2d()
    return fly_root().call("BL::libinfo")


def platform():
    load_blend2d()
    return fly_root().call("BL::platform")


def radint_id():
    from random import randint
    return str(randint(0, 9999) + randint(0, 9999) + randint(0, 9999) + randint(0, 9999) - randint(0, 9999) - randint(0, 9999))


class Blend2DImage(Image):
    def __init__(self, surface, cnf={}, master=None, **kw):
        Image.__init__(self, 'blend2d', surface, cnf, **kw)


class Surface(object):
    def __init__(self, name: str = ".surface", width: int = 450, height: int = 450, iscreate: bool = True):
        load_blend2d()
        self._name = name+radint_id()
        if iscreate:
            self.create(self._name, width=width, height=height)

    def destory(self):
        fly_root().call(self._name, "destory")

    def create(self, name: str = ".surface", width: int = 450, height: int = 450):
        fly_root().eval(f"BL::Surface create {name} -format "+"{ "+str(width)+" "+str(height)+" }")

    def clear(self, style="BL::color black"):
        fly_root().eval(f"{self._name} clear -fill.style [{style}]")

    def save(self, file: str = "surface.bmp"):
        fly_root().call(self._name, "save", file)

    def flush(self):
        fly_root().call(self._name, "flush")

    def reset(self):
        fly_root().call(self._name, "reset")

    def photo(self, name):
        from tkinter import PhotoImage
        _photo = PhotoImage(name)
        fly_root().call(self._name, "writeToTkphoto", name)
        return _photo

    def fill(self, geometry, style="BL::color red"):
        fly_root().eval(f"{self._name} fill [{geometry}] -style [{style}]")

    def size(self):
        return fly_root().call(self._name, "size")

    def configure(self, **kwargs):
        if "fillstyle" in kwargs:
            fly_root().eval(f"{self._name} configure -fill.style [{kwargs.pop('fillstyle')}]")
        if "size" in kwargs:
            size = kwargs.pop("size")
            fly_root().eval(f"{self._name} configure -format "+"{ "+str(size[0])+" "+str(size[1])+" }")

    def cget(self, optionName):
        if optionName == "fillstyle":
            return fly_root().eval(f"{self._name} cget -fill.style")


class FontFace(object):
    def __init__(self, fontfile: str, faceIdxL: int = 145, name: str = ".fontface", iscreate: bool = True):
        load_blend2d()
        self._name = name+radint_id()
        if iscreate:
            self.create(name=self._name, fontfile=fontfile, faceIdxL=faceIdxL)

    def create(self, fontfile: str, faceIdxL: int, name: str = ".surface"):
        fly_root().eval(f'BL::FontFace create {name} "{fontfile}" {faceIdxL}')


class Font(object):
    def __init__(self, fontface: FontFace, fontsize: int = 12, name: str = ".font", iscreate: bool = True):
        load_blend2d()
        self._name = name+radint_id()
        if iscreate:
            self.create(name=self._name, fontface=fontface, fontsize=fontsize)

    def create(self, fontface: FontFace, name: str = ".surface", fontsize: int = 12):
        fly_root().eval(f'BL::Font create {name} {fontface} {fontsize}')

    def names(self):
        return fly_root().call("BL::Font", "names")


class ImageSurface(Label):
    def __init__(self, *args, name=".surface.image", image_name=".surface.image.image", width: int = 450, height: int = 450, iscreate: bool = True, **kwargs):
        self.surface = Surface(name, iscreate=iscreate, width=width, height=height)
        self.surface.clear()

        self.image_name = image_name+radint_id()

        super().__init__(*args, **kwargs)

        self.image = self.surface.photo(self.image_name)
        self.configure(image=self.image)

        self.bind("<Map>", lambda _: self.update_image())
        self.bind("<Configure>", lambda _: self.update_image())

    def update_image(self):
        from random import randint
        self.surface.flush()
        image = self.surface.photo(self.image_name+"."+radint_id())
        self.image = image
        self.configure(image=image)
        return image


class Blend2D(object):
    def __init__(self):
        """
        Blead2D引擎
        """

        load_blend2d()

    @staticmethod
    def create_fontface(name: str = ".fontface", fontfile: str = None, id: int = 100):
        return FontFace(name=name, fontfile=fontfile.replace("\\", "/"), faceIdxL=str(id)+radint_id())

    @staticmethod
    def create_font(name: str = ".font", fontface: FontFace = None, fontsize: int = 12):
        return Font(name=name, fontface=fontface._name, fontsize=fontsize)

    @staticmethod
    def create_surface(name: str = ".surface", size: tuple = (450, 450)):
        return Surface(name=name, width=size[0], height=size[1])

    @staticmethod
    def create_image_surface(name: str = ".surface", image_name: str = ".surface.image", size: tuple = (450, 450)):
        return ImageSurface(name=name, image_name=image_name, width=size[0], height=size[1])

    @staticmethod
    def create_roundrect(x, y, width, height, rx, ry=""):
        return roundrect(x, y, width, height, rx, ry)

    @staticmethod
    def create_rect(x, y, width, height):
        return rect(x, y, width, height)

    @staticmethod
    def create_circle(pos: tuple = (0, 0), size: int or float = 40):
        return circle(pos[0], pos[1], size)

    @staticmethod
    def create_text(pos: tuple = (0, 0), font: Font = None, string: str = ""):
        if font is None:
            from tkfly.core import fly_local, fly_chdir

            with fly_chdir(fly_local()+"\\blend2d"):
                _fontface = FontFace(fontfile="HarmonyOS_Sans_Medium.ttf", faceIdxL=1, name=".fontface.road_page")
                _font = Font(fontface=_fontface._name)

            font = _font

        return text(pos[0], pos[1], font._name, string)

    @staticmethod
    def get_color(name="red", alpha: float = 1.0):
        return color(name, alpha)

    @staticmethod
    def get_rgb(rgb: tuple = (0, 0, 0), alpha: float = 1.0):
        return color(rgb[0], rgb[1], rgb[2], alpha)

    @property
    def platform(self):
        return platform()

    @property
    def libinfo(self):
        return libinfo()


if __name__ == '__main__':
    from tkinter import Tk, PhotoImage, Label

    root = Tk()

    info = Label(text=libinfo())
    info.pack(fill="x", side="top")

    blend2d = Blend2D()

    surface = blend2d.create_image_surface(size=(300, 450))

    # gradient_color = gradient(LINEAR, "{50 250 400 400}",
    #                           f"0.0 [{color('red')}] 0.5 [{color('orange')}] 1.0 [{color('yellow')}]")

    from tkfly.core import fly_local, fly_chdir

    fontface1 = blend2d.create_fontface(fontfile="HarmonyOS_Sans_Medium.ttf")
    font1 = blend2d.create_font(fontface=fontface1)

    surface.surface.fill(circle(150, 225, 50), color("lightblue"))

    surface.surface.fill(roundrect(20, 20, 100, 100, 20), color("orange"))

    surface.pack(fill="both")

    root.mainloop()
