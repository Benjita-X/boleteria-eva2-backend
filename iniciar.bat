@echo off
REM Inicia el servidor de desarrollo (PostgreSQL corre como servicio de Windows)
cd /d "%~dp0"
call venv\Scriptsctivate
python manage.py migrate
echo.
echo  Abrir: http://127.0.0.1:8000/   Swagger: http://127.0.0.1:8000/api/docs/
echo.
python manage.py runserver
