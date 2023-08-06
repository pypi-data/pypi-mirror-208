README for Windbg Copilot

Windbg Copilot is a powerful package that allows you to use the ChatGPT capabilities of OpenAI directly in Windows Debugger. This readme file provides instructions for running Windbg Copilot on your local machine.

Prerequisites

        A Windows machine running Windows 11, add environmet variable OPENAI_API_KEY with your openai api key.
        The Windows Debugger (Windbg) installed on your machine, for example: C:\Program Files\Debugging Tools for Windows (x64)
        Add environment variable WINDBG_PATH=C:\Program Files\Debugging Tools for Windows (x64).
        Add environment variable _NT_SYMBOL_PATH=srv*c:\symbols*https://msdl.microsoft.com/download/symbols
        Python 3.9 or later installed on your machine.
        An Internet connection for downloading and installing the package.

Installation

        Open a command prompt or terminal window, install the Windbg Copilot packages using pip:

        pip install pyttsx3==2.90
        pip install openai
        pip install windbg-copilot

        The packages will be downloaded and installed automatically.

Usage

        Open python command line and run:

        import windbg_copilot

        Use the following commands to interact with Windbg Copilot. You can chat, ask question and retrieve suggestions and assistance based on ChatGPT model.

            !chat or !c <ask me anything about debugging>: chat with windbg copilot
            !ask or !a <ask a specific question for the last debugger output>: if you want to ask something in regard to last debugger output, use this one.
            !explain or !e: explain the last debugger output
            !suggest or !s: suggest how to do next in regard to the last output
            !voice or !v <on|off>: turn voice on or off
            !quit or !q or q: quit debugger session
            !help or !h: help info

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