# Building from source
## Windows (Git Bash)
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

## Ubuntu Linux
1) Perform the **Configure the system** steps listed in the installation directions
2) Ensure system prerequisites are installed
   ```
   sudo apt-get install binutils git libxcb-cursor0
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

   [Python]: <https://www.python.org>
   [Git for Windows]: <https://gitforwindows.org>