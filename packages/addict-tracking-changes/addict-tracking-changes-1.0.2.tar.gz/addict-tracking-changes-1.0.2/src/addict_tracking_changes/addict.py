# This file is part of addict-tracking-changes
#
# Copyright (c) [2023] by Webworks, MonalLabs.
# This file is released under the MIT License.
#
# Author(s): Webworks, Monal Labs.

# MIT License

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import copy


def isnamedtupleinstance(x):
    t = type(x)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple:
        return False
    f = getattr(t, "_fields", None)
    if not isinstance(f, tuple):
        return False
    return all(type(n) == str for n in f)


def get_changed_history_list(arritems, tprefix="", path_guards=None):
    for idx, aitem in enumerate(arritems):
        if isinstance(aitem, Dict):
            yield from aitem.get_changed_history(
                tprefix + f"/{idx}", path_guards=path_guards
            )
        elif isinstance(aitem, list):
            yield from get_changed_history_list(
                aitem, tprefix + f"/{idx}", path_guards=path_guards
            )
        else:
            # list are by default tracked for changes
            yield tprefix + f"/{idx}"


def clear_changed_history_list(arritems):
    for _idx, aitem in enumerate(arritems):
        if isinstance(aitem, Dict):
            aitem.clear_changed_history()
        elif isinstance(aitem, list):
            clear_changed_history_list(aitem)
        else:
            pass


class Dict(dict):
    def __init__(__self, *args, **kwargs):
        object.__setattr__(__self, "__parent", kwargs.pop("__parent", None))
        object.__setattr__(__self, "__key", kwargs.pop("__key", None))
        object.__setattr__(__self, "__frozen", False)
        object.__setattr__(
            __self, "__track_changes", kwargs.pop("track_changes", False)
        )
        # to track __getattr__/__getitem chain of calls
        object.__setattr__(__self, "__breadcrumb_parent_dict", None)
        object.__setattr__(__self, "__breadcrumb_parent_dict_key", None)

        # __track_changes specifies tracking is on
        if object.__getattribute__(__self, "__track_changes"):
            object.__setattr__(__self, "__tracker", set())
        for arg in args:
            if not arg:
                continue
            elif isinstance(arg, dict):
                for key, val in arg.items():
                    __self[key] = __self._hook(val)
            elif isinstance(arg, tuple) and (not isinstance(arg[0], tuple)):
                __self[arg[0]] = __self._hook(arg[1])
            else:
                for key, val in iter(arg):
                    __self[key] = __self._hook(val)

        for key, val in kwargs.items():
            __self[key] = __self._hook(val)

    def __setattr__(self, name, value):
        if hasattr(self.__class__, name):
            raise AttributeError(
                "'Dict' object attribute " "'{0}' is read-only".format(name)
            )
        else:
            self[name] = value  # this invokes __setitem__

    def __setitem__(self, name, value):
        isFrozen = hasattr(self, "__frozen") and object.__getattribute__(
            self, "__frozen"
        )
        if isFrozen and name not in super(Dict, self).keys():
            raise KeyError(name)

        isTracked = False
        try:
            if object.__getattribute__(self, "__track_changes"):
                object.__getattribute__(self, "__tracker").add((name))

            curr_dict = self

            while True:
                if object.__getattribute__(curr_dict, "__breadcrumb_parent_dict"):
                    parent_dict = object.__getattribute__(
                        curr_dict, "__breadcrumb_parent_dict"
                    )
                    parent_key = object.__getattribute__(
                        curr_dict, "__breadcrumb_parent_dict_key"
                    )
                    if object.__getattribute__(parent_dict, "__track_changes"):
                        object.__getattribute__(parent_dict, "__tracker").add(
                            (parent_key)
                        )

                    # erase the breadcrumbs
                    object.__setattr__(curr_dict, "__breadcrumb_parent_dict", None)
                    object.__setattr__(curr_dict, "__breadcrumb_parent_dict_key", None)
                    # visit the parent
                    curr_dict = parent_dict
                else:
                    break
        except AttributeError as e:
            # skip the __track_changes not present attribute error.
            # which happens when Dict object is pickled/unpickled.
            pass

        super(Dict, self).__setitem__(name, value)
        try:
            p = object.__getattribute__(self, "__parent")
            key = object.__getattribute__(self, "__key")
        except AttributeError:
            p = None
            key = None
        if p is not None:
            p[key] = self
            object.__delattr__(self, "__parent")
            object.__delattr__(self, "__key")
        return isTracked

    # may introduce in future if required
    # def __add__(self, other):
    #     raise NotImplementedError("add operation not supported")

    @classmethod
    def _hook(cls, item):
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, (list, tuple)) and not isnamedtupleinstance(item):
            return type(item)(cls._hook(elem) for elem in item)
        return item

    def __getattr__(self, item):
        # _getattr is called when item is already present in the dict
        # but it may not be part of the tracker; removed via clear_changed_history
        child_item = super(Dict, self).__getitem__(item)
        if isinstance(child_item, type(self)):
            object.__setattr__(child_item, "__breadcrumb_parent_dict", self)
            object.__setattr__(child_item, "__breadcrumb_parent_dict_key", item)

        return child_item

    def __getitem__(self, key):
        if object.__getattribute__(self, "__track_changes"):
            object.__getattribute__(self, "__tracker").add((key))
        return self.__getattr__(key)

    def __missing__(self, name):
        if object.__getattribute__(self, "__frozen"):
            raise KeyError(name)
        return self.__class__(
            __parent=self,
            __key=name,
            track_changes=object.__getattribute__(self, "__track_changes"),
        )

    def __delitem__(self, key):
        if object.__getattribute__(self, "__track_changes"):
            # key may have removed with clear_changed_history
            if key in object.__getattribute__(self, "__tracker"):
                object.__getattribute__(self, "__tracker").remove(key)
        return super(Dict, self).__delitem__(key)

    # Phasing out pop for now
    # use del mydict['key'] expression to delete
    # def pop(self, key, default=None):
    #     """
    #     called when pop myd[a] is called
    #     """

    #     try:
    #         if object.__getattribute__(self, "__track_changes"):
    #             object.__getattribute__(self, "__tracker").remove(key)
    #     except:
    #         logging.info("Fatal error: cannot remove item from tracker")
    #         pass
    #     return super(Dict, self).pop(key, default)

    def __delattr__(self, name):
        del self[name]

    def to_dict(self):
        base = {}
        for key, value in self.items():
            if isinstance(value, type(self)):
                base[key] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                base[key] = type(value)(
                    item.to_dict() if isinstance(item, type(self)) else item
                    for item in value
                )
            else:
                base[key] = value
        return base

    def __copy__(self):
        raise NotImplementedError("Shallow copy is not supported for this class.")

    def __deepcopy__(self, memo):
        other = self.__class__()
        memo[id(self)] = other
        for key, value in self.items():
            other[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return other

    # ================================================================
    # Not removed; not added yet feature. Might fold in
    # if usage is clear

    # def update(self, *args, **kwargs):
    #     other = {}
    #     if args:
    #         if len(args) > 1:
    #             raise TypeError()
    #         other.update(args[0])
    #     other.update(kwargs)
    #     for k, v in other.items():
    #         if (
    #             (k not in self)
    #             or (not isinstance(self[k], dict))
    #             or (not isinstance(v, dict))
    #         ):
    #             self[k] = v
    #         else:
    #             self[k].update(v)

    # def __getnewargs__(self):
    #     return tuple(self.items())

    # def __getstate__(self):
    #     return self

    # def __setstate__(self, state):
    #     self.update(state)

    # def __or__(self, other):
    #     #print ("__or__")
    #     if not isinstance(other, (Dict, dict)):
    #         return NotImplemented
    #     new = Dict(self)
    #     new.update(other)
    #     return new

    # def __ror__(self, other):
    #     if not isinstance(other, (Dict, dict)):
    #         return NotImplemented
    #     new = Dict(other)
    #     new.update(self)
    #     return new

    # def __ior__(self, other):
    #     self.update(other)
    #     return self

    # def setdefault(self, key, default=None):
    #     if key in self:
    #         return self[key]
    #     else:
    #         self[key] = default
    #         return default

    # ============================== end =============================
    def freeze(self, shouldFreeze=True):
        object.__setattr__(self, "__frozen", shouldFreeze)
        for _key, val in self.items():
            if isinstance(val, Dict):
                val.freeze(shouldFreeze)

    def unfreeze(self):
        self.freeze(False)

    # as of now; don't see need for get
    # however --> keeping the option open
    # to be included if needed
    # def get(self, key, default=None):
    #     #print(f"Getting key '{key}'")
    #     return super().get(key, default)

    def get_changed_history(self, prefix="", path_guards=None):
        if super().__getattribute__("__track_changes") is False:
            return

        for key, value in self.items():
            if key in super().__getattribute__("__tracker"):
                if isinstance(value, type(self)):
                    if not path_guards or prefix + "/" + str(key) not in path_guards:
                        yield from value.get_changed_history(
                            prefix + "/" + str(key), path_guards=path_guards
                        )

                elif isinstance(value, list):
                    yield from get_changed_history_list(
                        value, prefix + "/" + str(key), path_guards=path_guards
                    )
                else:
                    yield prefix + "/" + key

    def clear_changed_history(self):
        if super().__getattribute__("__track_changes") is False:
            return
        for _key, value in self.items():
            if isinstance(value, type(self)):
                value.clear_changed_history()
            elif isinstance(value, list):
                clear_changed_history_list(value)
        super().__getattribute__("__tracker").clear()

    def set_tracker(self, track_changes=False):
        """
        pickle/unpickle forgets about trackers and frozenness
        """
        for _key, value in self.items():
            if isinstance(value, type(self)):
                value.set_tracker(self)
        object.__setattr__(self, "__frozen", False)
        object.__setattr__(self, "__track_changes", track_changes)
        if track_changes:
            object.__setattr__(self, "__tracker", set())


def walker(adict, ppath="", guards=None):
    for key, value in adict.items():
        if guards:
            if f"{ppath}/{key}" in guards:
                yield (f"{ppath}/{key}", value)
                continue  # stop at the guard
        if isinstance(value, Dict):
            yield from walker(value, ppath + f"/{key}", guards=guards)
        else:
            yield (f"{ppath}/{key}", value)
            pass
