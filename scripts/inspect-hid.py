"""Read K83 HID metadata and indexed string 4. Requires Windows and Python 3."""

import ctypes
from ctypes import wintypes
import json
import re
import sys


def inspect():
    if sys.platform != "win32":
        raise RuntimeError("This diagnostic requires Windows.")

    hid = ctypes.WinDLL("hid.dll", use_last_error=True, winmode=0x800)
    setup = ctypes.WinDLL("setupapi.dll", use_last_error=True, winmode=0x800)
    kernel = ctypes.WinDLL("kernel32.dll", use_last_error=True, winmode=0x800)
    config = ctypes.WinDLL("cfgmgr32.dll", use_last_error=True, winmode=0x800)

    def bind(library, name, result, *arguments):
        function = getattr(library, name)
        function.restype = result
        function.argtypes = arguments
        return function

    class Guid(ctypes.Structure):
        _fields_ = [
            ("data1", wintypes.DWORD),
            ("data2", wintypes.WORD),
            ("data3", wintypes.WORD),
            ("data4", ctypes.c_ubyte * 8),
        ]

    class InterfaceData(ctypes.Structure):
        _fields_ = [
            ("size", wintypes.DWORD),
            ("guid", Guid),
            ("flags", wintypes.DWORD),
            ("reserved", ctypes.c_size_t),
        ]

    class DeviceData(ctypes.Structure):
        _fields_ = [
            ("size", wintypes.DWORD),
            ("guid", Guid),
            ("devinst", wintypes.DWORD),
            ("reserved", ctypes.c_size_t),
        ]

    class Attributes(ctypes.Structure):
        _fields_ = [
            ("size", wintypes.ULONG),
            ("vid", wintypes.USHORT),
            ("pid", wintypes.USHORT),
            ("version", wintypes.USHORT),
        ]

    get_guid = bind(hid, "HidD_GetHidGuid", None, ctypes.POINTER(Guid))
    get_set = bind(setup, "SetupDiGetClassDevsW", wintypes.HANDLE,
                   ctypes.POINTER(Guid), wintypes.LPCWSTR, wintypes.HWND, wintypes.DWORD)
    enum_interface = bind(setup, "SetupDiEnumDeviceInterfaces", wintypes.BOOL,
                          wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(Guid),
                          wintypes.DWORD, ctypes.POINTER(InterfaceData))
    get_detail = bind(setup, "SetupDiGetDeviceInterfaceDetailW", wintypes.BOOL,
                      wintypes.HANDLE, ctypes.POINTER(InterfaceData), ctypes.c_void_p,
                      wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                      ctypes.POINTER(DeviceData))
    destroy_set = bind(setup, "SetupDiDestroyDeviceInfoList", wintypes.BOOL, wintypes.HANDLE)
    get_parent = bind(config, "CM_Get_Parent", wintypes.ULONG,
                      ctypes.POINTER(wintypes.DWORD), wintypes.DWORD, wintypes.ULONG)
    get_id = bind(config, "CM_Get_Device_IDW", wintypes.ULONG,
                  wintypes.DWORD, wintypes.LPWSTR, wintypes.ULONG, wintypes.ULONG)
    open_device = bind(kernel, "CreateFileW", wintypes.HANDLE, wintypes.LPCWSTR,
                       wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
                       wintypes.DWORD, wintypes.HANDLE)
    close_device = bind(kernel, "CloseHandle", wintypes.BOOL, wintypes.HANDLE)
    get_attributes = bind(hid, "HidD_GetAttributes", ctypes.c_ubyte,
                          wintypes.HANDLE, ctypes.POINTER(Attributes))
    get_preparsed = bind(hid, "HidD_GetPreparsedData", ctypes.c_ubyte,
                         wintypes.HANDLE, ctypes.POINTER(ctypes.c_void_p))
    free_preparsed = bind(hid, "HidD_FreePreparsedData", ctypes.c_ubyte, ctypes.c_void_p)
    get_caps = bind(hid, "HidP_GetCaps", wintypes.LONG,
                    ctypes.c_void_p, ctypes.POINTER(wintypes.USHORT))
    get_string = bind(hid, "HidD_GetIndexedString", ctypes.c_ubyte,
                      wintypes.HANDLE, wintypes.ULONG, ctypes.c_void_p, wintypes.ULONG)

    def checked(result, operation):
        if not result:
            error = ctypes.get_last_error()
            raise OSError(error, operation + " failed. " + ctypes.FormatError(error))

    def find_usb_parent(devinst):
        for _ in range(16):
            name = ctypes.create_unicode_buffer(512)
            status = get_id(devinst, name, len(name), 0)
            if status:
                raise RuntimeError(f"CM_Get_Device_IDW returned {status}")
            if re.fullmatch(r"USB\\VID_1B1C&PID_1B42\\[^\\]+", name.value, re.I):
                return name.value
            parent = wintypes.DWORD()
            if get_parent(ctypes.byref(parent), devinst, 0):
                return None
            devinst = parent.value
        return None

    guid = Guid()
    get_guid(ctypes.byref(guid))
    device_set = get_set(ctypes.byref(guid), None, None, 0x12)
    invalid = ctypes.c_void_p(-1).value
    if device_set in (None, invalid):
        checked(False, "SetupDiGetClassDevsW")
    result = []
    try:
        index = 0
        while True:
            interface = InterfaceData()
            interface.size = ctypes.sizeof(interface)
            if not enum_interface(device_set, None, ctypes.byref(guid), index,
                                  ctypes.byref(interface)):
                if ctypes.get_last_error() == 259:
                    break
                checked(False, "SetupDiEnumDeviceInterfaces")
            index += 1
            needed = wintypes.DWORD()
            get_detail(device_set, ctypes.byref(interface), None, 0,
                       ctypes.byref(needed), None)
            if needed.value < 8:
                checked(False, "SetupDiGetDeviceInterfaceDetailW size")
            detail = ctypes.create_string_buffer(needed.value)
            ctypes.cast(detail, ctypes.POINTER(wintypes.DWORD))[0] = (
                8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
            )
            device = DeviceData()
            device.size = ctypes.sizeof(device)
            checked(get_detail(device_set, ctypes.byref(interface), detail, needed.value,
                               None, ctypes.byref(device)),
                    "SetupDiGetDeviceInterfaceDetailW")
            path = ctypes.wstring_at(ctypes.addressof(detail) + 4)
            if not re.search(r"hid#vid_1b1c&pid_1b42&(mi_00&col05|mi_01)#", path, re.I):
                continue
            usb_parent = find_usb_parent(device.devinst)
            if not usb_parent:
                raise RuntimeError("The target collection has no matching USB parent.")
            handle = open_device(path, 0, 3, None, 3, 0, None)
            if handle in (None, invalid):
                checked(False, "CreateFileW with desired access 0")
            try:
                attributes = Attributes()
                attributes.size = ctypes.sizeof(attributes)
                checked(get_attributes(handle, ctypes.byref(attributes)),
                        "HidD_GetAttributes")
                preparsed = ctypes.c_void_p()
                checked(get_preparsed(handle, ctypes.byref(preparsed)),
                        "HidD_GetPreparsedData")
                try:
                    caps = (wintypes.USHORT * 32)()
                    status = get_caps(preparsed, caps) & 0xFFFFFFFF
                    if status != 0x00110000:
                        raise RuntimeError(f"HidP_GetCaps NTSTATUS 0x{status:08X}")
                    record = {
                        "path": path,
                        "usb_parent": usb_parent,
                        "vendor_id": attributes.vid,
                        "product_id": attributes.pid,
                        "revision": f"{attributes.version:04x}",
                        "usage_page": caps[1],
                        "usage": caps[0],
                        "input_bytes": caps[2],
                        "output_bytes": caps[3],
                        "feature_bytes": caps[4],
                    }
                    if (attributes.vid, attributes.pid, caps[1], caps[0]) == (
                        0x1B1C, 0x1B42, 0xFFC2, 4
                    ):
                        buffer = ctypes.create_unicode_buffer(256)
                        ctypes.set_last_error(0)
                        checked(get_string(handle, 4, ctypes.byref(buffer),
                                           ctypes.sizeof(buffer)),
                                "HidD_GetIndexedString(4)")
                        record["protocol"] = buffer.value
                    result.append(record)
                finally:
                    free_preparsed(preparsed)
            finally:
                close_device(handle)
    finally:
        destroy_set(device_set)
    return {"collections": result}


if __name__ == "__main__":
    try:
        print(json.dumps(inspect(), indent=2))
    except (OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
