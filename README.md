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
4) Launch **BedLeveler5000**, **PrinterInfoWizard**, or **InspectorG-code**

## Filing a bug report
See [Filing a bug report](Docs/FilingABugReport.md)

## Building from source
See [Building from source](Docs/BuildingFromSource.md)

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