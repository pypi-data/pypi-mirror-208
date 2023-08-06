# -*- coding: utf-8 -*-

import os
import re
import glob


def pad_filenames(folder, target:str='file', str_pattern:str=''):
    '''
    Folder: str
        Folder containing filenames to be modified
    
    target: str, optional
        'file' (default), 'dir' or 'both'
        Defines what should be renamed (files, folders or both)
        
    str_pattern: replace numbers directly after the string (e.g. str_pattern = '_s' will replace '_s1' with '_s001')
    If not pattern given, padding will be applied to the first number in the name
    
    '''
    
    assert os.path.exists(folder), 'Folder not found'
    
    os.chdir(folder)
    if target == 'file':
        files = [fname for fname in os.listdir() if not os.path.isdir(fname)]
    elif target == 'dir':
        files = [fname for fname in os.listdir() if os.path.isdir(fname)]
    elif target == 'both':
        files = [fname for fname in os.listdir()]
    for f in files:
        im_num = re.findall(str_pattern + '[0-9]+', f)
        if len(im_num) > 0:
            im_num = im_num[0]
            pos = [[res.start(), res.end()] for res in re.finditer(im_num, f)][0]
            os.rename(f, f[0:pos[0]+len(str_pattern)] + str(im_num[len(str_pattern):]).zfill(3) + f[pos[1]:])
        
        
        
def replace_pattern(folder, old='', new=''):
    
    assert os.path.exists(folder), 'Folder not found'
    
    os.chdir(folder)
    files = [fname for fname in os.listdir() if not os.path.isdir(fname)]
    
    for f in files:
        os.rename(f, f.replace(old, new))
    

def add_suffix(folder, str_pattern:str='', suffix:str=''):
    '''

    Parameters
    ----------
    folder : str
        Folder containing filenames to be modified.
    str_pattern : str
        Adds a suffix to all files that contain str_pattern
    suffix : str
        Suffix to be added to filenames

    '''
    assert os.path.exists(folder), 'Folder not found'
    
    os.chdir(folder)
    files = [fname for fname in os.listdir() if (str_pattern in fname) and not os.path.isdir(fname)]
    
    for f in files:
        os.rename(f, f.replace(f[-4:], suffix + f[-4:]))
    
def renumber_files(folder, start:int=0, channel_keyword:str='', str_pattern:str=''):

    assert os.path.exists(folder), 'Folder not found'
    os.chdir(folder)
    files = glob.glob(f'*{channel_keyword}*')
    for i, f in enumerate(files):
        im_num = re.findall(str_pattern + '[0-9]+', f)
        if len(im_num) > 0:
            im_num = im_num[0]
            pos = [[res.start(), res.end()] for res in re.finditer(im_num, f)][0]
            os.rename(f, f[0:pos[0]+len(str_pattern)] + str(start + i).zfill(3) + f[pos[1]:] + '_tmp')
    
    replace_pattern(folder, old='_tmp', new='')
































