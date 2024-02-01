$activateScriptPath = ".\sore\Scripts\Activate"
$djangoApppath = ".\soreapp\"
$fusekiServerPath = ".\apache-jena-fuseki-4.10.0\"

if (Test-Path $activateScriptPath) 
{
    & $activateScriptPath
    Write-Host "Virtual environment activated successfully."
} 
else 
{
    Write-Host "Error: Virtual environment could not be activated."
}

if (Test-Path $djangoAppPath) 
{
    cd $djangoAppPath
    Start-Process "cmd" -ArgumentList "/c python manage.py runserver" -NoNewWindow
    cd ..
    Write-Host "Django application started successfully."
} 
else 
{
    Write-Host "Error: Django application could not be started."
}

Start-Sleep -Seconds 5

if (Test-Path $fusekiServerPath) 
{
    cd $fusekiServerPath
    Start-Process "cmd" -ArgumentList "/c .\fuseki-server.bat --update --mem /ds" -NoNewWindow
    Write-Host "Fuseki server started successfully."
} 
else 
{
    Write-Host "Error: Fuseki server could not be started."
}