
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

# CONSTANT

`LINUX`

`WINDOWS`

# FUNCTION

## avg
`avg`

Simple Average Function karena tidak disediakan oleh python

```python
n = [1, 22, 2, 3, 13, 2, 123, 12, 31, 2, 2, 12, 2, 1]
print(avg(n))
```


## basename
`basename`

Mengembalikan nama file dari path

```python
print(basename("/ini/nama/folder/ke/file.py"))
```


## chunck_array
`chunck_array`

Membagi array menjadi potongan-potongan dengan besaran yg diinginkan

```python
array = [2, 3, 12, 3, 3, 42, 42, 1, 43, 2, 42, 41, 4, 24, 32, 42, 3, 12, 32, 42, 42]
print(generator.chunck_array(array, 5))
print(chunck_array(array, 5))
```


## console_run
`console_run`

Menjalankan command seperti menjalankan command di Command Terminal


## create_folder
`create_folder`

Membuat folder.
Membuat folder secara recursive dengan permission.

```py
create_folder("contoh_membuat_folder")
create_folder("contoh/membuat/folder/recursive")
create_folder("./contoh_membuat_folder/secara/recursive")
```


## datetime_from_string
`datetime_from_string`

Parse iso_string menjadi datetime object

```python
print(datetime_from_string("2022-12-12 15:40:13").isoformat())
print(datetime_from_string("2022-12-12 15:40:13", timezone="Asia/Jakarta").isoformat())
```


## datetime_now
`datetime_now`

Memudahkan dalam membuat Datetime untuk suatu timezone tertentu

```python
print(datetime_now("Asia/Jakarta"))
print(datetime_now("GMT"))
print(datetime_now("Etc/GMT+7"))
```


## dict_first
`dict_first`

Mengambil nilai (key, value) pertama dari dictionary dalam bentuk tuple

```python
d = {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3",
}
print(dict_first(d))
```


## dirname
`dirname`

Mengembalikan nama folder dari path.
Tanpa trailing slash di akhir.

```python
print(dirname("/ini/nama/folder/ke/file.py"))
```


## exit_if_empty
`exit_if_empty`

Keluar dari program apabila seluruh variabel
setara dengan empty

```python
var1 = None
var2 = '0'
exit_if_empty(var1, var2)
```


## explode
`explode`

Memecah text menjadi list berdasarkan separator.

```python
t = '/ini/contoh/path/'
print(explode(t, separator='/'))
```


## file_get_contents
`file_get_contents`

Membaca seluruh isi file ke memory.
Apabila file tidak ada maka akan return None.
Apabila file ada tetapi kosong, maka akan return empty string

```py
print(file_get_contents("ifile_test.txt"))
```


## file_put_contents
`file_put_contents`

Menuliskan content ke file.
Apabila file tidak ada maka file akan dibuat.
Apabila file sudah memiliki content maka akan di overwrite.

```py
file_put_contents("ifile_test.txt", "Contoh menulis content")
```


## filter_empty
`filter_empty`


## get_class_method
`get_class_method`

Mengembalikan berupa tuple yg berisi list dari method dalam class

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


## get_filemtime
`get_filemtime`

Mengambil informasi last modification time file dalam nano seconds

```python
print(get_filemtime(__file__))
```


## get_filesize
`get_filesize`

Mengambil informasi file size dalam bytes

```python
print(get_filesize(__file__))
```


## github_pull
`github_pull`

Menjalankan command `git pull`

```py
github_pull()
```


## github_push
`github_push`

Menjalankan command status, add, commit dan push

```py
github_push('Commit Message')
```


## html_get_contents
`html_get_contents`

Mengambil content html dari url.

RETURN:
- String: Apabila hanya url saja yg diberikan
- List of etree: Apabila xpath diberikan
- False: Apabila terjadi error

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


## html_put_contents
`html_put_contents`

Fungsi untuk mengirim data ke URL dengan method POST dan mengembalikan
respon dari server sebagai string.

Parameters:
    url (str): URL tujuan.
    data (dict): Data yang akan dikirim.

Returns:
- str: Respon dari server dalam bentuk string.

```python
data = dict(pengirim="saya", penerima="kamu")
print(html_put_contents("https://arbadzukhron.deta.dev/", data))
```


## implode
`implode`

Simplify Python join functions like PHP function.
Iterable bisa berupa sets, tuple, list, dictionary.

```python
arr = {'asd','dfs','weq','qweqw'}
print(implode(arr, ', '))

arr = '/ini/path/seperti/url/'.split('/')
print(implode(arr, ','))
print(implode(arr, ',', remove_empty=True))

arr = {'a':'satu', 'b':(12, 34, 56), 'c':'tiga', 'd':'empat'}
print(implode(arr, separator='</li>\n<li>', start='<li>', end='</li>', recursive_flat=True))
print(implode(arr, separator='</div>\n<div>', start='<div>', end='</div>'))
print(implode(10, ' '))
```


## input_char
`input_char`

Meminta masukan satu huruf tanpa menekan Enter.

```py
input_char("Input char : ")
input_char("Input char : ", default='Y')
input_char("Input Char without print : ", echo_char=False)
```


## irange
`irange`

Improve python range() function untuk pengulangan menggunakan huruf

```python
print(generator.irange('a', 'z'))
print(irange('H', 'a'))
print(irange('1', '5', 3))
print(irange('1', 5, 3))
# print(irange('a', 5, 3))
print(irange(-10, 4, 3))
print(irange(1, 5))
```


## is_empty
`is_empty`

Mengecek apakah variable setara dengan nilai kosong pada empty.

Pengecekan nilai yang setara menggunakan simbol '==', sedangkan untuk
pengecekan lokasi memory yang sama menggunakan keyword 'is'

```python
print(is_empty("teks"))
print(is_empty(True))
print(is_empty(False))
print(is_empty(None))
print(is_empty(0))
print(is_empty([]))
```


## is_iterable
`is_iterable`

Mengecek apakah suatu variabel bisa dilakukan forloop atau tidak

```python
s = 'ini string'
print(is_iterable(s))

l = [12,21,2,1]
print(is_iterable(l))

r = range(100)
print(is_iterable(r))

d = {'a':1, 'b':2}
print(is_iterable(d.values()))
```


## iscandir
`iscandir`

Mempermudah scandir untuk mengumpulkan folder, subfolder dan file

```py
for i in generator.iscandir():
    print(i)

for i in iscandir():
    print(i)
```


## log
`log`

Decorator untuk mempermudah pembuatan log karena tidak perlu mengubah fungsi yg sudah ada.
Melakukan print ke console untuk menginformasikan proses yg sedang berjalan didalam program.

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


## print_colorize
`print_colorize`

Print text dengan warna untuk menunjukan text penting

```python
print_colorize("Print some text")
print_colorize("Print some text", color=colorama.Fore.RED)
```


## print_dir
`print_dir`

Print property dan method yang tersedia pada variabel

```python
p = pathlib.Path("c:/arba/dzukhron.dz")
print_dir(p)
```


## print_log
`print_log`

Akan melakukan print ke console.
Berguna untuk memberikan informasi proses program yg sedang berjalan.

```python
print_log("Standalone Log")
```


## random_bool
`random_bool`

Menghasilkan nilai random True atau False.
Fungsi ini merupakan fungsi tercepat untuk mendapatkan random bool.

```python
print(random_bool())
```


## scan_file
`scan_file`

Mengumpulkan nama-nama file dalam folder dan subfolder.

```py
for i in generator.scan_file():
    print(i)

for i in scan_file():
    print(i)
```


## scan_folder
`scan_folder`

Mengumpulkan nama-nama folder dan subfolder.
Tidak termasuk [".", ".."] dan file.

```python
for i in generator.scan_folder(recursive=False):
    print(i)

for i in scan_folder(recursive=False):
    print(i)
```


## serialize
`serialize`

Mengubah variabel data menjadi string untuk yang dapat dibaca untuk disimpan.
String yang dihasilkan berbentuk syntax YAML.

```python
data = {
    'a': 123,
    't': ['disini', 'senang', 'disana', 'senang'],
    'l': (12, 23, [12, 42])
}
print(serialize(data))
```


## set_timeout
`set_timeout`

Menjalankan fungsi ketika sudah sekian detik.
Apabila timeout masih berjalan tapi kode sudah selesai dieksekusi semua, maka
program tidak akan berhenti sampai timeout selesai, kemudian fungsi dijalankan,
kemudian program dihentikan.

```python
set_timeout(3, lambda: print("Timeout 3"))
x = set_timeout(7, lambda: print("Timeout 7"))
print(x)
print("menghentikan timeout 7")
x.cancel()
```


## sets_ordered
`sets_ordered`

Hanya mengambil nilai unik dari suatu list

```python
array = [2, 3, 12, 3, 3, 42, 42, 1, 43, 2, 42, 41, 4, 24, 32, 42, 3, 12, 32, 42, 42]
print(generator.sets_ordered(array))
print(sets_ordered(array))
```


## strtr
`strtr`

STRing TRanslate, mengubah string menggunakan kamus dari dict.

```python
text = 'aku disini mau kemana saja'
replacements = {
    "disini": "disitu",
    "kemana": "kesini",
}
print(strtr(text, replacements))
```


## strtr_regex
`strtr_regex`

STRing TRanslate metode Regex, mengubah string menggunakan kamus dari dict.

```python
text = 'aku {{ ini }} mau ke {{ sini }} mau kemana saja'
replacements = {
    r"\{\{\s*(ini)\s*\}\}": r"itu dan \1",
    r"\{\{\s*sini\s*\}\}": r"situ",
}
print(strtr_regex(text, replacements))
```


## to_str
`to_str`

Mengubah value menjadi string literal

```python
print(to_str(5))
print(to_str([]))
print(to_str(False))
print(to_str(True))
print(to_str(None))
```


## unserialize
`unserialize`

Mengubah string data hasil dari serialize menjadi variabel.
String data adalah berupa syntax YAML.

```python
data = {
    'a': 123,
    't': ['disini', 'senang', 'disana', 'senang'],
    'l': (12, 23, [12, 42])
}
s = serialize(data)
print(unserialize(s))
```


# CLASS

## Batchmaker
`Batchmaker`

Alat Bantu untuk membuat teks yang berulang.
Gunakan {[start]-[finish][-[step]]}.
```
[start] dan [finish]    -> bisa berupa huruf maupun angka
[-[step]]               -> bersifat optional
```

```python
s = "Urutan {1-30-5} dan {3-1} dan {a-d} dan {Z-A-10} saja."
print(Batchmaker(s).result())
```


## ComparePerformance
`ComparePerformance`

Menjalankan seluruh method dalam class,
kemudian membandingkan waktu yg diperlukan.

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


## RunParallel
`RunParallel`

Menjalankan program secara bersamaan.

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


## generator
`generator`

Class ini menyediakan beberapa fungsi yang bisa mengembalikan generator.
Digunakan untuk mengoptimalkan program.

Class ini dibuat karena python generator yang disimpan dalam variabel
hanya dapat diakses satu kali.

