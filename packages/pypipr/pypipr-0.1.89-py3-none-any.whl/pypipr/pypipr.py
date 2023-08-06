""" PYPIPR Module """

"""PYTHON Standard Module"""
import asyncio
import collections.abc
import datetime
import json
import math
import multiprocessing
import operator
import os
import pathlib
import platform
import pprint
import queue
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import timeit
import urllib
import uuid
import warnings
import webbrowser
import zoneinfo
import textwrap


__platform_system = platform.system()

WINDOWS = __platform_system == "Windows"
"""
True apabila berjalan di platform Windows

```python
print(WINDOWS)
```
"""

LINUX = __platform_system == "Linux"
"""
True apabila berjalan di platform Linux

```python
print(LINUX)
```
"""

# TYPE_NONE = type(None)


if WINDOWS:
    import msvcrt as _getch


"""PYPI Module"""
import colorama
import lxml.html
import requests
import yaml

if LINUX:
    import getch as _getch


colorama.init()


class generator:
    """
    Class ini menyediakan beberapa fungsi yang bisa mengembalikan generator.
    Digunakan untuk mengoptimalkan program.

    Class ini dibuat karena python generator yang disimpan dalam variabel
    hanya dapat diakses satu kali.
    """

    def iscandir(folder_name=".", glob_pattern="*", recursive=True):
        """
        Mempermudah scandir untuk mengumpulkan folder, subfolder dan file

        ```py
        for i in generator.iscandir():
            print(i)

        for i in iscandir():
            print(i)
        ```
        """
        if recursive:
            return pathlib.Path(folder_name).rglob(glob_pattern)
        else:
            return pathlib.Path(folder_name).glob(glob_pattern)

    def scan_folder(folder_name="", glob_pattern="*", recursive=True):
        """
        Mengumpulkan nama-nama folder dan subfolder.
        Tidak termasuk [".", ".."] dan file.

        ```python
        for i in generator.scan_folder(recursive=False):
            print(i)

        for i in scan_folder(recursive=False):
            print(i)
        ```
        """
        p = generator.iscandir(
            folder_name=folder_name,
            glob_pattern=glob_pattern,
            recursive=recursive,
        )
        for i in p:
            if i.is_dir():
                yield i

    def scan_file(folder_name="", glob_pattern="*", recursive=True):
        """
        Mengumpulkan nama-nama file dalam folder dan subfolder.

        ```py
        for i in generator.scan_file():
            print(i)

        for i in scan_file():
            print(i)
        ```
        """
        p = generator.iscandir(
            folder_name=folder_name,
            glob_pattern=glob_pattern,
            recursive=recursive,
        )
        for i in p:
            if i.is_file():
                yield i

    def get_class_method(cls):
        """
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
        """
        for x in dir(cls):
            a = getattr(cls, x)
            if not x.startswith("__") and callable(a):
                yield a

    def chunck_array(array, size, start=0):
        """
        Membagi array menjadi potongan-potongan dengan besaran yg diinginkan

        ```python
        array = [2, 3, 12, 3, 3, 42, 42, 1, 43, 2, 42, 41, 4, 24, 32, 42, 3, 12, 32, 42, 42]
        print(generator.chunck_array(array, 5))
        print(chunck_array(array, 5))
        ```
        """
        for i in range(start, len(array), size):
            yield array[i : i + size]

    def irange(start, finish, step=1):
        """
        Meningkatkan fungsi range() dari python untuk pengulangan menggunakan huruf

        ```python
        print(generator.irange('a', 'c'))
        print(irange('z', 'a', 10))
        print(irange('a', 'z', 10))
        print(irange(1, '7'))
        print(irange(10, 5))
        ```
        """

        def casting_class():
            start_int = isinstance(start, int)
            finish_int = isinstance(finish, int)
            start_str = isinstance(start, str)
            finish_str = isinstance(finish, str)
            start_numeric = start.isnumeric() if start_str else False
            finish_numeric = finish.isnumeric() if finish_str else False

            if start_numeric and finish_numeric:
                # irange("1", "5")
                return (int, str)

            if (start_numeric or start_int) and (finish_numeric or finish_int):
                # irange("1", "5")
                # irange("1", 5)
                # irange(1, "5")
                # irange(1, 5)
                return (int, int)

            if start_str and finish_str:
                # irange("a", "z")
                # irange("p", "g")
                return (ord, chr)

            """
            kedua if dibawah ini sudah bisa berjalan secara logika, tetapi
            perlu dimanipulasi supaya variabel start dan finish bisa diubah.
            """
            # irange(1, 'a') -> irange('1', 'a')
            # irange(1, '5') -> irange(1, 5)
            # irange('1', 5) -> irange(1, 5)
            # irange('a', 5) -> irange('a', '5')
            #
            # if start_str and finish_int:
            #     # irange("a", 5) -> irange("a", "5")
            #     finish = str(finish)
            #     return (ord, chr)
            #
            # if start_int and finish_str:
            #     # irange(1, "g") -> irange("1", "g")
            #     start = str(start)
            #     return (ord, chr)

            raise Exception(
                f"[{start} - {finish}] tidak dapat diidentifikasi kesamaannya"
            )

        counter_class, converter_class = casting_class()
        start = counter_class(start)
        finish = counter_class(finish)

        faktor = 1 if finish > start else -1
        step = int(step) * faktor
        finish += faktor

        for i in range(start, finish, step):
            yield converter_class(i)

    def sets_ordered(iterator):
        """
        Hanya mengambil nilai unik dari suatu list

        ```python
        array = [2, 3, 12, 3, 3, 42, 42, 1, 43, 2, 42, 41, 4, 24, 32, 42, 3, 12, 32, 42, 42]
        print(generator.sets_ordered(array))
        print(sets_ordered(array))
        ```
        """
        for i in dict.fromkeys(iterator):
            yield i

    def filter_empty(iterable, zero_is_empty=True, str_strip=True):
        for i in iterable:
            if i == 0 and zero_is_empty:
                continue
            if isinstance(i, str) and str_strip:
                i = i.strip()
            if not is_iterable(i) and not to_str(i):
                continue
            yield i


def print_colorize(
    text,
    color=colorama.Fore.GREEN,
    bright=colorama.Style.BRIGHT,
    color_end=colorama.Style.RESET_ALL,
    text_start="",
    text_end="\n",
):
    """
    Print text dengan warna untuk menunjukan text penting

    ```python
    print_colorize("Print some text")
    print_colorize("Print some text", color=colorama.Fore.RED)
    ```
    """
    print(f"{text_start}{color + bright}{text}{color_end}", end=text_end, flush=True)


def log(text=None):
    """
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
    """

    def inner_log(func=None):
        def callable_func(*args, **kwargs):
            main_function(text)
            result = func(*args, **kwargs)
            return result

        def main_function(param):
            print_log(param)

        if func is None:
            return main_function(text)
        return callable_func

    if text is None:
        return inner_log
    elif callable(text):
        return inner_log(text)
    else:
        # inner_log(None)
        return inner_log


def print_log(text):
    """
    Akan melakukan print ke console.
    Berguna untuk memberikan informasi proses program yg sedang berjalan.

    ```python
    print_log("Standalone Log")
    ```
    """
    print_colorize(f">>> {text}")


def console_run(command):
    """
    Menjalankan command seperti menjalankan command di Command Terminal
    """
    return subprocess.run(command, shell=True)


def input_char(
    prompt=None,
    prompt_ending="",
    newline_after_input=True,
    echo_char=True,
    default=None,
):
    """
    Meminta masukan satu huruf tanpa menekan Enter.

    ```py
    input_char("Input char : ")
    input_char("Input char : ", default='Y')
    input_char("Input Char without print : ", echo_char=False)
    ```
    """
    if prompt:
        print(prompt, end=prompt_ending, flush=True)
    if default is not None:
        a = default
    else:
        a = _getch.getche() if echo_char else _getch.getch()
    if newline_after_input:
        print()
    return a.decode()


def datetime_now(timezone=None):
    """
    Memudahkan dalam membuat Datetime untuk suatu timezone tertentu

    ```python
    print(datetime_now("Asia/Jakarta"))
    print(datetime_now("GMT"))
    print(datetime_now("Etc/GMT+7"))
    ```
    """
    tz = zoneinfo.ZoneInfo(timezone) if timezone else None
    return datetime.datetime.now(tz)


def datetime_from_string(iso_string, timezone="UTC"):
    """
    Parse iso_string menjadi datetime object

    ```python
    print(datetime_from_string("2022-12-12 15:40:13").isoformat())
    print(datetime_from_string("2022-12-12 15:40:13", timezone="Asia/Jakarta").isoformat())
    ```
    """
    return datetime.datetime.fromisoformat(iso_string).replace(
        tzinfo=zoneinfo.ZoneInfo(timezone)
    )


def sets_ordered(iterable):
    return type(iterable)(generator.sets_ordered(iterable))


def chunck_array(array, size, start=0):
    return tuple(generator.chunck_array(array=array, size=size, start=start))


def github_push(commit=None):
    """
    Menjalankan command status, add, commit dan push

    ```py
    github_push('Commit Message')
    ```
    """

    def console(t, c):
        print_log(t)
        console_run(c)

    def console_input(prompt, default):
        print_colorize(prompt, text_end="")
        if default:
            print(default)
            return default
        else:
            return input()

    print_log("Menjalankan Github Push")
    console("Checking files", "git status")
    msg = console_input("Commit Message if any or empty to exit : ", commit)
    if msg:
        console("Mempersiapkan files", "git add .")
        console("Menyimpan files", f'git commit -m "{msg}"')
        console("Mengirim files", "git push")
    print_log("Selesai Menjalankan Github Push")


def github_pull():
    """
    Menjalankan command `git pull`

    ```py
    github_pull()
    ```
    """
    print_log("Git Pull")
    console_run("git pull")


def file_get_contents(filename):
    """
    Membaca seluruh isi file ke memory.
    Apabila file tidak ada maka akan return None.
    Apabila file ada tetapi kosong, maka akan return empty string

    ```py
    print(file_get_contents("ifile_test.txt"))
    ```
    """
    try:
        f = open(filename, "r")
        r = f.read()
        f.close()
        return r
    except:
        return None


def file_put_contents(filename, contents):
    """
    Menuliskan content ke file.
    Apabila file tidak ada maka file akan dibuat.
    Apabila file sudah memiliki content maka akan di overwrite.

    ```py
    file_put_contents("ifile_test.txt", "Contoh menulis content")
    ```
    """
    f = open(filename, "w")
    r = f.write(contents)
    f.close()
    return r


def create_folder(folder_name):
    """
    Membuat folder.
    Membuat folder secara recursive dengan permission.

    ```py
    create_folder("contoh_membuat_folder")
    create_folder("contoh/membuat/folder/recursive")
    create_folder("./contoh_membuat_folder/secara/recursive")
    ```
    """
    pathlib.Path(folder_name).mkdir(parents=True, exist_ok=True)


def iscandir(folder_name=".", glob_pattern="*", recursive=True):
    return tuple(
        generator.iscandir(
            folder_name=folder_name,
            glob_pattern=glob_pattern,
            recursive=recursive,
        )
    )


def scan_folder(folder_name="", glob_pattern="*", recursive=True):
    return tuple(
        generator.scan_folder(
            folder_name=folder_name,
            glob_pattern=glob_pattern,
            recursive=recursive,
        )
    )


def scan_file(folder_name="", glob_pattern="*", recursive=True):
    return tuple(
        generator.scan_file(
            folder_name=folder_name,
            glob_pattern=glob_pattern,
            recursive=recursive,
        )
    )


def html_get_contents(url, xpath=None, regex=None, css_select=None):
    """
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
    """
    url_req = urllib.request.Request(
        url=url,
        headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36"
        },
    )
    url_open = urllib.request.urlopen(url_req)
    try:
        if xpath:
            return lxml.html.parse(url_open).findall(xpath)
        if regex:
            return re.findall(regex, url_open.read().decode())
        if css_select:
            return lxml.html.parse(url_open).getroot().cssselect(css_select)
        return url_open.read().decode()
    except:
        return False


def html_put_contents(url, data):
    """
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
    """

    # Encode data ke dalam format yang bisa dikirim
    data = urllib.parse.urlencode(data).encode()

    # Buat objek request
    req = (
        urllib.request.Request(
            url=url,
            data=data,
            headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36"
            },
        ),
    )

    # Kirim request dan terima respon
    response = urllib.request.urlopen(req)
    html = response.read().decode()

    # Tutup koneksi
    response.close()

    # Kembalikan respon sebagai string
    return html


def get_filesize(filename):
    """
    Mengambil informasi file size dalam bytes

    ```python
    print(get_filesize(__file__))
    ```
    """
    return os.stat(filename).st_size


def get_filemtime(filename):
    """
    Mengambil informasi last modification time file dalam nano seconds

    ```python
    print(get_filemtime(__file__))
    ```
    """
    return os.stat(filename).st_mtime_ns


def dict_first(d: dict) -> tuple:
    """
    Mengambil nilai (key, value) pertama dari dictionary dalam bentuk tuple

    ```python
    d = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    print(dict_first(d))
    ```
    """
    for k in d:
        return (k, d[k])


def random_bool() -> bool:
    """
    Menghasilkan nilai random True atau False.
    Fungsi ini merupakan fungsi tercepat untuk mendapatkan random bool.

    ```python
    print(random_bool())
    ```
    """
    return bool(random.getrandbits(1))


def set_timeout(interval, func, args=None, kwargs=None):
    """
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
    """
    t = threading.Timer(interval=interval, function=func, args=args, kwargs=kwargs)
    t.start()
    # t.cancel() untuk menghentikan timer sebelum waktu habis
    return t


def get_class_method(cls):
    return tuple(generator.get_class_method(cls))


class ComparePerformance:
    """
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
    """

    number = 1

    def get_all_instance_methods(self):
        c = set(dir(__class__))
        l = (x for x in dir(self) if x not in c)
        return tuple(
            x for x in l if callable(getattr(self, x)) and not x.startswith("_")
        )

    def test_method_performance(self, methods):
        d = {x: [] for x in methods}
        for _ in range(self.number):
            for i in set(methods):
                d[i].append(self.get_method_performance(i))
        return d

    def get_method_performance(self, callable_method):
        c = getattr(self, callable_method)
        s = time.perf_counter_ns()
        for _ in range(self.number):
            c()
        f = time.perf_counter_ns()
        return f - s

    def calculate_average(self, d: dict):
        # avg = lambda v: sum(v) / len(v)
        r1 = {i: avg(v) for i, v in d.items()}
        min_value = min(r1.values())
        persen = lambda v: int(v / min_value * 100)
        r2 = {i: persen(v) for i, v in r1.items()}
        return r2

    def compare_performance(self):
        m = self.get_all_instance_methods()
        p = self.test_method_performance(m)
        a = self.calculate_average(p)
        return a

    def compare_result(self):
        m = self.get_all_instance_methods()
        return {x: getattr(self, x)() for x in m}


class RunParallel:
    """
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
    """

    def get_all_instance_methods(self, coroutine):
        c = set(dir(__class__))
        l = (x for x in dir(self) if x not in c)
        return tuple(
            a
            for x in l
            if callable(a := getattr(self, x))
            and not x.startswith("_")
            and asyncio.iscoroutinefunction(a) == coroutine
        )

    def run_asyncio(self):
        m = self.get_all_instance_methods(coroutine=True)
        a = self.module_asyncio(*m)
        return self.dict_results(m, a)

    def run_multi_threading(self):
        m = self.get_all_instance_methods(coroutine=False)
        a = self.module_threading(*m)
        return self.dict_results(m, a)

    def run_multi_processing(self):
        m = self.get_all_instance_methods(coroutine=False)
        a = self.module_multiprocessing(*m)
        return self.dict_results(m, a)

    def dict_results(self, names, results):
        return dict(zip((x.__name__ for x in names), results))

    def module_asyncio(self, *args):
        async def main(*args):
            return await asyncio.gather(*(x() for x in args))

        return asyncio.run(main(*args))

    def module_threading(self, *args):
        a = tuple(dict() for _ in args)
        q = queue.Queue()
        r = tuple(
            threading.Thread(target=v, args=(a[i], q)) for i, v in enumerate(args)
        )
        for i in r:
            i.start()
        for i in r:
            i.join()
        return a

    def module_multiprocessing(self, *args):
        m = multiprocessing.Manager()
        q = m.Queue()
        a = tuple(m.dict() for _ in args)
        r = tuple(
            multiprocessing.Process(target=v, args=(a[i], q))
            for i, v in enumerate(args)
        )
        for i in r:
            i.start()
        for i in r:
            i.join()
        return (i.copy() for i in a)


def avg(i):
    """
    Simple Average Function karena tidak disediakan oleh python

    ```python
    n = [1, 22, 2, 3, 13, 2, 123, 12, 31, 2, 2, 12, 2, 1]
    print(avg(n))
    ```
    """
    return sum(i) / len(i)


def exit_if_empty(*args):
    """
    Keluar dari program apabila seluruh variabel
    setara dengan empty

    ```python
    var1 = None
    var2 = '0'
    exit_if_empty(var1, var2)
    ```
    """
    for i in args:
        if not is_empty(i):
            return
    sys.exit()


def implode(
    iterable,
    separator="",
    start="",
    end="",
    remove_empty=False,
    recursive=True,
    recursive_flat=False,
):
    """
    Simplify Python join functions like PHP function.
    Iterable bisa berupa sets, tuple, list, dictionary.

    ```python
    arr = {'asd','dfs','weq','qweqw'}
    print(implode(arr, ', '))

    arr = '/ini/path/seperti/url/'.split('/')
    print(implode(arr, ','))
    print(implode(arr, ',', remove_empty=True))

    arr = {'a':'satu', 'b':(12, 34, 56), 'c':'tiga', 'd':'empat'}
    print(implode(arr, separator='</li>\\n<li>', start='<li>', end='</li>', recursive_flat=True))
    print(implode(arr, separator='</div>\\n<div>', start='<div>', end='</div>'))
    print(implode(10, ' '))
    ```
    """
    if not is_iterable(iterable):
        iterable = [iterable]

    separator = to_str(separator)

    if isinstance(iterable, dict):
        iterable = iterable.values()

    if remove_empty:
        iterable = (i for i in generator.filter_empty(iterable))

    if recursive:
        rec_flat = dict(start=start, end=end)
        if recursive_flat:
            rec_flat = dict(start="", end="")
        rec = lambda x: implode(
            iterable=x,
            separator=separator,
            **rec_flat,
            remove_empty=remove_empty,
            recursive=recursive,
            recursive_flat=recursive_flat,
        )
        iterable = ((rec(i) if is_iterable(i) else i) for i in iterable)

    iterable = (str(i) for i in iterable)

    result = start

    for index, value in enumerate(iterable):
        if index:
            result += separator
        result += value

    result += end

    return result


def strtr(string: str, replacements: dict):
    """
    STRing TRanslate, mengubah string menggunakan kamus dari dict.

    ```python
    text = 'aku disini mau kemana saja'
    replacements = {
        "disini": "disitu",
        "kemana": "kesini",
    }
    print(strtr(text, replacements))
    ```
    """
    for i, v in replacements.items():
        string = string.replace(i, v)
    return string


def strtr_regex(string: str, replacements: dict, flags=0):
    """
    STRing TRanslate metode Regex, mengubah string menggunakan kamus dari dict.

    ```python
    text = 'aku {{ ini }} mau ke {{ sini }} mau kemana saja'
    replacements = {
        r"\{\{\s*(ini)\s*\}\}": r"itu dan \\1",
        r"\{\{\s*sini\s*\}\}": r"situ",
    }
    print(strtr_regex(text, replacements))
    ```
    """
    for i, v in replacements.items():
        string = re.sub(i, v, string, flags=flags)
    return string


def print_dir(var):
    """
    Print property dan method yang tersedia pada variabel

    ```python
    p = pathlib.Path("c:/arba/dzukhron.dz")
    print_dir(p)
    ```
    """
    for i in dir(var):
        try:
            a = getattr(var, i)
            r = a() if callable(a) else a
            print(f"{i: >20} : {r}")
        except:
            pass


def is_iterable(var):
    """
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
    """

    """ Metode #1 """
    # it = (list, tuple, set, dict)
    # it += (TYPE_GENERATOR, TYPE_RANGE, TYPE_DICT_VALUES)
    # return isinstance(var, it)

    """ Metode #2 """
    # return isinstance(var, collections.abc.Iterable)

    """ Metode #3 """
    try:
        iter(var)
        return True
    except TypeError:
        return False


def irange(start, finish, step=1):
    """
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
    """
    return list(generator.irange(start, finish, step))


def serialize(data):
    """
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
    """
    return yaml.safe_dump(data)


def unserialize(data):
    """
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
    """
    return yaml.safe_load(data)


def basename(path):
    """
    Mengembalikan nama file dari path

    ```python
    print(basename("/ini/nama/folder/ke/file.py"))
    ```
    """
    return os.path.basename(path)


def dirname(path):
    """
    Mengembalikan nama folder dari path.
    Tanpa trailing slash di akhir.

    ```python
    print(dirname("/ini/nama/folder/ke/file.py"))
    ```
    """
    return os.path.dirname(path)


class Batchmaker:
    """
    Alat Bantu untuk membuat teks yang berulang.
    Gunakan {...-...}.

    ```python
    s = "Urutan {1-3} dan {3-1} dan {a-d} dan {D-A} saja."
    print(Batchmaker(s).result())
    ```
    """

    regex_pattern = r"\{([0-9a-zA-Z]+)\-([0-9a-zA-Z]+)\}"
    regex_compile = re.compile(regex_pattern)

    def __init__(self, pattern) -> None:
        self.text: str = pattern

    def result(self):
        s = self.regex_compile.search(self.text)

        if s is None:
            return [self.text]

        find = s.group()
        start = s.group(1)
        finish = s.group(2)

        result = list()
        for i in generator.irange(start, finish):
            r = self.text.replace(find, i)
            result += Batchmaker(r).result()

        return result


def filter_empty(iterable, zero_is_empty=True, str_strip=True):
    return type(iterable)(
        generator.filter_empty(
            iterable=iterable,
            zero_is_empty=zero_is_empty,
            str_strip=str_strip,
        )
    )


def to_str(value):
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, bool):
        return "1" if value else "0"
    if is_empty(value):
        return ""
    raise Exception(f"Tipe data {value} tidak diketahui")


# Dibuat beberapa baris supaya terlihat rapi
__is_empty = [None, False, 0, -0]
__is_empty += ["0", "", "-0", "\n", "\t"]
__is_empty += [set(), dict(), list(), tuple()]


def is_empty(variable, empty=__is_empty):
    """
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
    """
    for e in empty:
        if variable == e:
            return True
    return False


def explode(text, separator="", include_separator=False):
    """
    Memecah text menjadi list berdasarkan separator.

    ```python
    t = '/ini/contoh/path/'
    print(explode(t, separator='/'))
    ```
    """
    if include_separator:
        separator = f"({separator})"

    result = re.split(separator, text, flags=re.IGNORECASE | re.MULTILINE)

    return result
