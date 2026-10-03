Remove-Item -Recurse -Force dist, build, release
Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory | Remove-Item -Force -Recurse
pyinstaller --onefile main.py

Write-Host "Copying files into 'release' directory..."
# Copy the config directory to the release folder
Copy-Item -Path .\config -Destination .\release\config -Recurse -Force

# Wait for a few seconds (adjust the time as needed)
Start-Sleep -Seconds 3

# Copy and rename the main.exe file to the release folder
Copy-Item -Path .\dist\main.exe -Destination .\release\reis_file_utils.exe -Force
Write-Host "Complete."