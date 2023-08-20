# Bed Leveler 5000
## The future of FDM bed leveling!

**Bed Leveler 5000** provides a simple method for paper and feeler gauge-free manual
FDB bed leveling. No firmware, setting, configuration, or hardware changes are required
to use **Bed Leveler 5000**.

## Features

- Paper and feeler gauge-free bed leveling
- No printer modifications or extra hardware required
- 3D bed mesh visualiations
- Does not lose, corrupt, or change existing mesh(es) on the printer

## Tech

**Bed Leveler 5000** uses a number of open source projects to work properly:

- [PySide6] - The official Python module from the Qt for Python project
- [Python] - The Python programming language
- [pylint] - A static code analyser for Python 2 and 3
- [Pillow] - The friendly PIL fork

[Bed Leveler 5000][BedLeveler5000] itself is open source with a [public repository][bedleveler5000] on GitHub.

## Installation

Download the binary archive, extract, and the ```BedLeveler5000``` executable.

#### Building from source

#### Linux
```
sudo apt-get install binutils
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
./build_all
```

#### Windows
```
py -m venv venv
source venv/Scripts/activate
pip3 install -r requirements.txt
./build_all
```

## License

GPLv3

   [BedLeveler5000]: <https://sandmmakers.com/Projects/BedLeveler5000>
   [git-repo-url]: <https://github.com/sandmmakers/BedLeveler5000.git>
   [PySide6]: <https://pypi.org/project/PySide6>
   [Python]: <https://www.python.org>
   [pylint]: <https://github.com/pylint-dev/pylint>
   [Pillow]: <https://github.com/python-pillow/Pillow>