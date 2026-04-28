@echo off
setlocal
echo [1/3] Instalando dependencias...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [2/3] Limpando build anterior...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Tera.spec del /f /q Tera.spec

echo [3/3] Gerando executavel...
python -m PyInstaller --noconfirm --windowed --name Tera ^
--add-data "templates;templates" ^
--add-data "static;static" ^
main.py
if errorlevel 1 goto :error

echo.
echo Executavel gerado em: dist\Tera\Tera.exe
exit /b 0

:error
echo Falha na geracao do executavel.
exit /b 1
