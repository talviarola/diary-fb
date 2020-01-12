from setuptools import setup
from cx_Freeze import setup, Executable

packages = ["os", "unicodedata", "re", "urllib", "urllib3", "json", "hashlib", "tkinter"]

setup(
    name='diary-fb',
    version='',
    packages=[''],
    url='',
    license='',
    author='wtf post-ap 2020',
    author_email='',
    description='',
    options={"build_exe": {
        'packages': packages,
        'include_msvcr': True,
    }},
    executables=[Executable("gui.py", base="Win32GUI")]
)
