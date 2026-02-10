@echo off

if exist .venv\ (
    echo Virtual environment already existing.
) else (
    echo Creation of a virtual environment...
    python -m venv .venv
)

REM Installation des paquets requis
.venv\Scripts\pip.exe install -r requirements.txt

echo:
echo Installation completed successfully.
echo:
echo To run the program : .venv\Scripts\python.exe sources\main.py
echo: