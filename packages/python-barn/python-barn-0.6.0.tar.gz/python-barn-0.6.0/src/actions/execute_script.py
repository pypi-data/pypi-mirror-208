from typing import List
from logging import Logger
from src.core import barn_action, Context

@barn_action
def execute_script(
    script_name: str,
    trailing_args: List[str], 
    context: Context=None, 
    logger: Logger=None
):
    """
    This is the main entry point for the 'execute_script' action.
    Such action is triggered when a custom script is executed.
    E.g. barn start
    """
    config = context.get_project_config()
    scripts = config['scripts']
    script_to_execute = None
    for script in scripts:
        if script_name in script:
            script_to_execute = script[script_name]
    exit_code = context.setup_bash_function_capabilities(script_name, script_to_execute)
    if exit_code != 0:
        logger.error("Error setting up script. Is your script valid bash?")
        return exit_code
    
    trailing_args = ' ' + ' '.join(trailing_args) if len(trailing_args) > 0 else ''

    logger.debug(f"Executing script: {script_to_execute} with: {trailing_args}")

    return context.run_function_in_context(script_name, trailing_args)
