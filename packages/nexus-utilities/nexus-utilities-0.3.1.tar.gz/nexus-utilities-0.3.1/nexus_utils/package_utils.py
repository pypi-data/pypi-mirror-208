"""Utilities for working with Python packages"""
import sys
import os
import inspect

def add_package_to_path(verbose=False):
    """Programmatically determine the most likely root of the current running program, add its parent to the path, and return the root folder name"""
    # Define the list of common package root files and folders with lowercase
    package_root_items = ["src", "tests", "templates", "docs", "dist", "build", "readme.md", "license.txt", ".gitignore", "pyproject.toml", "requirements.txt", "poetry.lock", "setup.py", "manifest.in", ".editorconfig"]

    # Initialize a dictionary to store the count of package root items found in each directory
    item_counts = {}

    # Traverse upward from the current directory, counting the instances of package root items found in each directory
    current_dir = os.getcwd()
    while current_dir != os.path.dirname(current_dir):
        # Count the instances of package root items found in the current directory
        current_item_counts = {item: 0 for item in package_root_items}
        for item in os.listdir(current_dir):
            item_lower = item.lower()
            if item_lower in current_item_counts:
                current_item_counts[item_lower] += 1

        # Add the counts for the current directory to the overall counts dictionary
        for item, count in current_item_counts.items():
            if count > 0:
                item_counts.setdefault(item, {})[current_dir] = count

        # Move up one directory and continue counting
        current_dir = os.path.dirname(current_dir)

    # Find the directory with the most package root items found, and add its parent to the path
    max_item_count = 0
    max_item_count_dir = ""
    for item, counts in item_counts.items():
        for directory, count in counts.items():
            if count > max_item_count or (count == max_item_count and len(directory) > len(max_item_count_dir)):
                max_item_count = count
                max_item_count_dir = directory

    if max_item_count > 0:
        package_root_dir = os.path.dirname(max_item_count_dir)
        os.environ["PATH"] += os.pathsep + package_root_dir
        package_root_name = os.path.basename(max_item_count_dir)
        os.environ["PATH"] += os.pathsep + package_root_dir + os.sep + package_root_name
        if verbose == True:
            print(f'PATH: {os.environ["PATH"]}')
        return package_root_dir, package_root_name
    else:
        print("Could not find package root directory")
        return None

def import_relative(package_root_name, module_path, import_name, alias=None):
    """Import a relative library dynamically.  Accepts 'package_root_name' from 'add_package_to_path()' function"""
    module_name = f"{package_root_name}.{module_path}"
    print(f'module_name: {module_name}')
    module = __import__(module_name, fromlist=[import_name])

    # Get the imported object
    obj = getattr(module, import_name)

    # Determine the globals of the calling program and add any alias provided to it
    caller_globals = inspect.stack()[1][0].f_globals
    if alias:
        caller_globals[alias] = obj
    else:
        caller_globals[import_name] = obj

    # Return the imported object
    # return obj
