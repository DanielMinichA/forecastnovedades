@echo off
cd /d "%~dp0"
if not defined DOCUMENTS_PATH set "DOCUMENTS_PATH=C:\Users\corebi\Desktop\CoreBI\FORECAST NOVEDADES"
if not defined OLLAMA_MODEL set "OLLAMA_MODEL=llama3.2"
py -3 app.py
pause
