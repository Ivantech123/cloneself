@echo off
setlocal enabledelayedexpansion

echo Checking Python installation...

:: Проверяем наличие Python
python --version >nul 2>&1
if not errorlevel 1 (
    echo Python already installed
    goto :setup
)

echo Python not found. Downloading Python installer...

:: Создаем временную директорию
set "temp_dir=%temp%\python_install"
mkdir "%temp_dir%" 2>nul

:: Скачиваем Python
set "python_url=https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
set "installer=%temp_dir%\python_installer.exe"

:: Используем PowerShell для загрузки
powershell -Command "& {Invoke-WebRequest -Uri '%python_url%' -OutFile '%installer%'}"

if not exist "%installer%" (
    echo Failed to download Python installer
    goto :error
)

echo Installing Python...
:: Устанавливаем Python с нужными опциями
"%installer%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Проверяем успешность установки
python --version >nul 2>&1
if errorlevel 1 (
    echo Python installation failed
    goto :error
)

echo Python installed successfully
goto :cleanup

:error
echo An error occurred during installation
exit /b 1

:cleanup
:: Удаляем временные файлы
rmdir /s /q "%temp_dir%" 2>nul

:setup
:: Запускаем setup.bat
echo Running setup script...
call setup.bat

echo.
echo Installation completed successfully!
echo You can now run start.bat to launch the bot
pause
exit /b 0
