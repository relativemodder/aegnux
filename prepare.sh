#!/bin/sh


# Download Kitty Binary
echo Downloading Kitty Binary...
curl -LO https://github.com/kovidgoyal/kitty/releases/download/v0.43.1/kitty-0.43.1-x86_64.txz
mkdir -p ./bin/kitty && tar Jxf kitty-0.43.1-x86_64.txz --strip-components=0 -C ./bin/kitty
rm kitty-0.43.1-x86_64.txz


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
curl -LO https://uk1-dl.techpowerup.com/files/qpMrHvhJCaISg-CxO9bnTg/1761969558/Visual-C-Runtimes-All-in-One-Jul-2025.zip
VCR_FILE="Visual-C-Runtimes-All-in-One-Jul-2025.zip"

if head -c 512 "$VCR_FILE" | grep -q -i -E "(<!DOCTYPE|<html>|<?xml)"; then
    echo "Error: Downloaded file appears to be an HTML or XML page (possible error/redirect page)."
    rm "$VCR_FILE"
    exit 1
fi

mv "$VCR_FILE" ./assets/vcr.zip


# Download msxml3.zip bundle
echo Downloading msxml3 dlls...
curl -LO https://github.com/cutefishaep/AeNux/raw/refs/heads/main/asset/System32/msxml3.dll
curl -LO https://github.com/cutefishaep/AeNux/raw/refs/heads/main/asset/System32/msxml3r.dll
zip ./assets/msxml3.zip msxml3.dll msxml3r.dll
rm msxml3.dll
rm msxml3r.dll

echo --------------------------------------------
echo Done!