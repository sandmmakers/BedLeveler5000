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

## Documentation
- Introduction video: [Bed Leveler 5000][video]
- Homepage: https://sandmmakers.com/Projects/BedLeveler5000

## Tech

**Bed Leveler 5000** uses a number of open source projects to work properly:

- [PySide6] - The official Python module from the Qt for Python project
- [Python] - The Python programming language
- [pylint] - A static code analyser for Python 2 and 3
- [Pillow] - The friendly PIL fork

[Bed Leveler 5000][BedLeveler5000] itself is open source with a [public repository][bedleveler5000] on GitHub.

## Installation
### Windows
1) Download the **.7z** file from the latest release at https://github.com/sandmmakers/BedLeveler5000/releases
2) Extract the downloaded archive
3) Launch **BedLeveler5000.exe**

### Ubuntu Linux
>[!NOTE]
>Use of Ubuntu's Dark theme is not recommended.

1) Configure the system
    1) Ensure **brltty** is not installed
    ```
    sudo apt remove brltty
    ```
    2) Give the current user permissions to use serial ports
    ```
    sudo usermod -a -G dialout $USER
    ```
    3) Reboot to ensure all changes take effect
2) Download the **.tgz** file from the latest release at https://github.com/sandmmakers/BedLeveler5000/releases
3) Extract the downloaded archive
4) Launch **BedLeveler5000**

## Building from source
### Windows (Git Bash)
1) Install [Python]
2) Install [Git for Windows]
3) (Optional) Disable conflicting **app execution aliases** Windows features
    1) Navigate to **Start** -> **Settings** -> **Advanced app settings** -> **App execution aliases**
    2) Set **App Installer - python.exe** to **off**
    3) Set **App Installer - python3.exe** to **off**
4) Clone the repository
   ```
   git clone https://github.com/sandmmakers/BedLeveler5000.git
   ```
5) Enter the repository
   ```
   cd BedLeveler5000
   ```
5) (Optional) Create a virtual environment
   ```
   py -m venv venv
   ```
6) Activate the virtual environment
   ```
   source venv/Scripts/activate
   ```
7) Install prerequisites
   ```
   pip3 install -r requirements.txt
   ```
8) Build the binary package
   ```
   ./build_all
   ```

### Ubuntu Linux
1) Perform the **Configure the system** steps listed in the installation directions
2) (Optional) Ensure **python3-venv** is installed
   ```
   sudo apt-get install python3-venv
   ```
2) Ensure **binutils** is installed
   ```
   sudo apt-get install binutils
   ```
2) Clone the repository
   ```
   git clone https://github.com/sandmmakers/BedLeveler5000.git
   ```
3) Enter the repository
   ```
   cd BedLeveler5000
   ```
4) (Optional) Create a virtual environment
   ```
   python3 -m venv venv
   ```
5) Activate the virtual environment
   ```
   source venv/bin/activate
   ```
6) Install prerequisites
   ```
   pip3 install -r requirements.txt
   ```
7) Build the binary package
   ```
   ./build_all
   ```

## License

GPLv3

   [BedLeveler5000]: <https://sandmmakers.com/Projects/BedLeveler5000>
   [git-repo-url]: <https://github.com/sandmmakers/BedLeveler5000.git>
   [video]: <https://youtu.be/j5rzlHdtJAo>
   [PySide6]: <https://pypi.org/project/PySide6>
   [Python]: <https://www.python.org>
   [pylint]: <https://github.com/pylint-dev/pylint>
   [Pillow]: <https://github.com/python-pillow/Pillow>
   [Git for Windows]: <https://gitforwindows.org>