import os
import dill
import zipfile
from typing import Optional, Union

from utils import File


class ZipFormatFile(File):
    def __init__(self, path, password=None, mode="w"):
        # print(mode)
        super().__init__(path)

        self._currentDir = ""
        self.zipfile = zipfile.ZipFile(path, mode)
        self.password = password

    def chdir(self, path):
        path = self.get_fp(path)
        self._currentDir = path

    def getcwd(self):
        return self._currentDir

    def split_path(self, path: str):
        # if path.count('/') >= 2:
        #     paths = self.os.path.split(path)
        #     s_paths = self.split_path(paths[0])
        #     return (s_paths[0], s_paths[1], paths[1])
        # elif path.count('/') == 1:
        #     return self.os.path.split(path)
        # else:
        #     return [path]
        return tuple(path.replace("\\", "/").split("/"))

    def get_fp(self, fp=None):
        if not fp:
            fp = self._currentDir
        else:
            if not self.os.path.isabs(fp):
                fp = self.os.path.join(self._currentDir, fp).replace("\\", "/")

        fp = "/" + fp

        fp = fp.replace("\\", "/")

        if fp[-1] == "/" and fp != "/":
            fp = fp[:-1]

        return fp[1:]

    def listdir(self, fp=None):
        fp = self.get_fp(fp)
        list_ = []
        # print(self.zipfile.infolist())
        for item in self.zipfile.infolist():
            if len(self.split_path(item.filename)) >= 2:
                # print(item.filename)
                # print(self.split_path(item.filename))
                # print(self.os.path.split(item.filename))
                s_path2 = self.split_path(item.filename)[:-1]
                s_path3 = self.os.path.join(
                    s_path2[0] if len(s_path2) >= 2 else "", *[s_path2[1]] if len(s_path2) >= 3 else []). \
                    replace("\\", "/")

                # print("SPath:", s_path2)
                # print("SPath 3:", s_path3)
                if s_path2:
                    if s_path3 == fp:
                        list_.append(self.split_path(item.filename)[-2])
            if self.os.path.join(*self.os.path.split(item.filename)[:-1]) == fp:
                list_.append(self.os.path.split(item.filename)[-1])
        return list_

    def listfiles(self, fp=None):
        fp = self.get_fp(fp)

        list_ = []
        # print(self.zipfile.infolist())
        # for item in self.zipfile.infolist():
        #     print("File [x] == [ ]:", self.os.path.join(*self.os.path.split(item.filename)[:-1]))
        #     print("File [ ] == [x]:", fp)
        #     if self.os.path.join(*self.os.path.split(item.filename)[:-1]) == fp:
        #         if not item.is_dir():
        #             list_.append(self.os.path.split(item.filename)[-1])

        for item in self.zipfile.infolist():
            # if len(self.split_path(item.filename)) >= 2:
            #     print(item.filename)
            #     print(self.split_path(item.filename))
            #     print(self.os.path.split(item.filename))
            #     s_path2 = self.split_path(item.filename)[:-1]
            #     s_path3 = self.os.path.join(
            #         s_path2[0] if len(s_path2) >= 2 else "", *[s_path2[1]] if len(s_path2) >= 3 else []). \
            #         replace("\\", "/")
            #
            #     print("SPath:", s_path2)
            #     print("SPath 3:", s_path3)
            #     if s_path2:
            #         if s_path3 == fp:
            #             list_.append(self.split_path(item.filename)[-2])
            file1 = self.os.path.join(*self.os.path.split(item.filename)[:-1])
            if item.filename[-1] != "/":
                if item.filename.count("/") > 0:
                    file2 = item.filename.split("/")[:-1]
                else:
                    file2 = ""
            else:
                file2 = item.filename.split("/")[:-2]

            file2 = fp
            # print("FILE [x] == [ ]:", file1)
            # print("FILE [ ] == [x]:", file2)
            # print("ITEM IS NOT DIR:", not item.is_dir())
            # print()
            if file1 == file2:
                if not item.is_dir():
                    list_.append(self.os.path.split(item.filename)[-1])
        return list_

    def listdirs(self, fp=None):
        fp = self.get_fp(fp)

        list_ = []
        # print(self.zipfile.infolist())
        for item in self.zipfile.infolist():
            # print("ITEM.FILENAME", item.filename)
            # print("SPLIT PATH", self.split_path(item.filename))
            # print("OS SPLIT", self.os.path.split(item.filename))
            if item.filename.count("/") > 0:
                s_path2 = self.split_path(item.filename)[:-1]
                s_path3 = "/".join(s_path2[:-1])

                # print("S_PATH:", s_path2)
                # print("S_PATH3:", s_path3)
                if s_path2:
                    if s_path3 == fp:
                        if item.filename[-1] == "/":
                            append_value1 = self.split_path(item.filename[:-1])[-1]
                        else:
                            append_value1 = self.split_path(item.filename)[-2]
                        if append_value1 not in list_ + [""]:
                            list_.append(append_value1)
            else:  # if self.os.path.join(*self.os.path.split(item.filename)[:-1]) == fp:
                if item.is_dir():
                    append_value2 = self.os.path.split(item.filename)[-1]
                    if append_value2 not in list_ + [""]:
                        list_.append(append_value2)
        return list_

    def close(self):
        self.zipfile.close()


# noinspection PyProtectedMember
class ZippedFile(object):
    def __init__(self, zip_file: ZipFormatFile, path: str, pwd=None):
        self.zipFormatFile = zip_file
        self.path = path
        self.password = pwd

        self.fileName = os.path.split(path)[-1]

        self._fd: Optional[zipfile.ZipExtFile] = None
        self._fileOpen = False

    def read(self, size=None):
        with self.zipFormatFile.zipfile.open(self.zipFormatFile.get_fp(self.path)[:], "r") as file:
            data = file.read(size)
        return data

    def readline(self, size=None):
        with self.zipFormatFile.zipfile.open(self.zipFormatFile.get_fp(self.path)[:], "r") as file:
            data = file.readline(limit=size)
        return data

    def write(self, data: Union[bytes, bytearray]):
        with self.zipFormatFile.zipfile.open(self.path, "w", self.password) as file:
            file.write(data)

    def __repr__(self):
        return f"<ZippedFile '{self.path}'>"

    #
    # def __gt__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.fileName > other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.fileName > other.fileName
    #
    # def __ge__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.fileName >= other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.fileName >= other.fileName

    def __lt__(self, other):
        if type(other) == ZippedDirectory:
            other: ZippedDirectory
            return int(os.path.splitext(self.fileName)[0]) < int(os.path.splitext(other.dirName)[0])
        elif type(other) == ZippedFile:
            other: ZippedFile
            return int(os.path.splitext(self.fileName)[0]) < int(os.path.splitext(other.fileName)[0])
    #
    # def __le__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.fileName <= other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.fileName <= other.fileName
    #
    # def __eq__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return False
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.fileName == other.fileName
    #
    # def __ne__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return True
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.fileName != other.fileName


# noinspection PyProtectedMember
class ZippedDirectory(object):
    def __init__(self, zip_file: ZipFormatFile, path, pwd=None):
        import os
        self.zipFormatFile = zip_file
        self.path = path
        self.password = pwd
        self.dirName = os.path.split(path)[-1]

        self.os = os

    def create(self):
        pass

    def listdir(self):
        return self.index()

    def index(self):
        list_ = []
        # print(self.path)
        # print(self.zipFormatFile.listdir(self.path))
        # print(self.zipFormatFile.listdirs(self.path))
        for dir_ in self.zipFormatFile.listdirs(self.path):
            # print("LIST DIRS IN FOLDER", self.path, "ARE", self.zipFormatFile.listdirs(self.path))
            list_.append(
                ZippedDirectory(self.zipFormatFile, self.zipFormatFile.get_fp(os.path.join(self.path, dir_)),
                                self.password))

        for file in self.zipFormatFile.listfiles(self.path):
            # print("LIST FILES IN FOLDER", self.path, "ARE", self.zipFormatFile.listfiles(self.path))
            list_.append(
                ZippedFile(self.zipFormatFile, self.zipFormatFile.get_fp(os.path.join(self.path, file)), self.password))
        return list_

    def listfiles(self):
        # print("LIST FILES IN FOLDER", self.path, "ARE", self.zipFormatFile.listfiles(self.path))
        return [
            ZippedFile(self.zipFormatFile, self.os.path.join(self.path, file).replace("\\", "/"), self.password)
            for file in self.zipFormatFile.listfiles(self.path)]

    def listdirs(self):
        return [
            ZippedDirectory(self.zipFormatFile, self.os.path.join(self.path, dir_).replace("\\", "/"), self.password)
            for dir_ in self.zipFormatFile.listdirs(self.path)]

    def __repr__(self):
        return f"<ZippedDirectory '{self.path}'>"

    # def __gt__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.dirName > other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.dirName > other.fileName
    #
    # def __ge__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.dirName >= other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.dirName >= other.fileName

    def __lt__(self, other):
        if type(other) == ZippedDirectory:
            other: ZippedDirectory
            return int(os.path.splitext(self.dirName)[0]) < int(os.path.splitext(other.dirName)[0])
        elif type(other) == ZippedFile:
            other: ZippedFile
            return int(os.path.splitext(self.dirName)[0]) < int(os.path.splitext(other.fileName)[0])

    # def __le__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.dirName <= other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return self.dirName <= other.fileName
    #
    # def __eq__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.dirName == other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return False
    #
    # def __ne__(self, other):
    #     if type(other) == ZippedDirectory:
    #         other: ZippedDirectory
    #         return self.dirName != other.dirName
    #     elif type(other) == ZippedFile:
    #         other: ZippedFile
    #         return True


class ZipFile(ZippedDirectory):
    def __init__(self, path, mode="r", password=None):
        # print(mode)
        import os
        mode = mode.replace("b", "")
        mode = mode.replace("+", "")
        zip_file = ZipFormatFile(path, mode=mode, password=password)
        if password:
            zip_file.zipfile.setpassword(password)
        super().__init__(zip_file, "", pwd=password)

        self.absPath: str = os.path.abspath(path)
        try:
            self.relPath: str = os.path.relpath(path)
        except ValueError:
            self.relPath: Optional[str] = None


class DillFile(object):
    def __init__(self, filename):
        self._contents = {}
        self.data: dict = {}
        self.path = filename

    def save(self):
        with open(self.path, "wb+") as file:
            dill.dump(self.data, file)
            file.close()

    def load(self):
        with open(self.path, "rb") as file:
            data = dill.load(file)
            file.close()

        self.data = data

        if type(self.data) is not dict:
            data = {}
        return data


if __name__ == '__main__':
    data_ = {"string": "Hallo", "int": 39, "float": 43.6, "boolean": True, "object": print,
             "dict": {"Hoi": 3, "Hallo": False,
                      "FolderLOL": {"File1": "Hoi", "Number": 584.5, "Dictionary": {"Score": 48376, "Lives": 6}}},
             "list": [485.4, False, 95, "Hoi", 40], "lambda": lambda name: print(f"Hello {name}")}
    nzt_file = DillFile("Test.nzt")
    nzt_file.data = data_
    nzt_file.save()

    nzt_file2 = DillFile("Test.nzt")
    nzt_file2.load()
    # print(repr(data_))
    # print(repr(nzt_file2.data))

    print("https://www.google.com")
