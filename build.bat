cd M:\python\ap
pyuic6 -x Landlord.ui -o output.py
pyinstaller --noconfirm --onefile Landlord.spec
MD M:\python\ap\dist\Landlord\pylabels
copy M:\python\ap\pylabels\*.* M:\python\ap\dist\Landlord\pylabels
dist\Landlord\Landlord.exe