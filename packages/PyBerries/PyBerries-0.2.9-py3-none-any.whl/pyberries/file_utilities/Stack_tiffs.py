# -*- coding: utf-8 -*-

import os
import re
import numpy as np
import glob
import tifffile
import shutil

def stack_tiffs(folder, channel_keyword:str='', position_keyword:str='Im'):
    
    assert os.path.exists(folder), 'Folder not found'
    os.chdir(folder)
    
    files = glob.glob(f'*{channel_keyword}*')
    positions = np.unique([re.findall(position_keyword + '[0-9]+', f) for f in files])
    
    for p in positions:
        with tifffile.TiffWriter(f'{p}{channel_keyword}_stack.tif') as stack:
            for filename in files:
                if p in filename and not '_stack' in filename:
                    stack.write(
                        tifffile.imread(filename), 
                        photometric='minisblack', 
                        contiguous=True,
                        metadata={'axes':'TYX'}
                    )

def stack_projection(folder, channel_keyword:str='', projection_type:str='average'):
    
    assert os.path.exists(folder), 'Folder not found'
    os.chdir(folder)

    files = glob.glob(f'*{channel_keyword}*')    
    for f in files:
        if not 'Projection' in f:
            with tifffile.TiffWriter(f'{f}_{projection_type}Projection.tif') as stack:
                if projection_type == 'average':
                    im_out = np.mean(tifffile.imread(f), axis=0, dtype='float64')
                elif projection_type == 'max':
                    im_out = np.max(tifffile.imread(f), axis=0, dtype='int16')
                elif projection_type == 'std':
                    im_out = np.std(tifffile.imread(f), axis=0, dtype='float64')
                stack.write(
                    im_out, 
                    photometric='minisblack',
                    contiguous=True,
                    metadata={'axes':'YX'}
                )

def update_axis(folder, channel_keyword:str='', position_keyword:str='Im', axes:str='ZYX'):
    
    assert os.path.exists(folder), 'Folder not found'
    os.chdir(folder)
    
    files = glob.glob('*'+channel_keyword+'*')
    
    for f in files:
        p = re.findall(position_keyword + '[0-9]+', f)[0]
        img = tifffile.imread(f)
        tifffile.imwrite(p + channel_keyword + '.tif',
                         img,
                         imagej=True,
                         metadata={'axes':axes}
                         )


def replicate_image(folder, filename, replicates:int=200, sep:str='_t'):
    
    assert os.path.exists(folder), 'Folder not found'
    os.chdir(folder)
    
    for i in range(replicates-1):
        shutil.copy2(filename, filename.replace(sep+'001', sep+str(i+2).zfill(3)))
    












































