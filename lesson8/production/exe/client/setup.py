import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["common", "logs", "unit_tests"],
}
setup(
    name="mess_client",
    version="0.0.1",
    description="mess_client",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('client.py',
                            base='Win32GUI',
                            targetName='client.exe',
                            )]
)
