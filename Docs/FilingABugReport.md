# Filing a bug report
When filing a bug report, providing all the required and relevant information is
essential for the quick and efficient resolution of the issue.

## Creating a bug report
1) Navigate to the [Bed Leveler 5000 Software Suite repository] on GitHub
2) Click on the **Issues** tab
3) Click the **New issue** button
4) Add a succinct title describing the issue
5) Fill in the description field with the following information:
    - Detailed description of the problem
    - Detailed steps to reproduce the problem
    - Name and model of printer(s) experiancing the issue
    - Type of printer (Klipper or Marlin)
    - Versions of software installed on the printer
      - Marlin
        - Manufacturer firmware version number
        - Marlin firmware version (if known)
      - Klipper
        - Klipper
        - Moonraker
        - Web interface (Fluidd or Mainsail)
6) Attach the following to the bug report
    - Log file created while the problem is occuring
    - If possible, screenshots or videos of the application exhibiting the issue
    - (For Klipper printers) The printer.cfg file for the printer

## Creating a log file
>[!NOTE]
>Applications in the **Bed Leveler 5000 Software Suite** append log information to the specified log file.
>When creating a log file, please either delete any existing log files named `log.txt` or use a different
> file name.
1) Open a command prompt or terminal
2) Navigate to the directory containing the **Bed Leveler 5000 Software Suite** executables
3) Launch the launch the application experiancing the bug with logging enabled
    - **Windows**
      - **Bed Leveler 5000**
        ```
        BedLeveler5000.exe --log-level debug --log-file log.txt
        ```
      - **Printer Info Wizard**
        ```
        PrinterInfoWizard.exe --log-level debug --log-file log.txt
        ```
      - **Inspector G-code**
        ```
        InspectorG-code.exe --log-level debug --log-file log.txt
        ```
    - **Linux**
      - **Bed Leveler 5000**
        ```
        ./BedLeveler5000 --log-level debug --log-file log.txt
        ```
      - **Printer Info Wizard**
        ```
        ./PrinterInfoWizard --log-level debug --log-file log.txt
        ```
      - **Inspector G-code**
        ```
        ./InspectorG-code --log-level debug --log-file log.txt
        ```

   [Bed Leveler 5000 Software Suite repository]: <https://github.com/sandmmakers/BedLeveler5000.git>

## Determine Klipper software versions
### Fluidd
1) Navigate to the **Fluidd** web interface for the affected printer
2) Click on the **Settings** icon (bottom icon on the left)
3) Record all listed versions in the **Software Updates** section

### Mainsail
1) Navigate to the **Mainsail** web interface for the affected printer
2) Navigate to the **MACHINE** tab
3) Record all of the listed versions in the **Update Manager** section