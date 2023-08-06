# Hent

Neofetch alternative built in python

## Usage:
```
$ hent
         ..             Distro: Arch Linux
         cc             Kernel: 5.10.16-zen1-1-zen
        :ooc            Uptime: 3 hours, 45 minutes
       ::lool         Packages: 1864 (pacman), 38 (flatpak)
     .looooool.          Shell: bash
    .loo;..;ooo.      Terminal: kitty
   'oooo    looc.          CPU: Intel i7-4790K @ 4.00GHz
  ;l;'..     .';l;         GPU: GeForce RTX 2060 Rev. A
 ..              .'     Memory: 6325MB / 24562MB
```
```
$ hent --help
usage: hent [-h] [--distro distro] [--color true/false]

Neofetch inspired fetch tool built in python.

optional arguments:
  -h, --help          show this help message and exit
  --distro distro     which ascii art to use
  --color true/false  enable/disable colored output
```

## Installation:

### With pip:
```
pip3 install hent
```

### With git:
```
git clone https://github.com/imsofi/hent.git
cd hent
pip3 install --upgrade build
python3 -m build
pip3 install dist/*.whl
```

## Development

```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```
