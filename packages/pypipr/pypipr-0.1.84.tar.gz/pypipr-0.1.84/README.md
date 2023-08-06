# About
The Python Package Index Project (pypipr)

pypi : https://pypi.org/project/pypipr


# Setup
Install with pip
```
python -m pip install pypipr
```

Import with * for fastest access
```python
from pypipr.pypipr import *
```


# Functions
`WINDOWS` True apabila berjalan di platform Windows

```python
print(WINDOWS)
```


`LINUX` True apabila berjalan di platform Linux

```python
print(LINUX)
```


`avg()` Simple Average Function karena tidak disediakan oleh python

```python
n = [1, 22, 2, 3, 13, 2, 123, 12, 31, 2, 2, 12, 2, 1]
print(avg(n))
```


`random_bool()` Menghasilkan nilai random antara 1 atau 0

```python
print(random_bool())
```


`set_timeout()` Menjalankan fungsi ketika sudah sekian detik.

```python
set_timeout(3, lambda: print("Timeout 3"))
x = set_timeout(7, lambda: print("Timeout 7"))
print(x)
print("menghentikan timeout 7")
x.cancel()
```


`get_class_method()` Mengembalikan berupa tuple yg berisi list dari method dalam class

```python
class ExampleGetClassMethod:
    def a():
        return [x for x in range(10)]

    def b():
        return [x for x in range(10)]

    def c():
        return [x for x in range(10)]

    def d():
        return [x for x in range(10)]


if __name__ == "__main__":
    print(get_class_method(ExampleGetClassMethod))
```


`exit_if_empty()` Menghentikan program apabila semua variabel bernilai false

```python
var1 = None
var2 = '0'
exit_if_empty(var1, var2)
```


`strtr()` STRing TRanslate, mengubah string menggunakan kamus dari dict.

```python
text = 'aku disini mau kemana saja'
replacements = {
    "disini": "disitu",
    "kemana": "kesini",
}
print(strtr(text, replacements))
```


`strtr_regex()` STRing TRanslate, mengubah string menggunakan kamus dari dict.

```python
text = 'aku {{ ini }} mau ke {{ sini }} mau kemana saja'
replacements = {
    r"\{\{\s*(ini)\s*\}\}": r"itu dan \1",
    r"\{\{\s*sini\s*\}\}": r"situ",
}
print(strtr_regex(text, replacements))
```


`print_dir()` print possible property and method from variable

```python
p = pathlib.Path("c:/arba/dzukhron.dz")
print_dir(p)
```


`is_iterable()` Mengecek apakah suatu variabel bisa dilakukan forloop atau tidak

```python
s = 'ini string'
print(is_iterable(s))

l = [12,21,2,1]
print(is_iterable(l))
```


`irange()` Meningkatkan fungsi range() dari python untuk pengulangan menggunakan huruf

```python
print(generator.irange('a', 'z'))
print(irange('H', 'a'))
print(irange('1', '5', 3))
print(irange('1', 5, 3))
# print(irange('a', 5, 3))
print(irange(-10, 4, 3))
print(irange(1, 5))
```


`serialize()`  PHP like serialize function

```python
data = {
    'a': 123,
    't': ['disini', 'senang', 'disana', 'senang'],
    'l': (12, 23, [12, 42])
}
print(serialize(data))
```


`unserialize()` PHP like unserialize function

```python
data = {
    'a': 123,
    't': ['disini', 'senang', 'disana', 'senang'],
    'l': (12, 23, [12, 42])
}
s = serialize(data)
print(unserialize(s))
```


`Batchmaker` Class untuk membuat teks yang berulang

```python
s = "Urutan {1-3} dan {3-1} dan {a-d} dan {D-A} saja."
print(Batchmaker(s).result())
```


# Compare Performance

`class ComparePerformance` Menjalankan seluruh method dalam class, kemudian membandingkan waktu yg diperlukan.

```python
class ExampleComparePerformance(ComparePerformance):
    # number = 1
    z = 10

    def a(self):
        return (x for x in range(self.z))

    def b(self):
        return tuple(x for x in range(self.z))

    def c(self):
        return [x for x in range(self.z)]

    def d(self):
        return list(x for x in range(self.z))


if __name__ == "__main__":
    print(ExampleComparePerformance().compare_result())
    print(ExampleComparePerformance().compare_performance())
    print(ExampleComparePerformance().compare_performance())
    print(ExampleComparePerformance().compare_performance())
    print(ExampleComparePerformance().compare_performance())
    print(ExampleComparePerformance().compare_performance())
```


# Run Parallel

`class RunParallel` Menjalankan program secara bersamaan.


Structure:
- Semua methods akan dijalankan secara paralel kecuali method dengan nama yg diawali underscore `_`
- Method untuk multithreading/multiprocessing harus memiliki 2 parameter, yaitu: `result: dict` dan `q: queue.Queue`. Parameter `result` digunaan untuk memberikan return value dari method, dan Parameter `q` digunakan untuk mengirim data antar proses.
- Method untuk asyncio harus menggunakan keyword `async def`, dan untuk perpindahan antar kode menggunakan `await asyncio.sleep(0)`, dan keyword `return` untuk memberikan return value.
- Return Value berupa dictionary dengan key adalah nama function, dan value adalah return value dari setiap fungsi


Note:
- `class RunParallel` didesain hanya untuk pemrosesan data saja.
- Penggunaannya `class RunParallel` dengan cara membuat instance sub class beserta data yg akan diproses, kemudian panggil fungsi yg dipilih `run_asyncio / run_multi_threading / run_multi_processing`, kemudian dapatkan hasilnya.
- `class RunParallel` tidak didesain untuk menyimpan data, karena setiap module terutama module `multiprocessing` tidak dapat mengakses data kelas dari proses yg berbeda.


```python
class ExampleRunParallel(RunParallel):
    z = "ini"

    def __init__(self) -> None:
        self.pop = random.randint(0, 100)
    
    def _set_property_here(self, v):
        self.prop = v

    def a(self, result: dict, q: queue.Queue):
        result["z"] = self.z
        result["pop"] = self.pop
        result["a"] = "a"
        q.put("from a 1")
        q.put("from a 2")

    def b(self, result: dict, q: queue.Queue):
        result["z"] = self.z
        result["pop"] = self.pop
        result["b"] = "b"
        result["q_get"] = q.get()

    def c(self, result: dict, q: queue.Queue):
        result["z"] = self.z
        result["pop"] = self.pop
        result["c"] = "c"
        result["q_get"] = q.get()

    async def d(self):
        print("hello")
        await asyncio.sleep(0)
        print("hello")

        result = {}
        result["z"] = self.z
        result["pop"] = self.pop
        result["d"] = "d"
        return result

    async def e(self):
        print("world")
        await asyncio.sleep(0)
        print("world")

        result = {}
        result["z"] = self.z
        result["pop"] = self.pop
        result["e"] = "e"
        return result


if __name__ == "__main__":
    print(ExampleRunParallel().run_asyncio())
    print(ExampleRunParallel().run_multi_threading())
    print(ExampleRunParallel().run_multi_processing())
```


# Collections

`sets_ordered()` Hanya mengambil nilai unik dari suatu list

```python
array = [2, 3, 12, 3, 3, 42, 42, 1, 43, 2, 42, 41, 4, 24, 32, 42, 3, 12, 32, 42, 42]
print(generator.sets_ordered(array))
print(sets_ordered(array))
```


`chunck_array()` membagi array menjadi potongan dengan besaran yg diinginkan

```python
array = [2, 3, 12, 3, 3, 42, 42, 1, 43, 2, 42, 41, 4, 24, 32, 42, 3, 12, 32, 42, 42]
print(generator.chunck_array(array, 5))
print(chunck_array(array, 5))
```


`dict_first()` Mengambil nilai (key, value) pertama dari dictionary dalam bentuk tuple

```python
d = {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3",
}
print(dict_first(d))
```


`implode()` Simplify Python join functions

```python
arr = {'asd','dfs','weq','qweqw'}
print(implode(arr, ', '))

arr = '/ini/path/seperti/url/'.split('/')
print(implode(arr, ','))
print(implode(arr, ',', remove_empty=True))

arr = {'a':'satu', 'b':'dua', 'c':'tiga', 'd':'empat'}
print(implode(arr, separator='</li>\n<li>', start='<li>', end='</li>'))
print(implode(10, ' '))
```


# Console

`print_colorize()` print ke console dengan warna

```python
print_colorize("Print some text")
print_colorize("Print some text", color=colorama.Fore.RED)
```


`@Log()` / `Log decorator` akan melakukan print ke console. Mempermudah pembuatan log karena tidak perlu mengubah fungsi yg sudah ada. Berguna untuk memberikan informasi proses program yg sedang berjalan.

```python

@log
def some_function():
    pass

@log()
def some_function_again():
    pass

@log("Calling some function")
def some_function_more():
    pass

if __name__ == "__main__":
    some_function()
    some_function_again()
    some_function_more()
```


`print_log` akan melakukan print ke console. Berguna untuk memberikan informasi proses program yg sedang berjalan.

```python
print_log("Standalone Log")
```


`input_char()` meminta masukan satu huruf tanpa menekan enter.

```py
input_char("Input char : ")
input_char("Input char : ", default='Y')
input_char("Input Char without print : ", echo_char=False)
```


# Datetime

`datetime_now()` memudahkan dalam membuat tanggal dan waktu untuk suatu timezone

```python
print(datetime_now("Asia/Jakarta"))
print(datetime_now("GMT"))
print(datetime_now("Etc/GMT+7"))
```


`datetime_from_string()` Parse iso_string menjadi datetime object dengan timezone UTC

```python
print(datetime_from_string("2022-12-12 15:40:13").isoformat())
print(datetime_from_string("2022-12-12 15:40:13", timezone="Asia/Jakarta").isoformat())
```


# File and Folder

`file_put_contents()` membuat file kemudian menuliskan contents ke file. Apabila file memiliki contents, maka contents akan di overwrite.

```py
file_put_contents("ifile_test.txt", "Contoh menulis content")
```


`file_get_contents()` membaca contents file ke memory.

```py
print(file_get_contents("ifile_test.txt"))
```


`html_get_contents()` Mengambil content html dari url

```py
print(html_get_contents("https://arbadzukhron.deta.dev/"))
```
```python
# Using XPATH
a = html_get_contents("https://www.google.com/", xpath="//a")
for i in a:
    print(i.text)
    print(i.attrib.get('href'))

# Using REGEX
a = html_get_contents("https://www.google.com/", regex=r"(<a.[^>]+>(?:(?:\s+)?(.[^<]+)(?:\s+)?)<\/a>)")
for i in a:
    print(i)

# Using cssselect
a = html_get_contents("https://www.google.com/", css_select="a")
for i in a:
    print(i.text)
    print(i.attrib.get("href"))
```


`html_put_contents()` Mengirim POST data ke url. Return response content.

```py
data = dict(pengirim="saya", penerima="kamu")
print(html_put_contents("https://arbadzukhron.deta.dev/", data))
```


`get_filesize()` Mengambil informasi file size dalam bytes

```python
print(get_filesize(__file__))
```


`get_filemtime()` Mengambil informasi last modification time file dalam nano seconds

```python
print(get_filemtime(__file__))
```


`create_folder()` membuat folder secara recursive.

```py
create_folder("contoh_membuat_folder")
create_folder("contoh/membuat/folder/recursive")
create_folder("./contoh_membuat_folder/secara/recursive")
```


`iscandir()` scan folder, subfolder, dan file

```py
for i in generator.iscandir():
    print(i)

for i in iscandir():
    print(i)
```


`scan_folder()` scan folder dan subfolder

```python
for i in generator.scan_folder(recursive=False):
    print(i)

for i in scan_folder(recursive=False):
    print(i)
```


`scan_file()` scan file dalam folder dan subfolder

```py
for i in generator.scan_file():
    print(i)
    
for i in scan_file():
    print(i)
```


`dirname()` nama folder

```python
print(dirname("/ini/nama/folder/ke/file.py"))
```


`basename()` nama file dari path

```python
print(basename("/ini/nama/folder/ke/file.py"))
```


# Third Party

`github_pull()` simple github pull

```py
github_pull()
```


`github_push()` simple github push dengan auto commit message

```py
github_push('Commit Message')
```
