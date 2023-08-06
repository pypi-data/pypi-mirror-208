import importlib
import shutil
from typing import Union
try:
    try:
        from buffcall import get_mu
    except Exception:
        try:
            from buffercalc import get_mu
        except Exception:
            pyximport = importlib.import_module("pyximport")
            pyximport.install(inplace=True)
            from buffercalc import get_mu
except Exception:
    pass

from hackyargparser import add_sysargv, config
import sys
from datetime import datetime
import pandas as pd
from touchtouch import touch
from tqdm import tqdm
from uffspd import list_all_files
import os
from functools import cache
from getfilenuitkapython import get_filepath
from ctypes import wintypes, byref, WinDLL
from time import perf_counter



if __name__ == "__main__":
    config.helptext = r"""
      Example: copytool --src "C:\ProgramData\anaconda3\envs" --dst "e:\envbackup" --use_tqdm 1 --copy_date 1 --copy_permission 0 --overwrite 1
      --src                     str         (source folder)
      --dst                     str         (destination folder)
      --log                     str  ""     (csv log)
      --copy_date               int  0      (copy date stats)
      --copy_permission         int  0      (copy permissions)
      --use_tqdm                int  1      (show progress bar)
      --overwrite               int  1      (overwrite existing files in dst)
      --use_uffs                int  1      (use uffs to get a list of files)

      Press ENTER to exit! 
    """
    config.kill_when_not_there(("--src", "--dst"))
    config.stop_after_kill = True
conf = sys.modules[__name__]
conf.tq = None
conf.uffsfilepath = get_filepath("uffs.com")
try:
    O_BINARY = os.O_BINARY
except:
    O_BINARY = 0
READ_FLAGS = (
    os.O_RDONLY | O_BINARY
)  # | os.O_RANDOM #| os.O_NOINHERIT | os.O_RANDOM #os.O_SEQUENTIAL #| os.O_NOINHERIT | os.O_SEQUENTIAL #| os.O_SHORT_LIVED
WRITE_FLAGS = (
    os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
)  # | os.O_RANDOM   #| os.O_NOINHERIT | os.O_RANDOM #os.O_SEQUENTIAL# os.O_NOINHERIT |  # | os.O_SHORT_LIVED  #| os.O_TEMPORARY #| os.O_SHORT_LIVED
kernel32 = WinDLL("kernel32", use_last_error=True)
r"""
.\python.exe "C:\ProgramData\anaconda3\envs\dfdir\Lib\site-packages\copytool\__init__.py" --src "C:\ProgramData\anaconda3\envs" --dst "e:\envbackup1x9" --use_tqdm 1 --copy_date 1 --copy_permission 0 --overwrite 1
"""


def copy_subprocess(src, dst):
    shutil.copyfile(src,dst)

@cache
def mkdirsall(folderfipath):
    try:
        if not os.path.exists(folderfipath):
            os.makedirs(folderfipath)
        return folderfipath
    except Exception:
        return folderfipath


@cache
def t2stamp(t):
    return int(datetime.strptime(t.decode(), "%Y-%m-%d %H:%M:%S").timestamp())


def copyallfiles(
    aa_path,
    aa_archive,
    destfolder,
    buffer,
    copy_date,
    copy_permission,
    usetqm,
    aa_last_written: bytes | None = None,
    aa_last_accessed: bytes | None = None,
    aa_created: bytes | None = None,
    aa_attributes=None,
    overwrite=True,
):
    newfipath = os.path.normpath(os.path.join(destfolder, aa_path[2:].strip("\\/")))
    if not overwrite:
        if os.path.exists(newfipath):
            return pd.NA
    if aa_archive:
        folderfipath = os.path.dirname(newfipath)
        _ = mkdirsall(folderfipath)
        if usetqm:
            conf.tq.set_description(f"\r{str(aa_path).ljust(160)}")
        try:
            _copyfile(aa_path, newfipath, False, buffer)

        except Exception as fa:
            # print(fa)
            return pd.NA
        try:
            pr = int(aa_attributes)
            if pr != 32:
                if copy_date:
                    try:
                        set_times_on_file(
                            path=newfipath,
                            created_timestamp=t2stamp(aa_created),
                            access_timestamp=t2stamp(aa_last_accessed),
                            modify_timestamp=t2stamp(aa_last_written),
                        )
                    except Exception:
                        try:
                            os.utime(newfipath, (aa_last_accessed, aa_last_written))
                        except Exception:
                            pass
                    if copy_permission:
                        try:
                            os.chmod(newfipath, pr)
                        except Exception:
                            pass
            else:
                if copy_date:
                    try:
                        set_times_on_file(
                            path=newfipath,
                            created_timestamp=t2stamp(aa_created),
                            access_timestamp=t2stamp(aa_last_accessed),
                            modify_timestamp=t2stamp(aa_last_written),
                        )
                    except Exception:
                        try:
                            os.utime(newfipath, (aa_last_accessed, aa_last_written))
                        except Exception:
                            pass
        except Exception:
            pass
        if usetqm:
            conf.tq.update(1)
        return newfipath
    else:
        mkdirsall(newfipath)
        if usetqm:
            conf.tq.update(1)
    return pd.NA


class CTError(Exception):
    def __init__(self, errors):
        self.errors = errors


@cache
def get_mu2(buffer):
    return get_mu(buffer)


def copyfile(
    src: str,
    dst: str,
    copystat: bool = False,
    buffer: int = 1000 * 1024,
    copy_date=True,
    copy_permission=False,
):
    copyok = False
    closeok = False
    stat_ = None
    try:
        fin = os.open(src, READ_FLAGS)
        stat_ = os.fstat(fin)
        try:
            buffer = get_mu2(stat_.st_size)
        except Exception:
            buffer = 512000
        fout = os.open(dst, WRITE_FLAGS, stat_.st_mode)
        for x in iter(lambda: os.read(fin, buffer), b""):
            os.write(fout, x)
        copyok = True
    finally:
        try:
            os.close(fout)

        except Exception:
            pass
        try:
            os.close(fin)
            closeok = True
        except Exception:
            pass
    if copystat and copyok and closeok and stat_:
        if copy_date:
            try:
                set_times_on_file(
                    path=dst,
                    created_timestamp=stat_.st_ctime,
                    access_timestamp=stat_.st_atime,
                    modify_timestamp=stat_.st_mtime,
                )
            except Exception as fe:
                # print(fe)
                try:
                    os.utime(dst, (stat_.st_atime, stat_.st_mtime))
                except Exception:
                    pass
        if copy_permission:
            if stat_.st_mode != 33206:
                try:
                    os.chmod(dst, stat_.st_mode)
                except Exception:
                    pass
    if copyok:
        return True
    try:
        copy_subprocess(src, dst)
        return True
    except Exception:
        pass

    return False


def copytree(
    src: str,
    dst: str,
    ignore: Union[list, type(None)] = None,
    symlinks: bool = False,
    copystat: bool = False,
    ignore_exceptions=True,
    copy_date=False,
    copy_permission=False,
    overwrite=True,
        use_tqdm=True,
):
    if ignore is None:
        ignore = []
    if not os.path.exists(dst):
        os.makedirs(dst)
    names = iter(os.listdir(src))
    for name in names:
        if name in ignore:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isfile(srcname):
                if not overwrite:
                    if os.path.exists(dstname):
                        continue
                try:
                    copyfile(
                        srcname,
                        dstname,
                        copystat,
                        1000 * 1024,
                        copy_date,
                        copy_permission,
                    )
                except Exception as fa:
                    copy_subprocess(srcname, dstname)
                if use_tqdm:
                    conf.tq.set_description(f"\r{str(srcname).ljust(160)}")
                    conf.tq.update(1)

            elif os.path.isdir(srcname):
                copytree(
                    srcname,
                    dstname,
                    ignore,
                    symlinks,
                    copystat,
                    ignore_exceptions,
                    copy_date,
                    copy_permission,
                )
                if use_tqdm:
                    conf.tq.set_description(f"\r{str(srcname).ljust(160)}")
                    conf.tq.update(1)
            elif symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
                if use_tqdm:
                    conf.tq.set_description(f"\r{str(srcname).ljust(160)}")
                    conf.tq.update(1)
        except Exception as fe:
            if not ignore_exceptions:
                raise fe
            else:
                print((f"ERROR: {srcname} -> {dstname}"))
                print(fe)
                continue


def _copyfile(
    src: str, dst: str, copystat: bool = True, buffer: int = 1000 * 1024
) -> bool:
    copyok = False

    try:
        try:
            buffer = get_mu2(buffer)
        except Exception:
            buffer = 512000
        fin = os.open(src, READ_FLAGS)
        stat_ = os.fstat(fin)
        fout = os.open(dst, WRITE_FLAGS, stat_.st_mode)
        for x in iter(lambda: os.read(fin, buffer), b""):
            os.write(fout, x)
        copyok = True
    finally:
        try:
            os.close(fout)
        except Exception:
            pass
        try:
            os.close(fin)
        except Exception:
            pass
    if copyok:
        return True

    try:
        _ = copy_subprocess(src, dst)
        return True
    except Exception:
        pass

    return False


@add_sysargv
def get_all_files_on_hdd_and_copy(
    src: str = "",
    dst: str = "",
    log: str = "",
    copy_date: int = 1,
    copy_permission: int = 0,
    use_tqdm: int = 1,
    overwrite: int = 1,
    use_uffs:int=1,
):
    copy_date = bool(copy_date)
    copy_permission = bool(copy_permission)
    use_tqdm = bool(use_tqdm)
    overwrite = bool(overwrite)
    use_uffs = bool(use_uffs)
    start = perf_counter()
    src = os.path.normpath(src.strip("\"' "))
    dst = os.path.normpath(dst.strip("\"' "))
    if not use_uffs:
        if log:
            print("Log is only possible with uffs")
        copystat = True
        if not copy_date and not copy_permission:
            copystat = False
        if use_tqdm:
            conf.tq = tqdm(unit="")

        copytree(
            src,
            dst,
            ignore=None,
            symlinks=False,
            copystat=copystat,
            ignore_exceptions=True,
            copy_date=copy_date,
            copy_permission=copy_permission,
            overwrite=overwrite,
            use_tqdm=use_tqdm,
        )
        print("\n\n")
        print(perf_counter() - start)
        if use_tqdm:
            conf.tq.close()
        return
    print(f"Getting all files from {src}...\n")
    try:
        dframetemp = list_all_files(
            path2search=src,
            file_extensions=None,
            uffs_com_path=conf.uffsfilepath,
        )
    except Exception:
        conf.uffsfilepath = get_filepath("uffs.com")
        dframetemp = list_all_files(
            path2search=src,
            file_extensions=None,
            uffs_com_path=conf.uffsfilepath,
        )

    dframetemp["aa_copied"] = pd.NA

    totallen = len(dframetemp)
    if use_tqdm:
        conf.tq = tqdm(total=totallen, unit="")
    dframetemp["aa_copied"] = dframetemp.apply(
        lambda fi: copyallfiles(
            fi.aa_path,
            fi.aa_archive,
            dst,
            fi.aa_size_on_disk,
            copy_date,
            copy_permission,
            use_tqdm,
            fi.aa_last_written,
            fi.aa_last_accessed,
            fi.aa_created,
            fi.aa_attributes,
            overwrite,
        ),
        axis=1,
    )
    if use_tqdm:
        conf.tq.close()
    print("\n\n")
    print(perf_counter() - start)
    if log:
        logfile = os.path.normpath(log)
        touch(logfile)
        dframetemp.to_csv(logfile)
    return dframetemp


def set_times_on_file(
    path: str,
    created_timestamp: int = None,
    access_timestamp: int = None,
    modify_timestamp: int = None,
):
    timestamp = int((created_timestamp * 1e7) + 116444736e9)
    ctime = wintypes.FILETIME(timestamp & 0xFFFFFFFF, timestamp >> 32)
    handle = kernel32.CreateFileW(path, 256, 0, None, 3, 128, None)
    kernel32.SetFileTime(handle, byref(ctime), None, None)
    kernel32.CloseHandle(handle)
    os.utime(path, (access_timestamp, modify_timestamp))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_all_files_on_hdd_and_copy()
        try:
            sys.exit(0)
        finally:
            os._exit(0)
