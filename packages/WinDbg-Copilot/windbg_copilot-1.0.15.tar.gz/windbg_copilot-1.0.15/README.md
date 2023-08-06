README for Windbg Copilot

Windbg Copilot is a powerful package that allows you to use the ChatGPT capabilities of OpenAI directly in Windows Debugger. This readme file provides instructions for running Windbg Copilot on your local machine.

Prerequisites

        A Windows machine running Windows 11, add environmet variable OPENAI_API_KEY with your openai api key.
        The Windows Debugger (Windbg) installed on your machine C:\Program Files (x86)\Windows Kits\10\Debuggers\x64.
        Python 3.9 or later installed on your machine.
        An Internet connection for downloading and installing the package.

Installation

        Open a command prompt or terminal window, install the Windbg Copilot packages using pip:

        pip install pyttsx3==2.90
        pip install openai
        pip install windbg-copilot

        The packages will be downloaded and installed automatically.

Usage

        Open command line and run python:

        import windbg_copilot
        windbg_copilot.start()

        Use the following commands to interact with Windbg Copilot. You can chat, ask question and retrieve suggestions and assistance based on ChatGPT model.

                !chat <you may ask anything related to debugging>
                !ask <ask any question for the above output>
                !explain: explain the last output
                !suggest: suggest how to do next
                !q: quit

        Note: Windbg Copilot requires an active Internet connection to function properly, as it relies on Openai API.

Uninstallation

        Open a command prompt or terminal window.
        Use pip to uninstall the Windbg Copilot package:

        pip uninstall pyttsx3
        pip uninstall openai
        pip uninstall windbg-copilot

        The packages will be uninstalled automatically.

Conclusion

Windbg Copilot is a powerful package that allows you to use the ChatGPT capabilities of OpenAI directly in Windows Debugger. With its simple installation process and intuitive API, Windbg Copilot is an essential tool for anyone working on complex Windows debugging.