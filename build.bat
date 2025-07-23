@echo off
cd /d "%~dp0"
pyinstaller --noconfirm --onefile --windowed ^
--name "ATFISHNVRP BY NTSHOP" ^
--icon "lgo.ico" ^
--add-data "image;image" ^
main.py
pause
