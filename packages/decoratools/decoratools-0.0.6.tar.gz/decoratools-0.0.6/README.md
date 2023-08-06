Collection of useful decorators

-----

# Installation

```bash
pip install decoratools
```

# Usage

## `capi`

Interface with [`statx(2)`](https://man7.org/linux/man-pages/man2/statx.2.html):

```python
import ctypes
from argparse import ArgumentParser

from decoratools.capi import ARRAY, structure

LIBC = ctypes.CDLL("libc.so.6")
AT_FDCDW = -100
STATX_BASIC_STATS = 0x000007FF


@structure
class StatxTimestamp:
    tv_sec: ctypes.c_int64
    tv_nsec: ctypes.c_uint32
    __statx_timestamp_pad1: ctypes.c_int32


@structure
class Statx:
    stx_mask: ctypes.c_uint32
    stx_blksize: ctypes.c_uint32
    stx_attributes: ctypes.c_uint64
    stx_nlink: ctypes.c_uint32
    stx_uid: ctypes.c_uint32
    stx_gid: ctypes.c_uint32
    stx_mode: ctypes.c_uint16
    __statx_pad1: ctypes.c_uint16
    stx_ino: ctypes.c_uint64
    stx_size: ctypes.c_uint64
    stx_blocks: ctypes.c_uint64
    stx_attributes_mask: ctypes.c_uint64

    stx_atime: StatxTimestamp
    stx_btime: StatxTimestamp
    stx_ctime: StatxTimestamp
    stx_mtime: StatxTimestamp

    stx_rdev_major: ctypes.c_uint32
    stx_rdev_minor: ctypes.c_uint32

    stx_dev_major: ctypes.c_uint32
    stx_dev_minor: ctypes.c_uint32

    stx_mnt_id: ctypes.c_uint64

    stx_dio_mem_align: ctypes.c_uint32
    stx_dio_offset_align: ctypes.c_uint32

    __statx_pad2: ARRAY[ctypes.c_uint64, 12]


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("path", help="path to statx")
    args = parser.parse_args()

    statx = Statx()
    rc = LIBC.statx(AT_FDCDW, ctypes.c_char_p(args.path.encode()), 0, STATX_BASIC_STATS, ctypes.byref(statx))
    if rc != 0:
        raise RuntimeError("statx: failed")
    print(statx)
```

```console
$ python statx.py /dev/null
Statx(stx_mask=6143, stx_blksize=4096, stx_attributes=0, stx_nlink=1, stx_uid=0, stx_gid=0, stx_mode=8630, _Statx__statx_pad1=0, stx_ino=4, stx_size=0, stx_blocks=0, stx_attributes_mask=2109552, stx_atime=StatxTimestamp(tv_sec=1672527600, tv_nsec=0, _StatxTimestamp__statx_timestamp_pad1=0), stx_btime=StatxTimestamp(tv_sec=0, tv_nsec=0, _StatxTimestamp__statx_timestamp_pad1=0), stx_ctime=StatxTimestamp(tv_sec=1672527600, tv_nsec=0, _StatxTimestamp__statx_timestamp_pad1=0), stx_mtime=StatxTimestamp(tv_sec=1672527600, tv_nsec=0, _StatxTimestamp__statx_timestamp_pad1=0), stx_rdev_major=1, stx_rdev_minor=3, stx_dev_major=0, stx_dev_minor=5, stx_mnt_id=22, stx_dio_mem_align=0, stx_dio_offset_align=0, _Statx__statx_pad2=<decoratools.capi.c_ulong_Array_12 object at 0x7efe94be0a70>)
```
