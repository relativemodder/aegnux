<img src="icons/aegnux.png" width="128" />

# Aegnux 

A convenient way to install Adobe After Effects on Linux using Wine. Heavily inspired by [AeNux](https://github.com/cutefishaep/AeNux) by cutefish.

**⚠️ SOFTWARE IS NOT IN THE RELEASE STATE**

*If you're interested in the project's roadmap, check out [**ROADMAP.md**](https://github.com/relativemodder/aegnux/blob/main/ROADMAP.md)*.

[Download Flatpak package](https://github.com/relativemodder/com.relative.Aegnux/releases/latest) if you want to install it on any distro.

[<img src="assets/download_flatpak.png">](https://github.com/relativemodder/com.relative.Aegnux/releases/latest)

<div align="center">

[![Reddit Badge](https://img.shields.io/badge/reddit-orange?style=flat&logoColor=%23ff4500&label=Aegnux%20Sub&link=https%3A%2F%2Fwww.reddit.com%2Fr%2FAegnux)](https://www.reddit.com/r/Aegnux/)
[![AUR Badge](https://img.shields.io/badge/aur-package-blue?style=flat&label=AUR&link=https%3A%2F%2Faur.archlinux.org%2Fpackages%2Faegnux)](https://aur.archlinux.org/packages/aegnux)
[![Telegram Badge](https://img.shields.io/badge/telegram-chat-blue?style=flat&logoSize=%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20&label=Telegram&link=https%3A%2F%2Ft.me%2FAegnux)](https://t.me/Aegnux)


</div>


## License disclaimer

**This project is licensed under GNU GENERAL PUBLIC LICENSE V3.**

This project is intended for educational and experimental use only. Please respect software licensing agreements and use responsibly. The primary objective is to explore Linux compatibility for creative applications. After Effects is a commercial software developed by Adobe.


## Known downsides

- Limited hardware acceleration - NVIDIA GPUs only
- UI Rendering - Occasional flickering with certain plugins (e.g., Flow)
- Memory Management - Potential crashes under heavy RAM usage (need to tweak your system config)

## How to install natively

Native installation: the only tested environment is Arch Linux on KDE Plasma Wayland.

**It's available in the [AUR](https://aur.archlinux.org/packages/aegnux) now**
```bash
yay -S aegnux
# ...or
paru -S aegnux
```

## Manual installation

### Install dependencies
```bash
sudo pacman -Syu pyside6 python-requests unzip libarchive curl tar # Arch Linux
```

### Clone the repository
```bash
https://github.com/relativemodder/aegnux
cd aegnux
```

### Download binaries for workarounds to work
```bash
./prepare.sh
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
