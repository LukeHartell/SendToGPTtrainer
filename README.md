# Welcome

Hi, this is SendToGPTtrainer.
This program can help you add sources to your chatbot in GPT-trainer.

Simply right-click the file or folder you want to add, and click "Send to GPT-trainer".
If there is already a file with the same name in the database, you will be prompted for options.

There is no installation-file for this yet, so you'll have to follow the get started section below.
When you have completed the guide, you are left with an EXE-file, that you can share with others to let them upload to your bot. (Be careful please).

# Get started

1. First you'll need to configure this .py script, and make sure it works for you.

    1. Configure the script in the configuration section in the top of the script.

    2. Make sure you have python and all dependencies installed.

    3. Use CMD as admin to execute the script

        `C:\>python "C:\Path\To\SendToTrainer.py" --help`

        To add the "Send to GPT-trainer" option in the context menu use `--add-context-menu`
    4. Make sure to remove the option again for now. Use `--remove-context-menu`


2. Then you'll have to use auto-py-to-exe to compile it to an exe-file.

    1. Install auto-py-to-exe if you havn't already.

    2. Use the provided ***auto-py-to-exeConfig.json***, but make sure to corret the path.


3. I suggest placing the EXE in C:\Program Files\SendToGPTtrainer.

    It is not important, as you will never execute it manually.

    However, it is important that the EXE is not moved after the context-menu has been added.

    If you need to move the EXE, you'll have to remove the context menu option and add it again.


4. Add the context menu option for real this time.

    1. To add context menu option use CMD as admin to execute the EXE.

    `C:\Path\To\SendToTrainer>SendToGPTtrainer.exe --add-context-menu`

    This adds the menu for all users on the computer and also saves the location of the EXE.
