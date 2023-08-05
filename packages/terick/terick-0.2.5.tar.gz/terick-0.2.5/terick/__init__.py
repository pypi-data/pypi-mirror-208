import zipfile as zip
import os
import random
import time

# ----====[ Text Tricks ]====----


# --- bar v1.1
def bar(percent, lenght=100, chars="#_"):
    amount = int( percent/(100/lenght) )
    return ((chars[0]*amount) + (chars[1]*(lenght-amount)))

# --- unlist words v1.0
def unlist_words(list:list):
    result = ""

    for word in list:
        if len(result)>0: result += " "
        result += str(word)

    return result

# --- list lines v1.1
def list_lines(text:int, keep_enter=False):
    result = []
    sentence = ""

    for char in text:
        if char=="\n":
            if keep_enter: sentence += char
            result.append(sentence)
            sentence = ""

        else:
            sentence += char

    if len(sentence)>0: result.append(sentence)
    return result


# --- vanish character v1.1
def vanish_char(text:str, chars:str):
    result = ""
    for ch in text:
        if ch not in chars: result += ch
    return result

# --- better int v1.0
def interize(text:str):
    result = ""
    for char in text:
        if char in "1234567890": result += char
    return int(result)

# --- toggle bool v1.0
def toggle(var:bool):
    if var: return False
    else: return True

# --- unit 1.0
def short_num(number:float):
    units = "KMBT"
    for u in units:
        if number>=1000:
            number = int(number/1000)
            if number<1000: return str(number)+u
        else: return str(number)
    return str(number)+units[-1]

# --- string limit v1.0
def limit_str(text:str, max:int):
    result = ""
    if len(text)<max: return text

    for i in range(0, max):
        result += text[i]
    return result

# --- text_align v1.1
def text_align(text:str, lenght:int, align="center"):
    text = limit_str(text, lenght)
    if align in ["left", "l"]: return text + " "*(lenght-len(text))
    if align in ["right", "r"]: return " "*(lenght-len(text)) + text
    else: 
        gap = (lenght-len(text))/2
        result = " "*int(gap) + text
        if int(gap)==gap: result += " "*int(gap)
        else: result += " "*(int(gap)+1)
        return result

# --- into str v1.0
def into_str(into:str, obj:str, x:int):
    result = ""
    index = 0

    for i in range(0, len(into)):
        if (i>=x) and (index<len(obj)):
            result += obj[index]
            index += 1
        else:
            result += into[i]
    
    return result

# --- divide time v1.0
def div_time(seconds:float, as_text=False):
    s = int(seconds)
    m = int(seconds/60); s -= m*60
    h = int(m/60); m -= h*60

    if as_text: return f"{h}h {m}m {s}s"
    else: return h, m, s

# ----====[ Numbers ]====----


# --- number limit v1.0
def limit(value:float, min:float, max:float):
    if value>max: return max
    if value<min: return min
    else: return value


# ----====[ Files ]====----


# --- new 1.0
def new_file(filename:str):
    f = open(filename, "x")
    f.close()

# --- load v1.1
def load(filename:int, mode="normal"):
    f = open(filename, "r")
    data = f.readlines()
    f.close()

    if   mode in ["normal", "n"]: return data # NORMAL
    elif mode in ["text", "t"]: # TEXT
        result = ""
        for line in data: result += line
        return result
    
    elif mode in ["database", "d"]: # DATABASE
        result = []
        for line in data:
            result.append(line.split())
        return result

# --- save v1.1
def save(filename:str, data, mode="normal"):
    f = open(filename, "w")

    if   mode in ["normal", "n", "text", "t"]: f.writelines(data) # NORMAL and TEXT
    elif mode in ["database", "d"]:
        result = []
        for line in data: 
            if len(result)+1<len(data): result.append(unlist_words(line)+"\n")
            else: result.append(unlist_words(line))
        f.writelines(result)
    f.close()

# --- zip directory v1.0
def zipdir(dir:str, filename:str):
    walkvar = file_walk(dir)

    zipf = zip.ZipFile(filename, "w")
    for file in walkvar:
        zipf.write(file, compress_type=zip.ZIP_DEFLATED)
    zipf.close()

# --- unzip v1.0
def unzip(dir_from:str, dir_to:str):
    zipf = zip.ZipFile(dir_from)
    zipf.extractall(dir_to)
    zipf.close()

# --- file walk v1.0
def file_walk(dir:str, catch_folders=False):
    walkvar = []
    
    def walk(dir:str):
        for f in os.listdir(dir):
            
            path = f"{dir}/{f}"
            if os.path.isdir(path):
                if catch_folders: walkvar.append(path)
                walk(path)
            else:
                walkvar.append(path)
    walk(dir)
    return walkvar


# ----====[ Math ]====----


# -- get average v1.0
def calc_avg(values:list):
    total = 0
    if len(values)>0:
        for v in values: total += v
    else: return 0
    return total/len(values)

# -- get max v1.0
def get_max(values:list):
    result = 0
    for v in values:
        if v>result: result=v
    return result

# -- get min v1.0
def get_min(values:list):
    result = 0
    for v in values:
        if v<result: result=v
    return result

# count items v1.0
def count_items(values:list):
    items = []
    count = []

    for item in values:
        if item not in items:
            items.append(item)
            count.append(1)
        else:
            count[items.index(item)] += 1
    
    result = []
    for i in range(0, len(items)):
        result.append([items[i], count[i]])

    return result

# get common
def get_common(values:list):

    items = count_items(values)
    result = [None, 0]

    for item in items:
        if item[1]>result[1]: result = item
    
    return result[0]

# get most common v1.0
def sort_by_rarity(values:list):

    items = count_items(values)
    copy = items
    result = []
    
    for item in items:
        index = 0
        for i in range(0, len(copy)):
            if copy[i][1]>copy[index][1]: index = i
            
        result.append(copy.pop(index)[0])
    return result


# ----====[ Classes ]====----


class Timer():
    def __init__(self):
        self.begin = time.time()
        self.end = self.begin
        self.run = False

    def start(self):
        if not self.run:
            self.begin = time.time()
            self.run = True

    def stop(self):
        if self.run:
            self.end = time.time()
            self.run = False
    
    def toggle(self):
        if self.run: self.stop()
        else: self.start()

    def get_delay(self):
        if self.run: return time.time() - self.begin
        else: return self.end - self.begin
    
    def is_running(self):
        return self.run

# -- Delay Function v1.0
class Defu():
    def __init__(self, delay:float, func):
        self.delay = delay
        self.func = func
        self.run = True
        self.last = time.time()
    
    def set_delay(self, delay:float): self.delay = delay
    def start(self): self.run = True
    def stop(self): self.run = False
    
    def work(self, args=None):
        if self.run:
            if time.time()-self.last > self.delay:
                if args: self.func(*args)
                else: self.func()
                self.last = time.time()

class Fps():
    def __init__(self):
        self.last = time.time()
        self.delay = 0
        self.fps = -1 # infinite
        self.avg = []
    
    def update(self):
        tm = time.time()
        self.delay = tm - self.last
        self.last = tm 
    
    def get_fps(self):
        if self.delay!=0: return round(1/self.delay, 0)
        else: return 60
    
    def get_delay(self): return self.delay
    
    def target_fps(self, fps:int):
        self.fps = fps

    def limit(self):
        if self.fps!=-1:
            
            target = 1/self.fps
            
            if self.delay<target:
                excess = target - self.delay
                time.sleep(excess)