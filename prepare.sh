#!/bin/sh

# Download winetricks
echo Downloading Winetricks...
curl -LO https://raw.githubusercontent.com/Winetricks/winetricks/refs/heads/master/src/winetricks
mv winetricks ./bin/
chmod +x ./bin/winetricks


# Download cabextract
echo Downloading Cabextract...
curl -LO https://www.cabextract.org.uk/cabextract-1.11-1.x86_64.rpm
bsdtar -xf cabextract-1.11-1.x86_64.rpm usr/bin/cabextract
mv usr/bin/cabextract ./bin/cabextract
chmod +x ./bin/cabextract
rm -rf usr
rm cabextract-1.11-1.x86_64.rpm


# Download Wine
echo Downloading Wine...
curl -LO https://github.com/Kron4ek/Wine-Builds/releases/download/10.17/wine-10.17-amd64-wow64.tar.xz
mkdir -p ./assets/wine && tar Jxf wine-10.17-amd64-wow64.tar.xz --strip-components=1 -C ./assets/wine
rm wine-10.17-amd64-wow64.tar.xz


# Download Visual C++ Redistributable Runtimes
echo Downloading Visual C++ Redistributable Runtimes...
curl -LO https://github.com/relativemodder/aegnux/releases/download/vcrbin/vcr.zip
mv ./vcr.zip ./assets/vcr.zip


# Download msxml3.zip bundle
echo Downloading msxml3 dlls...
curl -LO https://github.com/relativemodder/aegnux/releases/download/vcrbin/msxml3.dll
curl -LO https://github.com/relativemodder/aegnux/releases/download/vcrbin/msxml3r.dll
zip ./assets/msxml3.zip msxml3.dll msxml3r.dll
rm msxml3.dll
rm msxml3r.dll


# Download gdiplus.dll
echo Downloading gdiplus.dll...
curl -LO https://github.com/relativemodder/aegnux/releases/download/vcrbin/gdiplus.dll
mv gdiplus.dll ./assets/

echo --------------------------------------------
echo Done!
