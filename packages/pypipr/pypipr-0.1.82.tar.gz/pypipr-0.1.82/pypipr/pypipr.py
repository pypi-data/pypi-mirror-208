""" PYPIPR Module """

"""PYTHON Standard Module"""
import datetime
import zoneinfo
import re
import subprocess
import platform
import pathlib
import urllib
import random
import webbrowser
import json
import shutil
import uuid
import time
import threading
import multiprocessing
import os
import timeit
import operator
import asyncio
import queue
import sys
import warnings
import collections.abc
import math
import pprint

# import math

__platform_system = platform.system()
WINDOWS = __platform_system == "Windows"
LINUX = __platform_system == "Linux"

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
    generator for Generators
    """

    def iscandir(folder_name=".", glob_pattern="*", recursive=True):
        """
        Mempermudah scandir untuk mengumpulkan folder, subfolder dan file
        """
        if recursive:
            return pathlib.Path(folder_name).rglob(glob_pattern)
        else:
            return pathlib.Path(folder_name).glob(glob_pattern)

    def scan_folder(folder_name="", glob_pattern="*", recursive=True):
        """
        Hanya mengumpulkan nama-nama folder dan subfolder.
        Tidak termasuk [".", ".."].
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
        Hanya mengumpulkan nama-nama file dalam folder dan subfolder.
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
        """
        for x in dir(cls):
            a = getattr(cls, x)
            if not x.startswith("__") and callable(a):
                yield a

    def chunck_array(array, size, start=0):
        """
        Membagi array menjadi potongan-potongan sebesar size
        """
        for i in range(start, len(array), size):
            yield array[i : i + size]

    def irange(start, finish, step=1):
        """
        Meningkatkan fungsi range() dari python untuk pengulangan menggunakan huruf
        contoh: irange('a', 'z')
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
        for i in dict.fromkeys(iterator):
            yield i


def print_colorize(
    text,
    color=colorama.Fore.GREEN,
    bright=colorama.Style.BRIGHT,
    color_end=colorama.Style.RESET_ALL,
    text_start="",
    text_end="\n",
):
    """Print text dengan warna untuk menunjukan text penting"""
    print(f"{text_start}{color + bright}{text}{color_end}", end=text_end, flush=True)


def log(text=None):
    """
    Melakukan print ke console untuk menginformasikan proses yg sedang berjalan didalam program.
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
    print_colorize(f">>> {text}")


def console_run(command):
    """Menjalankan command seperti menjalankan command di Command Terminal"""
    return subprocess.run(command, shell=True)


def input_char(
    prompt=None,
    prompt_ending="",
    newline_after_input=True,
    echo_char=True,
    default=None,
):
    """Meminta masukan satu huruf tanpa menekan Enter. Masukan tidak ditampilkan."""
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
    Datetime pada timezone tertentu
    """
    tz = zoneinfo.ZoneInfo(timezone) if timezone else None
    return datetime.datetime.now(tz)


def datetime_from_string(iso_string, timezone="UTC"):
    """
    Parse iso string menjadi datetime object dengan timezone UTC
    """
    return datetime.datetime.fromisoformat(iso_string).replace(
        tzinfo=zoneinfo.ZoneInfo(timezone)
    )


def sets_ordered(iterator):
    """
    Hanya mengambil nilai unik dari suatu list
    """
    return tuple(generator.sets_ordered(iterator))


def chunck_array(array, size, start=0):
    """
    Membagi array menjadi potongan-potongan sebesar size
    """
    return tuple(generator.chunck_array(array=array, size=size, start=start))


def github_push(commit=None):
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
    print_log("Git Pull")
    console_run("git pull")


def file_get_contents(filename):
    """
    Membaca seluruh isi file ke memory.
    Apabila file tidak ada maka akan return None.
    Apabila file ada tetapi kosong, maka akan return empty string
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
    """
    f = open(filename, "w")
    r = f.write(contents)
    f.close()
    return r


def create_folder(folder_name):
    """
    Membuat folder.
    Membuat folder secara recursive dengan permission.
    """
    pathlib.Path(folder_name).mkdir(parents=True, exist_ok=True)


def iscandir(folder_name=".", glob_pattern="*", recursive=True):
    """
    Mempermudah scandir untuk mengumpulkan folder, subfolder dan file
    """
    return tuple(
        generator.iscandir(
            folder_name=folder_name,
            glob_pattern=glob_pattern,
            recursive=recursive,
        )
    )


def scan_folder(folder_name="", glob_pattern="*", recursive=True):
    """
    Hanya mengumpulkan nama-nama folder dan subfolder.
    Tidak termasuk [".", ".."].
    """
    return tuple(
        generator.scan_folder(
            folder_name=folder_name,
            glob_pattern=glob_pattern,
            recursive=recursive,
        )
    )


def scan_file(folder_name="", glob_pattern="*", recursive=True):
    """
    Hanya mengumpulkan nama-nama file dalam folder dan subfolder.
    """
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

    Return :
    - String            : Apabila hanya url saja yg diberikan
    - List of etree     : Apabila xpath diberikan
    - False             : Apabila terjadi error
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
        str: Respon dari server dalam bentuk string.
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
    """
    return os.stat(filename).st_size


def get_filemtime(filename):
    """
    Mengambil informasi file size dalam bytes
    """
    return os.stat(filename).st_mtime_ns


def dict_first(d: dict) -> tuple:
    """
    Mengambil nilai (key, value) pertama dari dictionary dalam bentuk tuple
    """
    for k in d:
        return (k, d[k])


def random_bool() -> bool:
    """
    Menghasilkan nilai random True atau False
    fungsi ini merupakan fungsi tercepat untuk mendapatkan random bool
    """
    return bool(random.getrandbits(1))


def set_timeout(interval, func, args=None, kwargs=None):
    """
    menjalankan fungsi ketika sudah sekian detik.
    apabila timeout masih berjalan tapi kode sudah selesai dieksekusi semua,
    maka program tidak akan berhenti sampai timeout selesai, kemudian fungsi dijalankan,
    kemudian program dihentikan.
    """
    t = threading.Timer(interval=interval, function=func, args=args, kwargs=kwargs)
    t.start()
    # t.cancel() untuk menghentikan timer sebelum waktu habis
    return t


def get_class_method(cls):
    """
    Mengembalikan berupa tuple yg berisi list dari method dalam class
    """
    return tuple(generator.get_class_method(cls))


class ComparePerformance:
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
    """
    return sum(i) / len(i)


def exit_if_empty(*args):
    """
    keluar dari program apabila tidak ada variabl yg terisi
    """
    if not any(args):
        sys.exit()


def implode(iterable, separator="", start="", end=""):
    """
    Simplify Python join functions like PHP function.
    Iterable bisa berupa sets, tuple, list, dictionary.
    """
    if not is_iterable(iterable):
        iterable = {iterable}

    if isinstance(iterable, dict):
        iterable = iterable.values()

    result = start

    for index, value in enumerate(iterable):
        if index:
            result += separator
        result += str(value)

    result += end

    return result


def strtr(string: str, replacements: dict):
    """
    Melakukan translate kata untuk setiap items.

    replacements = {
        'satu': '1',
        'dua': '2',
    }
    """
    for i, v in replacements.items():
        string = string.replace(i, v)
    return string


def strtr_regex(string: str, replacements: dict, flags=0):
    """
    Melakukan multiple replacement untuk setiap list.

    regex_replacement_list = {
        r"regex": r"replacement",
        r"regex": r"replacement",
        r"regex": r"replacement",
    }
    """
    for i, v in replacements.items():
        string = re.sub(i, v, string, flags=flags)
    return string


def print_dir(var):
    """
    print possible property and method from variable
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
    """
    return isinstance(var, (tuple, list, dict, set))


def irange(start, finish, step=1):
    """
    improve python range() function untuk pengulangan menggunakan huruf
    contoh: irange('a', 'z')
    """
    return list(generator.irange(start, finish, step))


def serialize(data):
    """
    Mengubah variabel data menjadi string untuk yang dapat dibaca untuk disimpan.
    String yang dihasilkan berbentuk syntax YAML.
    """
    return yaml.safe_dump(data)


def unserialize(data):
    """
    Mengubah string data hasil dari serialize menjadi variabel.
    String data adalah berupa syntax YAML.
    """
    return yaml.safe_load(data)


def basename(path):
    """
    Mengembalikan nama file dari path
    """
    return os.path.basename(path)


def dirname(path):
    """
    Mengembalikan nama folder dari path
    """
    return os.path.dirname(path)


class Batchmaker:
    """
    Alat Bantu untuk membuat teks yang berulang. Gunakan {...-...}.
    contoh : Urutan {1-10} dan {5-1} dan {p-s} dan {A-D} saja.
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
