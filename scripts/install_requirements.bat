@echo off
..\venv\Scripts\pip.exe install -r ..\requirements.txt --no-index --find-links ..\files\requirements
echo 脚本执行完成
pause>nul