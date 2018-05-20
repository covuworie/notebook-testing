"""This file must be loaded into a Jupyter notebook (using the `%load` magic) and executed there to work correctly.

Note: 
    If it is placed into a module and imported into the notebook then `__name__` will be the module
    name and `__file__` will be in the `globals` object.
    
"""

def is_main_module():
    """Returns whether this notebook is the main module (i.e. not being run from another notebook).
    
    Taken from: 
    https://blog.sicara.com/present-data-science-results-jupyter-notebook-import-into-another-108433bc8505
    
    Returns:
        bool: True if this notebook is the main module, False otherwise.
        
    """
    return __name__ == '__main__' and '__file__' not in globals()