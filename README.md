<img src="icons/aegnux.png" width="128" />

# Aegnux 

A convenient way to install Adobe After Effects on Linux using Wine. Heavily inspired by [AeNux](https://github.com/cutefishaep/AeNux) by cutefish.


## License disclaimer

This project is intended for educational and experimental use only. Please respect software licensing agreements and use responsibly. The primary objective is to explore Linux compatibility for creative applications. After Effects is a commercial software developed by Adobe.


## Known downsides

- Limited hardware acceleration - NVIDIA GPUs only
- UI Rendering - Occasional flickering with certain plugins (e.g., Flow)
- Memory Management - Potential crashes under heavy RAM usage (need to tweak your system config)

## How to install

[Download Flatpak](https://github.com/relativemodder/com.relative.Aegnux/releases) if you want to install it on any distro.


Native installation: the only tested environment is Arch Linux on KDE Plasma Wayland.

### Install dependencies
```bash
sudo pacman -Syu python-pyside6 python-requests # Arch Linux
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
