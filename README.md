# The Bed Leveler 5000 Utility Suite
## The future of FDM bed leveling!

**Bed Leveler 5000** provides a simple method for paper and feeler gauge-free manual
FDB bed leveling. No firmware, setting, configuration, or hardware changes are required
to use **Bed Leveler 5000**.

## Features

- Paper and feeler gauge-free bed leveling
- No printer modifications or extra hardware required
- 3D bed mesh visualiations
- Does not lose, corrupt, or change existing mesh(es) on the printer
- Utility for adding new printer support
- Utility for testing and exploring G-code commands

## Documentation
- **Bed Leveler 5000** Klipper support video: [Bed Leveler 5000 Klipper support][BedLeveler5000KlipperVideo]
- **Bed Leveler 5000** introduction video: [Bed Leveler 5000][BedLeveler5000Video]
- **Printer Info Wizard** introduction video: [Printer Info Wizard][PrinterInfoWizardVideo]
- **Inspector G-code** introduction video: [Inspector G-code][InspectorG-code]
- Homepage: https://sandmmakers.com/Projects/BedLeveler5000

## Tech

**Bed Leveler 5000** uses a number of open source projects to work properly:

- [PySide6] - The official Python module from the Qt for Python project
- [Python] - The Python programming language (3.12+)
- [pylint] - A static code analyser for Python 2 and 3
- [Pillow] - The friendly PIL fork

[Bed Leveler 5000][BedLeveler5000], [Printer Info Wizard][BedLeveler5000], and [Inspector G-code][InspectorG-code] themselves are open source with a [public repository][bedleveler5000] on GitHub.

## Installation
### Windows
1) Download the **.7z** file from the latest release at https://github.com/sandmmakers/BedLeveler5000/releases
2) Extract the downloaded archive
3) Launch **BedLeveler5000.exe**, **PrinterInfoWizard.exe**, or **InspectorG-code.exe**

### Ubuntu Linux
>[!NOTE]
>Use of Ubuntu's Dark theme is not recommended.

1) Configure the system
    1) Install prerequisites
       ```
       sudo apt-get install libxcb-cursor0
       ```
    2) Ensure **brltty** is not installed
       ```
       sudo apt remove brltty
       ```
    3) Give the current user permissions to use serial ports
       ```
       sudo usermod -a -G dialout $USER
       ```
    4) Reboot to ensure all changes take effect
2) Download the **.tgz** file from the latest release at https://github.com/sandmmakers/BedLeveler5000/releases
3) Extract the downloaded archive
4) Launch **BedLeveler5000**, **PrinterInfoWizard**, or **InspectorG-code**

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
2) Ensure system prerequisites are installed
   ```
   sudo apt-get install binutils git
   ```
3) Install and configure Python
    - Systems with Python 3.12+
        1) (Optional) Ensure **python3-venv** is installed
           ```
           sudo apt-get install python3-venv
           ```
    - Systems without Python 3.12+
        1) Ensure the system is fully up to date
           ```
           sudo apt-get update
           sudo apt-get upgrade
           ```
        2) Ensure prerequisites for building Python are installed
           ```
           sudo apt install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
           ```
        3) Install `pyenv`
            1) Clone `pyenv`
               ```
               git clone https://github.com/pyenv/pyenv.git ~/.pyenv
               ```
            2) Build `pyenv` dynamic `bash` extension
               ```
               (cd ~/.pyenv && src/configure && make -C src)
               ```
            3) Add the following to `~/.bashrc` to configure environment
               ```
               # Configure pyenv
               export PYENV_ROOT="${HOME}/.pyenv"
               export PATH=~/.pyenv/bin:${PATH}
               eval "$(pyenv init -)"
               ```
            4) Ensure changes take affect
               ```
               source ~/.bashrc
               ```
        4) Install **Python 3.12+**
            1) Install **Python 3.12** or later
               ```
               pyenv install 3.12.0
               ```
            2) Activate **Python 3.12**+ for the current shell
               ```
               pyenv shell 3.12.0 # or newer
               ```
            3) (Optional) Update pip to prevent warnings
               ```
               pip install --upgrade pip
               ```
4) Clone the repository
   ```
   git clone https://github.com/sandmmakers/BedLeveler5000.git
   ```
5) Enter the repository
   ```
   cd BedLeveler5000
   ```
6) (Optional) Create a virtual environment
   ```
   python3 -m venv venv
   ```
7) Activate the virtual environment
   ```
   source venv/bin/activate
   ```
8) Install prerequisites
   ```
   pip3 install -r requirements.txt
   ```
9) Build the binary package
   ```
   ./build_all
   ```

## License

GPLv3

   [BedLeveler5000]: <https://sandmmakers.com/Projects/BedLeveler5000>
   [git-repo-url]: <https://github.com/sandmmakers/BedLeveler5000.git>
   [BedLeveler5000KlipperVideo]: <https://youtu.be/JBGN3U0C2LM>
   [BedLeveler5000Video]: <https://youtu.be/j5rzlHdtJAo>
   [PrinterInfoWizardVideo]: <https://youtu.be/vVYRg6_kZsc>
   [InspectorG-code]: <https://youtu.be/EVntFYltG1U>
   [PySide6]: <https://pypi.org/project/PySide6>
   [Python]: <https://www.python.org>
   [pylint]: <https://github.com/pylint-dev/pylint>
   [Pillow]: <https://github.com/python-pillow/Pillow>
   [Git for Windows]: <https://gitforwindows.org>