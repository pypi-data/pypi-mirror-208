import ctypes
import os
from pathlib import Path

from .mount import MS_PRIVATE, MS_REC, mount
from .verbose import verbose

CLONE_NEWNS = 0x20000
CLONE_NEWCGROUP = 0x2000000
CLONE_NEWUTS = 0x4000000
CLONE_NEWIPC = 0x8000000
CLONE_NEWUSER = 0x10000000
CLONE_NEWPID = 0x20000000
CLONE_NEWNET = 0x40000000
CLONE_NEWTIME = 0x80000000


libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

libc.unshare.argtypes = (ctypes.c_int,)
libc.unshare.restype = ctypes.c_int


def unshare(flags: int):
    ret = libc.unshare(flags)
    if ret == -1:
        errno = ctypes.get_errno()
        raise OSError(
            errno,
            f"Fail to unshare with flags {flags:#x}: {os.strerror(errno)}",
        )


def rewrite_uid_map(uid, gid):
    Path("/proc/self/uid_map").write_text(f"0 {uid} 1")
    Path("/proc/self/setgroups").write_text("deny")
    Path("/proc/self/gid_map").write_text(f"0 {gid} 1")


def setup_user_level_root():
    """Create user and mount namespaces and map the current user to root."""
    uid, gid = os.geteuid(), os.getegid()
    verbose("Creating user and mount namespaces")
    unshare(CLONE_NEWNS | CLONE_NEWUSER)
    mount(None, "/", None, MS_REC | MS_PRIVATE)
    rewrite_uid_map(uid, gid)
