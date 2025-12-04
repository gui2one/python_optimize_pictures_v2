./env/Scripts/Activate.ps1

pyinstaller ./main.spec --noconfirm --clean
# Run the built executable
$app_name = "picture_optimizer"
$exe = "./dist/$app_name/$app_name.exe"

& $exe