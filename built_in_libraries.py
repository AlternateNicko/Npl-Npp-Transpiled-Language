# Npp.libraries
import os
import sys
sys.path.append("Npp")
from npp import NPP

t, m, r, sys, json = None, None, None, None, None
class libraries:
    def __init__(self, lib, lib_name, var, line, cnt, classes):
        self.libraries = ["math", "files", "random", "sys", "time", "smart", "os"]
        self.library_name = lib_name
        self.library = lib
        self.line = line # main line to parse
        if isinstance(line, tuple):
            line = line[0] + line[1]
        npp = NPP(line)
        self.npp = npp
        self.cnt = cnt
        self.eval = npp.eval
        self.special_split = npp.special_split
        self.variables = var
        self.classes = classes
        self.attempt = False
        self.Errors = { # all of the errors that will show up, if one of this is True, the whole code is stop and prints a trace back where the error originated,
            'SyntaxError': False,
            'IndexError': False,
            'RecursionError': False,
            'NameError': False,
            'ZeroDivisionError': False,
            'TypeError': False,
            'KeyError': False,
            'MemoryError': False,
            'ValueError': False,
            'ModuleError': False,
            'QuitError': False
        }
    
    def process(self, line, ti, ma, ra, jsn, syss, variant="va"):
        global t, m, r, sys, json
        t = ti
        m = ma
        r = ra
        json = jsn
        sys = syss
        if variant == "va":
            res = self.assign_variables(variant)
            return tuple([self.variables])
        else:
            res = self.one_line(variant)
    
    def one_line(self, var):
        global t, m, json, sys, r
        if var == "ol":
            instruction = self.line
            try:
                if "time" in self.library and instruction.startswith(self.library_name["time"] + "."):
                    man = self.special_split(instruction, ".", ("'", '"'), ("'", '"'))[1]
                    if man.startswith("sleep(") and man.endswith(")"):
                        args = man[6:-1].strip()
                        val = self.eval(args, {}, self.variables)
                        t.sleep(val)
                if "files" in self.library and instruction.startswith(self.library_name["files"] + "."):
                    man = self.special_split(instruction, ".", ("'", '"'), ("'", '"'))[1]
                    if man.startswith("dump(") and man.endswith(")"):
                        args = man[5:-1].strip().split(",")
                        file = self.eval(args[1].strip(), {}, self.variables)
                        dictionary = self.eval(args[0], {}, self.variables)
                        try:
                            json.dump(dictionary, file)
                        except Exception as e:
                            if not self.attempt:
                                print("Traceback(most_recent_call_back):")
                                for i in self.traceback:
                                    print(f"    TB - [ File `<string>` line: {self.traceback[i]}, in {i} ],")
                                    print(f"    TB - [ File `<string>` TB found > line: {self.og_c} in {i} ]")
                                    print(f"\nValueError: value type of `{file}` is not a file type")
                                    self.Errors["ValueError"] = True
                                return None
                            
                if "sys" in self.library and instruction.startswith(self.library_name["sys"] + "."):
                    man = self.special_split(instruction, ".", ("'", '"'), ("'", '"'))[1]
                    if man.startswith("jump(") and man.endswith(")"):
                        args = man[5:-1].strip()
                        value = self.eval(args, {}, self.variables)
                        if not isinstance(value, int):
                            if not self.attempt:
                                print("Traceback(most_recent_call_back):")
                                for i in self.traceback:
                                    print(f"    TB - [ File `<string>` line: {self.traceback[i]}, in {i} ],")
                                    print(f"    TB - [ File `<string>` TB found > line: {self.og_c} in {i} ]")
                                    print(f"\nTypeError: sys.jump() expects argument `{args}` to be an int, but got `{type(value)}` instead")
                                    self.Errors["TypeError"] = True
                                return None
                        self.cnt = value
                    elif man.startswith("clear_term(") and man.endswith(")"):
                        print("\033c", end="")
                    elif man.startswith("stdwrite(") and man.endswith(")"):
                        args = self.eval(man[9:-1].strip(), {}, self.variables)
                        sys.stdout.write(args)
                    elif man.startswith("stderr(") and man.endswith(")"):
                        args = self.eval(man[7:-1].strip(), {}, self.variables)
                        sys.stderr.write(args)
                    elif man.startswith("setrecursionlimit(") and man.endswith(")"):
                        args = self.eval(man[18:-1].strip(), {}, self.variables)
                        sys.setrecursionlimit(args)
                    elif man.startswith("exit(") and man.endswith(")"):
                        args = self.eval(man[5:-1].strip(), {}, self.variables)
                        sys.exit(args + "\n")
                    elif man.startswith("attempt(") and man.endswith(")"):
                        self.attempt = not self.attempt
                return (self.variables, self.cnt)
            except Exception as e:
                print(e)
    def assign_variables(self, var):
        global t, m, r, json, sys
        if var == "va":
            inst = self.line
            left = inst[0]
            right = inst[1]
            libs = False
            if "math" in self.library and right.startswith(self.library_name["math"] + "."):
                man = self.special_split(right, ".", ("'", '"'), ("'", '"'))[1]
                # constants
                if man.startswith("pi"):
                    self.variables[left] = m.pi
                elif man.startswith("e"):
                    self.variables[left] = m.e
                elif man.startswith("tau"):
                    self.variables[left] = m.tau
                elif man.startswith("inf"):
                    self.variables[left] = m.inf
                elif man.startswith("nan"):
                    self.variables[left] = m.nan
                # functions and methods
                elif man.startswith("ceil(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.ceil(a)
                elif man.startswith("floor(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.floor(a)
                elif man.startswith("trunc(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.trunc(a)
                elif man.startswith("factorial(") and man.endswith(")"):
                    args = man[10:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.factorial(a)
                elif man.startswith("fabs(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.fabs(a)
                elif man.startswith("fmod(") and man.endswith(")"):
                    args = man[5:-1].strip().strip(",")
                    a = self.eval(args[0], {}, self.variables)
                    b = self.eval(args[1], {}, self.variables)
                    self.variables[left] = m.fmod(a, b)
                elif man.startswith("remainder(") and man.endswith(")"):
                    args = man[10:-1].strip().strip(",")
                    a = self.eval(args[0], {}, self.variables)
                    b = self.eval(args[1], {}, self.variables)
                    self.variables[left] = m.remainder(a, b)
                elif man.startswith("modf(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.modf(a)
                elif man.startswith("copysign(") and man.endswith(")"):
                    args = man[9:-1].strip().strip(",")
                    a = self.eval(args[0], {}, self.variables)
                    b = self.eval(args[1], {}, self.variables)
                    self.variables[left] = m.copysign(a, b)
                elif man.startswith("exp(") and man.endswith(")"):
                    args = man[4:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.exp(a)
                elif man.startswith("log(") and man.endswith(")"):
                    args = man[4:-1].strip().strip(",")
                    a = self.eval(args[0], {}, self.variables)
                    if len(args) > 1:
                        b = self.eval(args[1], {}, self.variables)
                    else:
                        b = m.e
                    self.variables[left] = m.log(a, b)
                elif man.startswith("log10(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.log10(a)
                elif man.startswith("log2(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.log2(a)
                elif man.startswith("sqrt(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.sqrt(a)
                elif man.startswith("cbrt(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.cbrt(a)
                elif man.startswith("sin(") and man.endswith(")"):
                    args = man[4:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.sin(a)
                elif man.startswith("cos(") and man.endswith(")"):
                    args = man[4:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.cos(a)
                elif man.startswith("tan(") and man.endswith(")"):
                    args = man[4:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.tan(a)
                elif man.startswith("asin(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.asin(a)
                elif man.startswith("acos(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.acos(a)
                elif man.startswith("atan(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.atan(a)
                elif man.startswith("degrees(") and man.endswith(")"):
                    args = man[8:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.degrees(a)
                elif man.startswith("radians(") and man.endswith(")"):
                    args = man[8:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.radians(a)
                elif man.startswith("sinh(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.sinh(a)
                elif man.startswith("cosh(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.cosh(a)
                elif man.startswith("tanh(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.tanh(a)
                elif man.startswith("asinh(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.asinh(a)
                elif man.startswith("acosh(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.acosh(a)
                elif man.startswith("atanh(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.atanh(a)
                elif man.startswith("erf(") and man.endswith(")"):
                    args = man[4:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.erf(a)
                elif man.startswith("gamma(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.gamma(a)
                elif man.startswith("isfinite(") and man.endswith(")"):
                    args = man[9:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.isfinite(a)
                elif man.startswith("isinf(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.isinf(a)
                elif man.startswith("isnan(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.isnan(a)
                elif man.startswith("fsum(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    a = self.eval(args, {}, self.variables)
                    self.variables[left] = m.fsum(a)
                elif man.startswith("prod(") and man.endswith(")"):
                    args = man[6:-1].strip().strip(",")
                    a = self.eval(args[0], {}, self.variables)
                    if len(args) > 1:
                        b = self.eval(args[1], {}, self.variables)
                    else:
                        b = 1
                    self.variables[left] = m.prod(a, b)
                elif man.startswith("dist(") and man.endswith(")"):
                    args = man[5:-1].strip().strip(",")
                    a = self.eval(args[0], {}, self.variables)
                    b = self.eval(args[1], {}, self.variables)
                    self.variables[left] = m.dist(a, b)
                return tuple([self.variables])
            if "random" in self.library and right.startswith(self.library_name["random"] + "."):
                man = self.special_split(right, ".", ("'", '"'), ("'", '"'))[1]
                if man.startswith("randint(") and man.endswith(")"):
                    libs = True
                    arg = man[8:-1].split(",")
                    arg = [self.eval(a.strip(), {}, self.variables) for a in arg]
                    if not isinstance(arg[0], int) or not isinstance(arg[1], int):
                        if not self.attempt:
                            print("Traceback(most_recent_call_back):")
                            for i in self.traceback:
                                print(f"    TB - [ File `<string>` line: {self.traceback[i]}, in {i} ],")
                            print(f"    TB - [ File `<string>` TB found > line: {self.og_c} in {i} ]")
                            print(f"\nTypeError: randint() method expects interger arguments, not {type(arg[0])}, {type(arg[1])}")
                        self.Errors["TypeError"] = True
                        return None
                    self.variables[left] = r.randint(arg[0], arg[1])
                elif man.startswith("choice(") and man.endswith(")"):
                    libs = True
                    arg = self.eval(man[7:-1].strip(), {}, self.variables)
                    if not isinstance(arg[0], int) or not isinstance(arg[1], int):
                        if not self.attempt:
                            print("Traceback(most_recent_call_back):")
                            for i in self.traceback:
                                print(f"    TB - [ File `<string>` line: {self.traceback[i]}, in {i} ],")
                            print(f"    TB - [ File `<string>` TB found > line: {self.og_c} in {i} ]")
                            print(f"\nTypeError: choice() method expects list or dict arguments, not {type(arg)}")
                        self.Errors["TypeError"] = True
                        return None
                    self.variables[left] = r.choice(arg)
                elif man.startswith("num(") and man.endswith(")"):
                    libs = True
                    if man[4:-1] == "":
                        arg = 10
                    else: arg = self.eval(man[4:-1].strip(), {}, self.variables) * 10
                    self.variables[left] = r.randint(1, arg) / 10
                elif man.startswith("shuffle(") and man.endswith(")"):
                    args = man[8:-1].strip()
                    value = self.eval(args, {}, self.variables)
                    r.shuffle(value)
                    self.variables[left] = value
                elif man.startswith("random(") and man.endswith(")"):
                    args = man[7:-1].strip()
                    self.variables[left] = r.random()
                elif man.startswith("uniform(") and man.endswith(")"):
                    args = man[8:-1].strip()
                    args = self.special_split(args, ",", ("'", '"'), ("'", '"'))
                    a = self.eval(args[0], {}, self.variables)
                    b = self.eval(args[1], {}, self.variables)
                    self.variables[left] = r.uniform(a, b)
                    
                return tuple([self.variables])
                
            if "time" in self.library and right.startswith(self.library_name["time"] + "."):
                man = self.special_split(right, ".", ("'", '"'), ("'", '"'))[1]
                if man.startswith("time(") and man.endswith(")"):
                    self.variables[left] = t.time()
                elif man.startswith("time_ns(") and man.endswith(")"):
                    self.variables[left] = t.time_ns()
                elif man.startswith("monotonic(") and man.endswith(")"):
                    self.variables[left] = t.monotonic()
                elif man.startswith("monotonic_ns(") and man.endswith(")"):
                    self.variables[left] = t.monotonic_ns()
                elif man.startswith("counter(") and man.endswith(")"):
                    self.variables[left] = t.perf_counter()
                elif man.startswith("counter_ns(") and man.endswith(")"):
                    self.variables[left] = t.perf_counter_ns()
                elif man.startswith("asctime(") and man.endswith(")"):
                    args = man[8:-1].strip()
                    try:
                        value = self.eval(args, {}, self.variables)
                    except Exception:
                        self.variables[left] = t.asctime()
                        return
                    if value is None:
                        value = ""
                    self.variables[left] = t.asctime(value)
                elif man.startswith("localtime(") and man.endswith(")"):
                    args = man[10:-1].strip()
                    try:
                        value = self.eval(args, {}, self.variables)
                    except Exception:
                        self.variables[left] = t.localtime()
                        return
                    self.variables[left] = t.localtime(value)
                elif man.startswith("ctime(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    try:
                        value = self.eval(args, {}, self.variables)
                    except Exception:
                        self.variables[left] = t.ctime()
                        return
                    self.variables[left] = t.ctime(value)
                elif man.startswith("strftime(") and man.endswith(")"):
                    args = man[9:-1].strip().split(",")
                    format = args[0]
                    t_tuple = self.eval(args[1], {}, self.variables)
                    self.variables[left] = t.strftime(format, t_tuple)
                elif man.startswith("strptime"):
                    args = man[9:-1].strip().split(",")
                    string = self.eval(args[0], {}, self.variables)
                    format = args[1]
                    self.variables[left] = t.strptime(string, format)
                return tuple([self.variables])
            if "smart" in self.library and right.startswith(self.library_name["smart"] + "."):
                man = self.special_split(right, ".", ("'", '"'), ("'", '"'))[1]
                if man.startswith("split(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    args = self.special_split(args, ",", ("'", '"'), ("'", '"'))
                    # args is smart.split(string, split_ch, in_char1, in_char2)
                    # uses special_split()
                    string = self.eval(args[0].strip(), {}, self.variables)
                    if string is None: # any type of None values
                        string = " " # defaults to space
                    split_ch = self.eval(args[1].strip(), {}, self.variables)
                    # arguments of in_char can be string, or list, or tuples
                    in_char1 = self.eval(args[2].strip(), {}, self.variables)
                    in_char2 = self.eval(args[3].strip(), {}, self.variables)
                    self.variables[left] = self.special_split(string, split_ch, in_char1, in_char2)
                elif man.startswith("strip(") and man.endswith(")"):
                    # strips an string but with conditions
                    # strip(string, strip_string, cond="")
                    # 4 conditions
                    args = man[6:-1].strip()
                    args = self.special_split(args, ",", ("'", '"', "("), ("'", '"', ")"))
                    string = self.eval(args[0].strip(), {}, self.variables)
                    strip_str = self.eval(args[1].strip(), {}, self.variables)
                    cond = self.eval(args[3].strip(), {}, self.variables)
                    pass
                return tuple([self.variables])
            if "sys" in self.library and right.startswith(self.library_name["sys"] + "."):
                man = self.special_split(right, ".", ("'", '"'), ("'", '"'))[1]
                if man.startswith("cnt"):
                    self.variables[left] = self.cnt
                elif man.startswith("variables"):
                    self.variables[left] = self.variables.copy()
                elif man.startswith("load_var(") and man.endswith(")"):
                    args = man[9:-1].strip()
                    value = self.eval(args, {}, self.variables)
                    self.variables[left] = self.variables[value]
                elif man.startswith("stdinp()"):
                    self.variables[left] = sys.stdin.readline().strip()
                elif man.startswith("get."):
                    args = man[4:].strip()
                    if args.startswith("recursionlimit"):
                        self.variables[left] = sys.getrecursionlimit()
                    elif args.startswith("sizeof(") and args.endswith(")"):
                        arg = self.eval(args[7:-1].strip(), {}, self.variables())
                        self.variables[left] = sys.getsizeof(arg)
                    elif args.startswith("maxsize"):
                        self.variables[left] = sys.maxsize
                elif man.startswith("version"):
                    self.variables[left] = self.version
                elif man.startswith("platform"):
                    self.variables[left] = sys.platform
                elif man.startswith("sync_variables"):
                    self.variables[left] = self.sync_variables.copy()
                elif man.startswith("classes"):
                    self.variables[left] = self.classes
                return tuple([self.variables])
            if "files" in self.library and right.startswith(self.library_name["files"] + "."):
                man = self.special_split(right, ".", ("'", '"'), ("'", '"'))[1]
                if man.startswith("load(") and man.endswith(")"):
                    args = man[5:-1].strip()
                    value = self.eval(args, {}, self.variables)
                    self.variables[left] = json.load(value)
                elif man.startswith("dumps(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    value = self.eval(args, {}, self.variables)
                    self.variables[left] = json.dumps(value)
                elif man.startswith("loads(") and man.endswith(")"):
                    args = man[6:-1].strip()
                    value = self.eval(args, {}, self.variables)
                    self.variables[left] = json.loads(value)      
                return tuple([self.variables])