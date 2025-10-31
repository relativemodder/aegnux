#!/bin/sh


# Download Kitty Binary
curl -LO https://github.com/kovidgoyal/kitty/releases/download/v0.43.1/kitty-0.43.1-x86_64.txz
mkdir -p ./bin/kitty && tar Jxf kitty-0.43.1-x86_64.txz --strip-components=0 -C ./bin/kitty
rm kitty-0.43.1-x86_64.txz


# Download winetricks
curl -LO https://raw.githubusercontent.com/Winetricks/winetricks/refs/heads/master/src/winetricks
mv winetricks ./bin/


# Download cabextract
curl -LO https://www.cabextract.org.uk/cabextract-1.11-1.x86_64.rpm
bsdtar -xf cabextract-1.11-1.x86_64.rpm usr/bin/cabextract
mv usr/bin/cabextract ./bin/cabextract
rm -rf usr
rm cabextract-1.11-1.x86_64.rpm


# Download Wine
curl -LO https://github.com/Kron4ek/Wine-Builds/releases/download/10.17/wine-10.17-amd64-wow64.tar.xz
mkdir -p ./assets/wine && tar Jxf wine-10.17-amd64-wow64.tar.xz --strip-components=1 -C ./assets/wine
rm wine-10.17-amd64-wow64.tar.xz


# Download Visual C++ Redistributable Runtimes
curl -LO https://uk1-dl.techpowerup.com/files/qpMrHvhJCaISg-CxO9bnTg/1761969558/Visual-C-Runtimes-All-in-One-Jul-2025.zip
mv Visual-C-Runtimes-All-in-One-Jul-2025.zip ./assets/vcr.zip


# Download msxml3.zip bundle
echo msxml3 downloading is not implemented yet.
echo --------------------------------------------
echo Done!