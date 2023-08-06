from logging import Logger
from src.core import barn_action, Context

@barn_action
def install(context: Context=None, logger: Logger=None):
    if not context.is_initialized:
        print("Initializing python_modules")
        context.run_command_on_global("python -m venv python_modules")

    if not context.lock_file_exists:
        return context.install_from_project()
    else:
        print("Installing..")
        # context.run_command_in_context("pip install -r barn.lock")
        return context.install_from_project()
