import ctypes
import ctypes.util
import os

from .socket import get_process_socket
from .unshare import CLONE_NEWNS, CLONE_NEWUSER

SYSCALL_PIDFD_OPEN = 434

libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)


def get_fd_for_process(pid: int) -> int:
    """Get a file descriptor for a process."""

    fd = libc.syscall(SYSCALL_PIDFD_OPEN, pid, 0, None, None, None)
    if fd < 0:
        errno = ctypes.get_errno()
        raise OSError(errno, f"pidfd_open failed for pid {pid}: {os.strerror(errno)}")

    return fd


def set_namespace(fd: int) -> None:
    """Enter the process namespace of a given PID."""

    if libc.setns(fd, CLONE_NEWUSER | CLONE_NEWNS) < 0:
        errno = ctypes.get_errno()
        raise OSError(errno, f"setns failed: {os.strerror(errno)}")


def set_namespace_pid(pid: int) -> None:
    fd = get_fd_for_process(pid)
    return set_namespace(fd)


def enter_process(pid: int, no_shell, command) -> None:
    """Enter the process namespace of a given PID."""

    fd = get_fd_for_process(pid)
    set_namespace(fd)

    conn = get_process_socket(pid)
    conn.sendall(b"info")
    data = conn.recv(1024)
    conn.close()
    os.chroot(data.decode("utf-8"))
    os.chdir("/")
    if no_shell:
        command = command.split()
        os.execvp(command[0], command[:])
    else:
        os.execvp("/bin/sh", ["sh", "-c", command])
