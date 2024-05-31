cd prueba2
python -m venv entorno_con_3.11
 .\entorno_con_3.11\Scripts\Activate
C:\Users\Manuel\Desktop\Folder\x\entorno_con_3.11\Scripts\python.exe -m pip install --upgrade pippip install -r requirements.txt
reflex init
reflex export --frontend-only
Remove-Item -Recurse -Force public
mkdir public
Expand-Archive -Path frontend.zip -DestinationPath public
Remove-Item -Force frontend.zip
deactivate