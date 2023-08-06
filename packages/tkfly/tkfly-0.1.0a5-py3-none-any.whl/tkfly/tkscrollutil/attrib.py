class Attrib(object):
    def attrib(self, name=None, value=None):
        return self.tk.call(self._w, "attrib", name, value)

    def hasattrib(self, name=None):
        has = self.tk.call(self._w, "hasattrib", name)
        if has == 1:
            return True
        else:
            return False

    def unsetattrib(self, name=None):
        return self.tk.call(self._w, "unsetattrib", name)
