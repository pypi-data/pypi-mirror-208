import inspect
import types
import re
import sys
import importlib

mod_ind = 0

class SerDeserClass:
    def __init__(self, mode: str = "json"):
        self.__mode = mode
        if self.__mode == "json":
            self.basic = '"type": "{type}", "value": {val}'
        else:
            self.basic = "<{type}> {val} </{type}>"

    def dumps(self, obj) -> str:
        return self.serialize(obj)

    def dump(self, obj, filepath: str):
        with open(filepath, "w") as file:
            print(self.serialize(obj), file=file)

    def load(self, filepath: str):
        with open(filepath, "r") as file:
            return self.deserialize(file.read())

    def loads(self, txt: str):
        return self.deserialize(txt)

    def dict_to_obj(self, d: dict) -> str:
        if self.__mode == "json":
            rstr = "{"
            for key, val in d.items():
                rstr += f'"{key}": {self.serialize(val)}, '

            rstr = rstr[:-2:]
            rstr += "}"

            return rstr
        else:
            rstr = ""
            for key, val in d.items():
                rstr += (
                    " " + self.__add_attribute(self.serialize(val), "key", key) + " "
                )

            return rstr
        
    @staticmethod
    def type_to_dict(obj: type) -> dict:
        dct = obj.__dict__

        thing = __builtins__
        if not isinstance(thing, dict):
            thing = thing.__dict__

        if obj in thing.values():
            ret_dct = {"builtin type": obj.__name__}
            return ret_dct

        ret_dct: dict = {"__name__": obj.__name__}
        for k, v in dct.items():
            if k == "__module__" or k == "__dict__" or k == "__weakref__":
                continue

            ret_dct[k] = v

        ret_dct["parents"] = tuple(obj.__bases__)

        if ret_dct["parents"] == (object,):
            ret_dct["parents"] = tuple()

        return ret_dct


    def serialize_builtin_function(self, obj: types.BuiltinFunctionType):
        return self.basic.format(
            type="builtinfunction", val=self.serialize(obj.__name__)
        )

    def serialize_method(self, obj: types.MethodType):
        tpl = obj.__func__, obj.__self__
        return self.basic.format(type="method", val=self.serialize(tpl))
    
    def serialize_staticmethod(self, obj: staticmethod):
        func = obj.__func__

        return self.basic.format(type="staticmethod", val=self.serialize(func))

    def serialize_classmethod(self, obj: classmethod):
        func = obj.__func__
        return self.basic.format(type="classmethod", val=self.serialize(func))
    
    def serialize_property(self, obj: property):
        tpl = obj.fget, obj.fset, obj.fdel
        return self.basic.format(type="property", val=self.serialize(tpl))

    def serialize_none(self):
        if self.__mode == "json":
            return self.basic.format(type="none", val="{}")
        else:
            return self.basic.format(type="none", val="")

    def serialize_type(self, obj: type) -> str:
        dct = self.type_to_dict(obj)

        return self.basic.format(type="type", val=self.dict_to_obj(dct))
    
    def serialize_module(self, obj):
        val_dict = {}
        line = str(obj)
        srch = re.search(r"\\\\", line)
        if srch is None:
            val_dict["path"] = "basic"
        else:
            val_dict["path"] = re.search(r"from \'(.*)\'", line).group(1)

        val_dict["name"] = re.search(r"module \'([^\']*)\'", line).group(1)

        return self.basic.format(type="module", val=self.dict_to_obj(val_dict))

    def serialize_tuple(self, obj):
        val = ""
        for it in obj:
            val += self.serialize(it)
            if self.__mode == "json":
                val += ", "
            else:
                val += " "

        if self.__mode == "json":
            val = val[:-2]
            val = "[" + val + "]"
        return self.basic.format(type="tuple", val=val)

    def serialize_set(self, obj):
        val = ""
        for it in obj:
            val += self.serialize(it)
            if self.__mode == "json":
                val += ", "
            else:
                val += " "
        if self.__mode == "json":
            val = val[:-2]
            val = "[" + val + "]"
        return self.basic.format(type="set", val=val)
    
    def serialize_bool(self, obj) -> str:
        return self.basic.format(type="bool", val=str(obj).lower())

    def serialize_int(self, obj) -> str:
        return self.basic.format(type="int", val=str(obj))

    def serialize_float(self, obj) -> str:
        return self.basic.format(type="float", val=str(obj))

    def serialize_string(self, obj) -> str:
        return self.basic.format(type="str", val='"' + self.__shield_str(obj) + '"')

    def serialize_dict_xml(self, obj: dict) -> str:
        val = ""
        form = "<keyval> {key} {val} </keyval> "
        for k, v in obj.items():
            val += form.format(
                key=self.__add_attribute(self.serialize(k), "key", "key"),
                val=self.__add_attribute(self.serialize(v), "key", "value"),
            )

        return self.basic.format(type="dict", val=val)

    def serialize_dict(self, obj: dict) -> str:
        if self.__mode != "json":
            return self.serialize_dict_xml(obj)
        val = "["
        for it in obj.items():
            val += (
                '{ "key": '
                + self.serialize(it[0])
                + ', "value": '
                + self.serialize(it[1])
                + "}, "
            )

        val = val[:-2] + "]"
        if val == "]":
            val = "[]"
        return self.basic.format(type="dict", val=val)

    def serialize_list(self, obj):
        val = ""
        for it in obj:
            val += self.serialize(it)
            if self.__mode == "json":
                val += ", "
            else:
                val += " "
        if self.__mode == "json":
            val = val[:-2:]
            val = "[" + val + "]"
        return self.basic.format(type="list", val=val)

    def serialize_bytes(self, obj: bytes):
        lst = list(obj)
        val = str(lst)
        if self.__mode != "json":
            val = val[1:-1]
        return self.basic.format(type="bytes", val=val)

    def serialize_code(self, obj: types.CodeType):
        tpl = (
            obj.co_argcount,
            obj.co_posonlyargcount,
            obj.co_kwonlyargcount,
            obj.co_nlocals,
            obj.co_stacksize,
            obj.co_flags,
            obj.co_code,
            obj.co_consts,
            obj.co_names,
            obj.co_varnames,
            "",
            obj.co_name,
            obj.co_qualname,
            obj.co_firstlineno,
            obj.co_linetable,
            obj.co_exceptiontable,
            obj.co_freevars,
            obj.co_cellvars,
        )
        # types.CodeType()
        # tpl = {
        #     "__argcount": obj.co_argcount,
        #     "__posonlyargcount": obj.co_posonlyargcount,
        #     "__kwonlyargcount": obj.co_kwonlyargcount,
        #     "__nlocals": obj.co_nlocals,
        #     "__stacksize": obj.co_stacksize,
        #     "__flags": obj.co_flags,
        #     "__codestring": obj.co_code,
        #     "__constants": obj.co_consts,
        #     "__names": obj.co_names,
        #     "__varnames": obj.co_varnames,
        #     "__filename": "",
        #     "__name": obj.co_name,
        #     "__firstlineno": obj.co_firstlineno,
        #     "__linetable": obj.co_linetable,
        #     "__freevars": obj.co_freevars,
        #     "__cellvars": obj.co_cellvars,
        # }
        value = self.serialize(tpl)
        return self.basic.format(val=value, type="code")

    def serialize_func(self, obj: types.FunctionType):
        info = inspect.getclosurevars(obj)
        val_dict = {}

        gl_dict = dict(info.globals)
        for k,v in gl_dict.items():
            if k == obj.__name__:
                gl_dict[k] = obj.__name__
                break
            
        val_dict["globals"] = gl_dict
        val_dict["argdefs"] = inspect.getfullargspec(obj).defaults

        cl_arr = []
        for k, v in info.nonlocals.items():
            if v.__name__ == obj.__name__:
                v = v.__name__
            cl_arr.append(v)

        val_dict["closure"] = tuple(cl_arr)
        val_dict["name"] = [
            val for key, val in inspect.getmembers(obj) if key == "__name__"
        ][0]

        val_dict["code"] = obj.__code__

        return self.basic.format(type="function", val=self.dict_to_obj(val_dict))
    
    def serialize_object(self, obj) -> str:
        type_dict = self.type_to_dict(type(obj))
        # print(obj)
        val = obj.__dict__
        val["type properties"] = type_dict

        return self.basic.format(type="object", val=self.dict_to_obj(val))
    
    def serialize(self, obj):
        default_types = [
            int,
            str,
            bool,
            dict,
            tuple,
            float,
            list,
            set,
            bool,
            type,
            types.FunctionType,
            types.ModuleType,
            type,
            types.CodeType,
            bytes,
            property,
            classmethod,
            staticmethod,
            types.MethodType,
            types.BuiltinFunctionType,
        ]
        res = ""
        if type(obj) in default_types:
            res = self.basic_serailize(obj)
        elif type(obj) is not types.NoneType:
            res = self.serialize_object(obj)
        else:
            res = self.serialize_none()

        if self.__mode == "json":
            return "{" + res + "}"
        return res

    def basic_serailize(self, obj) -> str:
        # int, float, string, dict, tuple, list, set, type, bool, function
        if type(obj) == bool:
            return self.serialize_bool(obj)
        elif type(obj) == int:
            return self.serialize_int(obj)
        elif type(obj) == float:
            return self.serialize_float(obj)
        elif type(obj) == str:
            return self.serialize_string(obj)
        elif type(obj) == dict:
            return self.serialize_dict(obj)
        elif type(obj) == list:
            return self.serialize_list(obj)
        elif type(obj) == set:
            return self.serialize_set(obj)
        elif type(obj) == tuple:
            return self.serialize_tuple(obj)
        elif type(obj) == types.FunctionType:
            return self.serialize_func(obj)
        elif type(obj) == type:
            return self.serialize_type(obj)
        elif type(obj) == types.CodeType:
            return self.serialize_code(obj)
        elif type(obj) == bytes:
            return self.serialize_bytes(obj)
        elif type(obj) == property:
            return self.serialize_property(obj)
        elif type(obj) == staticmethod:
            return self.serialize_staticmethod(obj)
        elif type(obj) == classmethod:
            return self.serialize_classmethod(obj)
        elif type(obj) == types.ModuleType:
            return self.serialize_module(obj)
        elif type(obj) == types.MethodType:
            return self.serialize_method(obj)
        elif type(obj) == types.BuiltinFunctionType:
            return self.serialize_builtin_function(obj)
        else:
            return self.serialize_none()

    # возвращает кортеж для среза скобок
    @staticmethod
    def parse_brackets(text: str, is_figure: bool) -> tuple[int, int]:
        begin = -1
        end = -1
        count = 0
        bracket = r"[]"
        if is_figure:
            bracket = r"{}"
        flag = False
        for n, ch in enumerate(text):
            if ch == '"' and text[n - 1] != "\\":
                flag = not flag
            if ch == bracket[0] and not flag:
                count += 1
                if begin == -1:
                    begin = n
            if ch == bracket[1] and not flag:
                count -= 1
                if count == 0:
                    end = n + 1
                    break

        return begin, end

    @staticmethod
    def parse_quotes(txt) -> tuple[int, int]:
        begin = -1
        end = -1
        flag = True
        for n, ch in enumerate(txt):
            if ch == '"' and (txt[n - 1] != "\\" or n == 0):
                if begin == -1:
                    begin = n
                else:
                    end = n + 1
                    break

        return begin, end

    @classmethod
    def find_value(cls, txt: str) -> tuple[int, int]:
        first_symb = re.search(r"[^\s:]", txt)
        val: str = ""
        if txt[first_symb.start()] == '"':
            beg, end = cls.parse_quotes(txt)
            return beg, end

        elif txt[first_symb.start()] == "[":
            return cls.parse_brackets(txt, False)

        elif txt[first_symb.start()] == "{":
            return cls.parse_brackets(txt, True)

        else:
            return re.search(r"[^\s:}]+", txt).span()

    def parse_to_kv(self, txt: str) -> dict:
        d = {}
        if self.__mode == "xml":
            while True:
                beg, end = self.parse_xml_tag(txt)
                if beg == -1:
                    return d
                obj = txt[beg:end]
                key = re.search(r'key\s*=\s*"([^"]*)"', obj).group(1)
                d[key] = obj
                txt = txt[end::]
        else:
            while True:
                key_match = re.search(r'"[^"]*"', txt)
                if not key_match:
                    break
                key = txt[key_match.start() + 1 : key_match.end() - 1]
                txt = txt[key_match.end() : :]
                val_tpl = self.find_value(txt)
                d[key] = txt[val_tpl[0] : val_tpl[1]]
                txt = txt[val_tpl[1] : :]

        return d

    def parse_xml_to_tv(self, txt):
        reg = r"<\s*(\w+)[^>]*>"
        mtch = re.search(reg, txt)
        tagname = mtch.group(1)
        beg1, val_beg = mtch.span()

        cltag = r"<\s*/\s*" + tagname + r"[^>]*>"
        optag = r"<\s*" + tagname + r"[^>]*>"
        thing = r"(?:" + optag + "|" + cltag + ")"

        count = 0
        val_end = val_beg

        mtchs = re.finditer(thing, txt)
        for mtch in mtchs:
            if re.match(optag, mtch.group(0)):
                count += 1
            else:
                count -= 1
            if count == 0:
                val_end = mtch.span()[0]
                break

        return tagname, txt[val_beg:val_end]

    def parse_xml_tag(self, txt) -> tuple[int, int]:
        reg = r"<\s*(\w+)[^>]*>"
        mtch = re.search(reg, txt)
        if not mtch:
            return -1, -1
        tagname = mtch.group(1)
        beg, end = mtch.span()

        cltag = r"<\s*/\s*" + tagname + r"[^>]*>"
        optag = r"<\s*" + tagname + r"[^>]*>"
        thing = r"(?:" + optag + "|" + cltag + ")"

        count = 0
        mtchs = re.finditer(thing, txt)
        for mtch in mtchs:
            if re.match(optag, mtch.group(0)):
                count += 1
            else:
                count -= 1
            if count == 0:
                end = mtch.span()[1]
                break

        return (beg, end)

    def get_type_value(self, txt: str) -> str:
        if self.__mode == "json":
            kv = self.parse_to_kv(txt)
            return kv["type"][1:-1], kv["value"]
        else:
            return self.parse_xml_to_tv(txt)

    def parse_object(self, txt) -> str:
        if self.__mode == "json":
            return self.parse_brackets(txt, True)
        else:
            return self.parse_xml_tag(txt)

    def gap_func(self, string: str):
        out_string: str = ""
        indent: int = 4
        opened_brackets: int = 0
        i: int = 0

        while i < len(string):
            if string[i] == "{" and string[i + 1] != "}":
                if string[i + 1] == " ":
                    out_string += string[i] + "\n" + " " * (indent - 1)
                else:
                    out_string += string[i] + "\n" + " " * indent
                opened_brackets += 1
                out_string += " " * indent * (opened_brackets - 1)
            elif string[i] == ":" and string[i + 2] == "{" and string[i + 3] != "}":
                out_string += string[i] + "\n" + " " * indent * opened_brackets
                i += 1
            elif string[i] == "}" and string[i - 1] != "{":
                opened_brackets -= 1
                out_string += "\n" + " " * indent * opened_brackets + string[i]
            elif string[i] == ",":
                out_string += string[i] + "\n" + " " * indent * opened_brackets
                i += 1
            else:
                out_string += string[i]
            i += 1

        return out_string

    @staticmethod
    def __shield_str(txt: str) -> str:
        txt = txt.replace("\\", "\\\\")
        txt = txt.replace('"', '\\"')
        txt = txt.replace("'", "\\'")
        txt = txt.replace("\n", "\\n")
        txt = txt.replace("\t", "\\t")

        return txt

    @staticmethod
    def deshield_str(txt: str) -> str:
        txt = txt.replace("\\t", "\t")
        txt = txt.replace("\\n", "\n")
        txt = txt.replace('\\"', '"')
        txt = txt.replace("\\'", "'")
        txt = txt.replace("\\\\", "\\")

        return txt
    
    @staticmethod
    def __add_attribute(txt: str, attr_name: str, attr_val: str) -> str:
        reg = r"<\s*\w+\s*>"
        beg, end = re.search(reg, txt).span()
        txt = txt[: end - 1 :] + f' {attr_name}="{attr_val}"' + txt[end - 1 : :]

        return txt

    def change_indent(src: str) -> str:
        while src[:3] != "def":
            src = src.replace("    def", "def", 1)
            src = src.replace("\n    ", "\n")

        return src
    
    def basic_deserialize(self, kv):
        t = kv["type"]
        v = kv["value"]

        if t == "str":
            return self.deserialize_string(v)
        elif t == "int":
            return self.deserialize_int(v)
        elif t == "bool":
            return self.deserialize_bool(v)
        elif t == "float":
            return self.deserialize_float(v)
        elif t == "tuple":
            return self.deserialize_tuple(v)
        elif t == "list":
            return self.deserialize_list(v)
        elif t == "set":
            return self.deseialize_set(v)
        elif t == "dict":
            return self.deserialize_dict(v)
        elif t == "function":
            return self.deserialize_function(v)
        elif t == "module":
            return self.deserialize_module(v)
        elif t == "type":
            return self.deserialize_type(v)
        elif t == "code":
            return self.deserialize_code(v)
        elif t == "bytes":
            return self.deserialize_bytes(v)
        elif t == "property":
            return self.deserialize_property(v)
        elif t == "staticmethod":
            return self.deserialize_staticmethod(v)
        elif t == "classmethod":
            return self.deserialize_classmethod(v)
        elif t == "method":
            return self.deserialize_method(v)
        elif t == "builtinfunction":
            return self.deserialize_builtin_function(v)
        elif t == "none":
            return None

    def deserialize(self, txt: str):
        basic_types = {
            "str",
            "dict",
            "tuple",
            "function",
            "bool",
            "set",
            "int",
            "float",
            "type",
            "list",
            "function",
            "module",
            "type",
            "none",
            "code",
            "bytes",
            "property",
            "classmethod",
            "staticmethod",
            "method",
            "builtinfunction",
        }
        tpl = self.get_type_value(txt)
        kv = {"type": tpl[0], "value": tpl[1]}
        if kv["type"] in basic_types:
            return self.basic_deserialize(kv)
        else:
            return self.deserialize_object(kv)

    def deserialize_builtin_function(self, val):
        st = self.deserialize(val)

        thing = __builtins__
        if not isinstance(thing, dict):
            thing = thing.__dict__

        for k, v in thing.items():
            if k == st:
                return v

    def deserialize_method(self, val):
        tpl = self.deserialize(val)

        return types.MethodType(*tpl)

    def deserialize_classmethod(self, val):
        f = self.deserialize(val)
        return classmethod(f)

    def deserialize_staticmethod(self, val):
        f = self.deserialize(val)
        return staticmethod(f)

    def deserialize_property(self, val):
        tpl = self.deserialize(val)
        return property(*tpl)

    def deserialize_bytes(self, val):
        reg = r"\d+"
        mtchs = re.findall(reg, val)

        lst = []
        for it in mtchs:
            lst.append(int(it))

        return bytes(lst)

    def deserialize_code(self, val):
        tpl = self.deserialize(val)

        return types.CodeType(*tpl)

    def deserialize_type(self, val):
        kv = self.parse_to_kv(val)
        if kv.get("builtin type") is not None:
            v = self.deserialize(kv["builtin type"])

            thing = __builtins__
            if not isinstance(thing, dict):
                thing = thing.__dict__

            for bk, bv in thing.items():
                if bk == v:
                    return bv

        for k, v in kv.items():
            kv[k] = self.deserialize(v)
        name = kv.pop("__name__")
        parents = kv.pop("parents")
        return type(name, parents, kv)

    def deserialize_module(self, val):
        global mod_ind
        kv = self.parse_to_kv(val)
        if kv["path"] != "basic":
            sys.path.insert(mod_ind, self.deserialize(kv["path"]))
            mod_ind += 1

        return importlib.import_module(self.deserialize(kv["name"]))

    def deserialize_function(self, val):
        kv = self.parse_to_kv(val)
        dct = {}
        for k, v in kv.items():
            dct[k] = self.deserialize(v)

        arr = []
        for it in dct['closure']:
            arr.append(types.CellType(it))

        dct["closure"] = tuple(arr)

        func = types.FunctionType(**dct)


        if func.__globals__.get(func.__name__):
            func.__globals__.update({func.__name__:func})

        return func

    def deserialize_string(self, val) -> str:
        if self.__mode == "json":
            return self.deshield_str(val[1:-1])
        else:
            return self.deshield_str(val[2:-2])

    def deserialize_int(self, val) -> int:
        return int(val)

    def deserialize_bool(self, val) -> bool:
        if self.__mode == "xml":
            val = val[1:-1]
        return val == "true"

    def deserialize_float(self, val) -> float:
        return float(val)

    def deserialize_tuple(self, val) -> tuple:
        lst = []

        while True:
            tpl = self.parse_object(val)
            if tpl[0] == -1:
                break
            lst.append(self.deserialize(val[tpl[0] : tpl[1]]))
            val = val[tpl[1] : :]

        return tuple(lst)

    def deserialize_list(self, val) -> list:
        lst = []

        while True:
            tpl = self.parse_object(val)
            if tpl[0] == -1:
                break
            lst.append(self.deserialize(val[tpl[0] : tpl[1]]))
            val = val[tpl[1] : :]

        return lst

    def deseialize_set(self, val) -> set:
        lst = []

        while True:
            tpl = self.parse_object(val)
            if tpl[0] == -1:
                break
            lst.append(self.deserialize(val[tpl[0] : tpl[1]]))
            val = val[tpl[1] : :]

        return set(lst)

    def deserialize_dict(self, val) -> dict:
        d = {}

        while True:
            tpl = self.parse_object(val)
            if tpl[0] == -1:
                break
            txt = val[tpl[0] : tpl[1]]
            if self.__mode == "xml":
                txt = self.parse_xml_to_tv(txt)[1]

            kv = self.parse_to_kv(txt)
            key = self.deserialize(kv["key"])
            value = self.deserialize(kv["value"])
            d[key] = value
            val = val[tpl[1] : :]

        return d

    def deserialize_object(self, kv) -> str:
        val_kv = self.parse_to_kv(kv["value"])
        type_kv = val_kv.pop("type properties")
        type_kv = self.deserialize(type_kv)

        parents = type_kv.pop("parents")
        name = type_kv.pop("__name__")
        typ = type(name, parents, type_kv)

        obj = typ.__new__(typ)

        for k, v in val_kv.items():
            val_kv[k] = self.deserialize(v)

        obj.__dict__ = val_kv

        return obj        