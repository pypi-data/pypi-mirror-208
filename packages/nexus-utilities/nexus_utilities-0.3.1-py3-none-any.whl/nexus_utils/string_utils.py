"""Utilities for working with strings"""
#%%
import re

# def title_to_snake_case(string):
#     converted_string = re.sub(r'(?<=[a-z0-9])([A-Z])|(?<=[^_])([A-Z](?=[a-z]))', r'_\1\2', string)
#     return converted_string.lower()

def cleanse_string(
    string, 
    remove_symbols=True, 
    title_to_snake_case=False, 
    hyphen_to_underscore=True, 
    period_to_underscore=True, 
    to_upper=False, 
    to_lower=True
):
    """Cleanse strings with a number of parameters"""

    if isinstance(string, str):
        if remove_symbols:
            characters_to_replace_with_underscore = [' ',':',';','&','@','^','+','=','~','/','\\','|','(','{','[','<']
            characters_to_remove = [',','`','#','$','%','*','\'','"','?','!',')','}',']','>']
            
            string = string.replace('_', '†')

            for char in characters_to_replace_with_underscore:
                string = string.replace(char, '_')
            string = string.replace('__', '_')
            
            for char in characters_to_remove:
                string = string.replace(char, '')

            string = string.replace('†_','†').replace('_†','†')

            string = string.replace('†','_')
        
        if title_to_snake_case:
            string = re.sub(r'(?<=[a-z0-9])([A-Z])|(?<=[^_])([A-Z](?=[a-z]))', r'_\1\2', string)

        if hyphen_to_underscore:
            string = string.replace('-', '_')

        if period_to_underscore:
            string = string.replace('.', '_')
        
        if to_upper:
            string = string.upper()
        
        if to_lower:
            string = string.lower()

        return string
    
    return None
#%%

"""
print(cleanse_string(
    'Field__(Name)', 
    remove_symbols=True, 
    title_to_snake_case=True, 
    hyphen_to_underscore=True, 
    period_to_underscore=True, 
    to_upper=False, 
    to_lower=True
))
"""