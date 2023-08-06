from logging import Logger
from src.core import barn_action, Context

@barn_action
def show(package, verbose=False, files=False, context: Context=None, logger: Logger=None):
    verbose_string = "--verbose" if verbose else ""
    files_string = "--files" if files else ""
    return context.run_command_in_context(f"pip show {verbose_string} {files_string} {package}")
