cd M:\python\ap
pyuic6 -x Landlord.ui -o output.py
DEL .\Landlord\LandlordIcons.py
pyside6-rcc .\res\Landlord.qrc -o Landlord\LandlordIcons.py
pyinstaller --noconfirm Landlord.spec
MD M:\python\ap\dist\Landlord\pylabels
copy M:\python\ap\pylabels\*.* M:\python\ap\dist\Landlord\pylabels
dist\Landlord\Landlord.exe