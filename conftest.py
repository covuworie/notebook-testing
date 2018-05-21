import pytest
import os
import sys

import nbformat as nbf

import ast
import collections
import glob
import os

from astor import to_source
from ipynb.utils import code_from_ipynb, validate_nb, filter_ast
import nbformat as nbf

from IPython.core.interactiveshell import InteractiveShell

from isort.isort import SortImports

TEST_FILE_PATTERNS = ['test_*.ipynb', '*_test.ipynb']

def pytest_collect_file(path, parent):
    for pattern in TEST_FILE_PATTERNS:
        if glob.fnmatch.fnmatch(glob.os.path.basename(path), pattern):
            write_notebook_source(path)
        
def write_notebook_source(path):
    nb = nbf.read(path, as_version=nbf.NO_CONVERT) # validate nbformat 4 only
        
    # transform the input to executable Python
    code = InteractiveShell.instance().input_transformer_manager.transform_cell(code_from_ipynb(nb))
        
    # add imports to code
    add_imports = []
    code_lines = code.splitlines()
    for code_line in code_lines:
        # many caveats - command line parameters :  
        # http://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-run
        if code_line.strip().startswith("get_ipython().run_line_magic('run'"): # what about quotes?
            nb_path = code_line.split(', ')[1].strip(")'") # check if endswith .ipy[nb]
            nb_path = os.path.normpath(nb_path)
            if not os.path.isabs(nb_path):
                nb_path = os.path.normpath(os.path.dirname(path) + os.path.sep + nb_path)
            
            # recursive call to deal with run magics
            write_notebook_source(nb_path)
            
            # add imports
            common_path = os.path.commonpath([path, nb_path])
            # if not common path bail!
            path_to_file = os.path.relpath(nb_path, common_path)
            path_to_file = os.path.dirname(path_to_file)
            path_to_file = (path_to_file.replace(os.path.sep, '.') + '.' 
                + os.path.split(nb_path)[1])
            path_to_file, _ = os.path.splitext(path_to_file)
            import_statement = ('from ' + path_to_file + ' import * ')
            add_imports.append(import_statement)
            
    # sort imports
    code = SortImports(file_contents=code, add_imports=add_imports).output
            
    # extract imports, function defs, class defs and constants
    code = filter_ast(ast.parse(code)) #code_from_ipynb(nb)
        
    # write the file
    filename, _ = os.path.splitext(path)
    filename = filename + '.py'
    with open(filename, 'w', encoding='utf-8') as py_file:
        py_file.write(to_source(code))
        print('Written file ', filename)