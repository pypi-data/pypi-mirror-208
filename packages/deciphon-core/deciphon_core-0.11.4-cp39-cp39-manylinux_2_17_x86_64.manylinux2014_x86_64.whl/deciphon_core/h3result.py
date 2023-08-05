import os
from pathlib import Path

from deciphon_core.cffi import ffi, lib
from deciphon_core.filepath import FilePath

__all__ = ["H3Result"]


class H3Result:
    def __init__(self, filepath: FilePath):
        self._cdata = ffi.NULL

        self._cdata = lib.h3c_result_new()
        if self._cdata == ffi.NULL:
            raise MemoryError()

        filepath = Path(filepath)

        fp = lib.fopen(bytes(filepath), b"rb")
        if fp == ffi.NULL:
            raise RuntimeError()

        rc = lib.h3c_result_unpack(self._cdata, fp)
        lib.fclose(fp)
        if rc != 0:
            raise RuntimeError()

    def print_targets(self, stream):
        fd = os.dup(stream.fileno())
        fp = lib.fdopen(fd, b"w")
        lib.h3c_result_print_targets(self._cdata, fp)
        lib.fclose(fp)

    def print_domains(self, stream):
        fd = os.dup(stream.fileno())
        fp = lib.fdopen(fd, b"w")
        lib.h3c_result_print_domains(self._cdata, fp)
        lib.fclose(fp)

    def print_targets_table(self, stream):
        fd = os.dup(stream.fileno())
        fp = lib.fdopen(fd, b"w")
        lib.h3c_result_print_targets_table(self._cdata, fp)
        lib.fclose(fp)

    def print_domains_table(self, stream):
        fd = os.dup(stream.fileno())
        fp = lib.fdopen(fd, b"w")
        lib.h3c_result_print_domains_table(self._cdata, fp)
        lib.fclose(fp)

    def __del__(self):
        if getattr(self, "_cdata", ffi.NULL) != ffi.NULL:
            lib.h3c_result_del(self._cdata)
