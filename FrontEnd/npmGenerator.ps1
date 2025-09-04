# build.ps1 - Corrected and streamlined script to sync React build with Django
# This version removes the direct HTML patching and only calls the Python script for a more reliable process.

# ----- 1. PATHS: Edit if needed -----
$frontend = "C:\Code projects\Tasin\FrontEnd"
$dist = Join-Path $frontend "dist"
$templates_react = "C:\Code projects\Tasin\backend\Tasin\react_accounts\templates\react"
$static_assets = "C:\Code projects\Tasin\backend\Tasin\react_accounts\static\react\assets"
$htmlPath = Join-Path $templates_react "index.html"
$pythonScriptPath = "C:\Code projects\Tasin\backend\Tasin\patch_html.py"

# ----- 2. Run npm build -----
Write-Host "`n===== Running npm run build... ====="
Push-Location $frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Error "npm build failed! Script stopped."
    Pop-Location
    exit 1
}
Pop-Location

# ----- 3. Copy index.html and vite.svg -----
Write-Host "`n===== Copying index.html and vite.svg... ====="
Copy-Item -Path (Join-Path $dist "index.html") -Destination $templates_react -Force
Copy-Item -Path (Join-Path $dist "vite.svg") -Destination $templates_react -Force

# ----- 4. Sync assets -----
Write-Host "`n===== Syncing assets directory... ====="
if (-not (Test-Path $static_assets)) {
    New-Item -ItemType Directory -Path $static_assets | Out-Null
}
Remove-Item -Path (Join-Path $static_assets '*') -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path (Join-Path $dist "assets\*") -Destination $static_assets -Recurse -Force

# ----- 5. Patch index.html using Python script -----
Write-Host "`n===== Patching index.html using Python script... ====="
python $pythonScriptPath
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python script failed! Script stopped."
    exit 1
}

Write-Host "`n===== All done! React build, copy, and Django HTML patch complete. =====`n"
