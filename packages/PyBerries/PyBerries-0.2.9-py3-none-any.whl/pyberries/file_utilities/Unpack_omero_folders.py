# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 10:14:45 2022

@author: dthedie
"""

import os
import shutil


def unpack_omero_folders(folder:str='', rm_pattern:str=None):
    
    '''
    rm_pattern: delete folders which have specified string in their name
    '''

    assert os.path.exists(folder), 'Folder not found'
    
    os.chdir(folder)
    
    folders = [fname for fname in os.listdir() if os.path.isdir(fname)]
    
    os.mkdir('Saved_files')
    
    for f in folders:
        if rm_pattern in f:
            shutil.rmtree(f)
        else:
            files = [file for file in os.listdir(f) if ('.TIF' or '.tif') in file]
            for j in files:
                shutil.move(os.path.join(f,j), './Saved_files')
            shutil.rmtree(f)
