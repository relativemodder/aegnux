<img src="icons/aegnux.png" width="128" />

# Aegnux 

A convenient way to install Adobe After Effects on Linux using Wine. Heavily inspired by [AeNux](https://github.com/cutefishaep/AeNux) by cutefish.

**⚠️ SOFTWARE IS NOT IN THE RELEASE STATE**\
**⚠️ SOFTWARE CONTAINS BINARY BLOBS (explaination is in the bottom of this README)**

**Heads up:** I'm planning on removing all of the proprietary blobs in my project and illegal AE download links too. Please be patient, or, even better, help me with this.

*If you're interested in the project's roadmap, check out [**ROADMAP.md**](https://github.com/relativemodder/aegnux/blob/main/ROADMAP.md)*.



[Download Flatpak package](https://github.com/relativemodder/com.relative.Aegnux/releases/latest) if you want to install it on any distro.


## License disclaimer

This project is intended for educational and experimental use only. Please respect software licensing agreements and use responsibly. The primary objective is to explore Linux compatibility for creative applications. After Effects is a commercial software developed by Adobe.


## Known downsides

- Limited hardware acceleration - NVIDIA GPUs only
- UI Rendering - Occasional flickering with certain plugins (e.g., Flow)
- Memory Management - Potential crashes under heavy RAM usage (need to tweak your system config)

## How to install

Native installation: the only tested environment is Arch Linux on KDE Plasma Wayland.

### Install dependencies
```bash
sudo pacman -Syu pyside6 python-requests # Arch Linux
```

### Clone the repository
```bash
https://github.com/relativemodder/aegnux
cd aegnux
```

### Run
```bash
./run.sh
```

## We need help!
You're welcome to contribute to this project. 
You can improve translations, AMD GPU support, overall stability, etc.

## Contribution rules
- NO proprietary blobs in the code, we're trying to get rid of those, reference them externally and explain what do they do
- Don't do massive commits
- Your code should follow the style of our project
- DON'T SEND AI-GENERATED SLOP, please, for the love of god
- Try to follow the [**ROADMAP.md**](https://github.com/relativemodder/aegnux/blob/main/ROADMAP.md)

## If you're doubt about origins of binary files...
- Wine (compiled and stripped) - official repo
- msxml3.dll - MS Windows
- Visual C++ Redist pack - [TechPowerUp](https://www.techpowerup.com/download/visual-c-redistributable-runtime-package-all-in-one/)
- kitty - [Binary releases](https://github.com/kovidgoyal/kitty/releases)
- cabextract - [Binary RPM](https://src.fedoraproject.org/rpms/cabextract)
- winetricks - it's already the source itself.

IF YOU WANT TO CHANGE THIS, you're welcome to write additional pipeline to compile these files from scratch.