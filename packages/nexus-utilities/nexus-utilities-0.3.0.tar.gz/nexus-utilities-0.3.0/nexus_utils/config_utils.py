"""Configuration-related utilities"""
#%%
import os
import pathlib
# import glob
import configparser
# import io

#%%
def read_config_file(config_filepath):
    """Read config .ini file at provided location, using '_local' version instead if found"""
    if isinstance(config_filepath, str):
        config_filepath = pathlib.Path(config_filepath)
    config = configparser.ConfigParser()
    break_out_flag = False
    # Locate local config file
    local_config_path = ''
    for root, dirs, files in os.walk(config_filepath.parent):
        if break_out_flag == True:
            break
        files = [file for file in files if file.endswith(('.ini'))]
        for file in files:
            if break_out_flag == True:
                break
            if file == config_filepath.stem + '_local.ini':
                # local_config_path = os.path.join(root, file)
                local_config_path = pathlib.Path(root) / file
                break_out_flag = True
                break
    config.read([config_filepath, local_config_path])#, encoding='utf-8-sig')
    return config

# %%
