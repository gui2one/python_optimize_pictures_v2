./env/Scripts/Activate.ps1

pyinstaller ./main.spec --noconfirm
# Run the built executable
$app_name = "gui2one_picture_converter"
$exe = "./dist/main/$app_name.exe"

& $exe