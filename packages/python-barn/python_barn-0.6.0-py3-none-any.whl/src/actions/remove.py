from logging import Logger
from src.core import barn_action, Context


@barn_action
def remove(package_name, context: Context=None, logger: Logger=None):

    stdout, exit_code = context.run_command_in_context(f"pip uninstall -y {package_name}")

    if exit_code == 0:
        stdout, exit_code = context.run_command_in_context("pip freeze > barn.lock")
        context.remove_dependency_from_project_yaml(package_name)
    else:
        print(f"Error removing {package_name}")

    return stdout, exit_code

