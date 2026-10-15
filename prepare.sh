#!/bin/sh
set -eu

# Stop on the first failure so a partial download doesn't get packaged or extracted later.
for tool in curl tar xz bsdtar zip; do
    command -v "$tool" >/dev/null 2>&1 || { echo "Missing required tool: $tool" >&2; exit 1; }
done

# Yeah, bundling the entire terminal emulator for flatpak builds lol
if [ -d /app ]; then
    # Download Kitty Binary
    echo Downloading Kitty Binary...
    curl -fLO https://github.com/kovidgoyal/kitty/releases/download/v0.43.1/kitty-0.43.1-x86_64.txz
    mkdir -p ./bin/kitty && tar Jxf kitty-0.43.1-x86_64.txz --strip-components=0 -C ./bin/kitty
    rm kitty-0.43.1-x86_64.txz
fi

# Download winetricks
echo Downloading Winetricks...
curl -fLO https://raw.githubusercontent.com/Winetricks/winetricks/refs/heads/master/src/winetricks
mv winetricks ./bin/
chmod +x ./bin/winetricks


# Download cabextract
echo Downloading Cabextract...
curl -fLO https://www.cabextract.org.uk/cabextract-1.11-1.x86_64.rpm
bsdtar -xf cabextract-1.11-1.x86_64.rpm usr/bin/cabextract
mv usr/bin/cabextract ./bin/cabextract
chmod +x ./bin/cabextract
rm -rf usr
rm cabextract-1.11-1.x86_64.rpm


# Download Wine
echo Downloading Wine...
curl -fLO https://github.com/Kron4ek/Wine-Builds/releases/download/11.12/wine-11.12-staging-tkg-amd64-wow64.tar.xz
mkdir -p ./assets/wine && tar Jxf wine-11.12-staging-tkg-amd64-wow64.tar.xz --strip-components=1 -C ./assets/wine
rm wine-11.12-staging-tkg-amd64-wow64.tar.xz

# Download comdlg32 patches
echo Downloading and applying file dialog patches...
curl -fLO https://github.com/buwryme/wine-xdg/releases/download/binaries/comdlg32.dll
curl -fLO https://github.com/buwryme/wine-xdg/releases/download/binaries/comdlg32.so
mv comdlg32.so assets/wine/lib/wine/x86_64-unix/comdlg32.so
mv comdlg32.dll assets/wine/lib/wine/x86_64-windows/comdlg32.dll

# Download Visual C++ Redistributable Runtimes
echo Downloading Visual C++ Redistributable Runtimes...
curl -fLO https://github.com/relativemodder/aegnux/releases/download/vcrbin/vcr.zip
mv ./vcr.zip ./assets/vcr.zip


# Download msxml3.zip bundle
echo Downloading msxml3 dlls...
curl -fLO https://github.com/relativemodder/aegnux/releases/download/vcrbin/msxml3.dll
curl -fLO https://github.com/relativemodder/aegnux/releases/download/vcrbin/msxml3r.dll
zip ./assets/msxml3.zip msxml3.dll msxml3r.dll
rm msxml3.dll
rm msxml3r.dll


# Download gdiplus.dll
echo Downloading gdiplus.dll...
curl -fLO https://github.com/relativemodder/aegnux/releases/download/vcrbin/gdiplus.dll
mv gdiplus.dll ./assets/


# Download dxvk
echo Downloading dxvk...
curl -fLO https://github.com/doitsujin/dxvk/releases/download/v3.0.1/dxvk-3.0.1.tar.gz
mv dxvk-3.0.1.tar.gz ./assets/dxvk.tar.gz

echo --------------------------------------------
echo Done!
