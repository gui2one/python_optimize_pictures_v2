./env/Scripts/Activate.ps1

python ./bump_version.py

pyinstaller ./main.spec --noconfirm
# Run the built executable
$app_name = "picture_optimizer"
$exe = "./dist/$app_name/$app_name.exe"
Copy-Item -Recurse -Path "./res" -Destination "./dist/$app_name/res"
Copy-Item -Path "./app_version.txt" -Destination "./dist/$app_name"

& $exe