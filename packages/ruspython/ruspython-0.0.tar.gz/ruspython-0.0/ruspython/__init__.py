def вывести(x): print(x)
def целое(x): return int(x)
def с_точькой(x): return float(x)
def строка(x): return str(x)
def словарь(x): return dict(x)
def картеж(x): return tuple(x)
def набор(x): return set(x)
def макс(*x): return max(x)
def мин(*x): return min(x)
def тип(x): return type(x)
def ввод(x = ''): return input(x)
def размер(x): return len(x)
def добавить(x,y): return x.append(y)
def убрать(x,y): return x.remove(y)
def вставить(x,y,z): return x.insert(y, z)
def очистить(x): return x.clear()
def большие(x): return x.upper()
def малые(x): return x.lower()
def бинарное(x): return bool(x)
def помощь():
  print("""
print() --> вывести()
int --> целое
float --> с_точькой
str --> строка
dict --> словарь
tuple --> картеж
set --> набор
max --> макс
min --> мин
type --> тип
input() --> ввод()
len --> размер
append --> добавить
insert --> вставить
clear --> очистить
upper --> большие
lower --> малые
bool --> бинарное
""")