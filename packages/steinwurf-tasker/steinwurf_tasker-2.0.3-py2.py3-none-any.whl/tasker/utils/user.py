import sys
import re
from invocations import console
from . import validate


class User(object):
    def __init__(self, editor=None):
        self.editor = editor

    def confirm(self, question, assume_yes=True):
        return console.confirm(question, assume_yes)

    def prompt(self, text, default="", validate=None):
        # Set up default display
        default_str = ""
        if default != "":
            default_str = f" [{str(default).strip()}] "
        else:
            default_str = " "
        # Construct full prompt string
        prompt_str = text.strip() + default_str
        # Loop until we pass validation
        value = None
        while value is None:
            # Get input
            value = input(prompt_str) or default
            # Handle validation
            if validate:
                # Callable
                if callable(validate):
                    # Callable validate() must raise an exception if validation
                    # fails.
                    try:
                        value = validate(value)
                    except Exception as e:
                        # Reset value so we stay in the loop
                        value = None
                        print("Validation failed for the following reason:")
                        print(f"\t{e}\n")
                # String / regex must match and will be empty if validation fails.
                else:
                    # Need to transform regex into full-matching one if it's not.
                    if not validate.startswith("^"):
                        validate = r"^" + validate
                    if not validate.endswith("$"):
                        validate += r"$"
                    result = re.findall(validate, value)
                    if not result:
                        print(
                            "Regular expression validation failed: '%s' does not match '%s'\n"
                            % (value, validate)
                        )
                        # Reset value so we stay in the loop
                        value = None
        return value

    def open(self, shell, file):
        if self.editor is None:
            default_editor = "notepad" if sys.platform == "win32" else "nano"
            self.editor = self.prompt(
                f"Which editor do you wish to use for opening files?",
                default=default_editor,
                validate=validate.executable,
            )
        cmd = [self.editor]
        if any([self.editor.endswith(e) for e in ["subl", "code"]]):
            cmd.append("-w")

        cmd.append(file)

        cmd = " ".join(cmd)

        # if nano, make sure the user knows what needs to be done.
        if self.editor == "nano":
            self.prompt(f'Running "{cmd}", press enter to continue.')

        shell.run(cmd)
