@echo off
call clear_requirements.bat
for /f "delims=" %%i in (..\requirements.txt ) do (
if "%%i" NEQ "" (..\venv\Scripts\pip.exe download  %%i -d ..\files\requirements)
)
if exist "..\files\requirements_special" (xcopy ..\files\requirements_special ..\files\requirements /s /e /y) 
echo �ű�ִ�����
pause>nul