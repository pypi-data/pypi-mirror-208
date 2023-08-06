import os
import sys 
import pkg_resources

def init():
    def get_template_path(template_name):
        relative_path = os.path.join("templates", template_name)
        return pkg_resources.resource_filename("src", relative_path)
    
    def is_cwd_empty():
        files_and_directories = os.listdir()
        return len(files_and_directories) == 0
    
    if not is_cwd_empty():
        print("The current directory is not empty. Please run this command in an empty directory.")
        sys.exit(1)

    print("Current working dir: ", os.getcwd())
    print(f"Template: {get_template_path('new-project/project.yml')}")

    project_info = {}

    project_info["name"] = input("Project name: ") or "my-project"
    project_info["version"] = input("Version (default: 0.1.0): ") or "0.1.0"
    project_info["description"] = input("Description: ") or ""
    project_info["author"] = input("Author: ") or ""
    project_info["license"] = input("License (default: MIT): ") or "MIT"

    # You can add more fields as needed

    print("\nProject information:")
    for key, value in project_info.items():
        print(f"{key}: {value}")

