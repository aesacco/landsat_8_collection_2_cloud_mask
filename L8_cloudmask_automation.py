# module imports
import os
from os.path import isfile
from os.path import join
from typing import Tuple
from tkinter import Tk
from tkinter.filedialog import askdirectory
import tarfile

import numpy as np
import rasterio

def int_to_binary(int_value: int) -> str:
    ''' Converts an integer into its binary equivalent.

    Parameters
    ----------
    int_value : INT
        An integer value of the current pixel.

    Returns
    -------
    bin_value : STR
        A string representation of the binary value of int_value.

    '''

    bin_value  =  "{0:b}".format(int_value)
    return bin_value

def landsat8_collection2_qa_mask(img: np.ndarray) -> np.ndarray:
    ''' Landsat 8 cloud mask using the provided QA mask for Collection 2.

    Parameters
    ----------
    img : Numpy.ndarray
        The numpy array representation of the raster imagery band.

    Returns
    -------
    img : Numpy.ndarray
        The cloud-masked raster imagery band, binarized, where 0's are clouds
        and 1's are not clouds.

    '''
    #set fill pixels as 0
    img[img == 1] = 0

    #get unique pixel values for qa mask
    unique_px_values = list(np.unique(img))
    #remove 0 index value and keep only valid pixel values
    del unique_px_values[0]

    for u_px in unique_px_values:
        px_bin = int_to_binary(u_px)
        if len(px_bin) == 15:
            reversed_bin = '0'+px_bin[::-1]
        elif len(px_bin)<15:
            reversed_bin = '0000000000000000'
        else:
            reversed_bin = px_bin[::-1]

        if reversed_bin[7] == '0':
            img[img == u_px] = 0
        else:
            img[img == u_px] = 1

    return img

def write_raster(raster: np.ndarray, raster_ds: rasterio.io.DatasetReader, path: str, file_prefix: str, dst_landsat_folder: str) -> int:
    ''' Writes the raster data to a GeoTIFF file.

    Parameters
    ----------
    raster : Numpy.ndarray
        The cloud-masked raster imagery for a particular image.
    raster_ds : rasterio.io.DatasetReader
        Holds geospatial information for the raster image being processed.
    path : STR
        String to concatenate on the end denoting raster is a cloud mask.
    file_prefix : STR
        The raster image's filename.
    dst_landsat_folder : STR
        The destination folder where the cloud mask output will be saved.

    Returns
    -------
    success : INT
        Flag to identify if image was successfully written or not.

    '''
    success = 0

    kwargs  =  {'driver': 'GTiff',
              'dtype': raster.dtype,
              'nodata': None,
              'width': raster_ds.width,
              'height': raster_ds.height,
              'count': 1,
              'crs': raster_ds.crs,
              'transform': raster_ds.transform}

    user_file_prefix  =  file_prefix.split('LC')[0]
    file_name  =  file_prefix.split(user_file_prefix[-3:])[1]

    with rasterio.open(
            os.path.join(
                dst_landsat_folder, file_name + '_' + path + '.TIF'),
            'w', **kwargs) as file:
        file.write(raster.astype(raster.dtype),1)
    if os.path.exists(os.path.join(
            dst_landsat_folder,file_name+'_'+path+'.TIF')):
        success+= 1
    return success

def create_cloud_mask(src_landsat_folder: str, dst_landsat_folder: str) -> Tuple[int, int]:
    ''' Creates a cloud mask from a given set of source files. Returns count of 
    the number of successful and unsuccessful masks processed. Terminal shows which
    specific files fail.

    Parameters
    ----------
    src_landsat_folder : STR
        Source folder where Tarballs are located on the local drive. This is
        where all the source Landsat imagery should be located.
    dst_landsat_folder : STR
        DESCRIPTION.

    Returns
    -------
    successful_masks : INT
        DESCRIPTION.
    unsuccessful_masks : INT
        The destination folder where the cloud mask output will be saved.

    '''
    #keep track of successes and failures
    successful_masks = unsuccessful_masks = 0

    #list of tar files
    image_tar_dirs  =  [os.path.join(root, name)
                      for root, dirs, files in os.walk(src_landsat_folder)
                      for name in files
                      if name.endswith((".tar"))]

    l8_images  =  [f for f in image_tar_dirs if isfile(join(src_landsat_folder, f))]

    for src_folder in l8_images:
        print(src_folder)

        temp_path = 'D:/temp'
        temp_file_name = 'curr_pixel_qa_band.TIF'
        zip_z = tarfile.open(src_folder)
        for zipfilename in zip_z.getmembers():
            if 'QA_PIXEL' in zipfilename.name:
                src_qa_zip_path = zipfilename.name
                zip_z.extract(zipfilename,path = temp_path)

        # Here we will create the cloudmask
        # Read the source QA into an rasterio object.
        if os.path.exists(os.path.join(temp_path,src_qa_zip_path)):
            with rasterio.open(os.path.join(temp_path,src_qa_zip_path)) as qa_raster:
                print('file:'+str(src_qa_zip_path))
                # Update the raster profile to use 0 as 'nodata'
                profile  =  qa_raster.profile
                profile.update(nodata = 0)

                qa_rast  =  qa_raster.read(1)
                cloudmask = landsat8_collection2_qa_mask(qa_rast)
                write_raster(cloudmask,qa_raster,'cloudmask',src_folder[:-4], dst_landsat_folder)

            #remove temp data
            if os.path.exists(os.path.join(temp_path,src_qa_zip_path)):
                os.remove(os.path.join(temp_path,src_qa_zip_path))
            if os.path.exists(os.path.join(temp_path,temp_file_name)):
                os.remove(os.path.join(temp_path,temp_file_name))

            print('successful'+str(src_qa_zip_path))
            successful_masks+= 1
        else:
            print('unsuccessful'+str(src_qa_zip_path))
            unsuccessful_masks+= 1

    return successful_masks, unsuccessful_masks


def main():
    '''
    Main function to run the cloud mask script for Landsat 8 Collection 2
    data.

    Returns
    -------
    None.

    '''
    # Grab directories for Landsat Tarballs and desired location of output.
    Tk().withdraw()
    src_landsat_folder  =  askdirectory()
    dst_landsat_folder  =  askdirectory()

    os.chdir(src_landsat_folder)

    create_cloud_mask(src_landsat_folder, dst_landsat_folder)

if __name__ == "__main__":
    main()
    
