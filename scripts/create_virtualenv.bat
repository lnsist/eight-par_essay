@echo off
set /P P_HOME=<1.PYTHON_HOME.txt
cd ..
%P_HOME%/Scripts/virtualenv.exe --never-download -p %P_HOME%/python.exe ./venv
echo 脚本执行完成
pause>nul