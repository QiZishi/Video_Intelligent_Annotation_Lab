set "NUITKA_ONEFILE_PARENT=%TEMP%"
nuitka ^
--onefile ^
--enable-plugin=pyqt5 ^
--windows-icon-from-ico=logo.ico ^
--output-dir=dist ^
--include-data-dir=config=config ^
--nofollow-import-to=tkinter,test ^
--windows-console-mode=disable ^
main.py
