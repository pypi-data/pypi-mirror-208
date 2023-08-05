import os
import subprocess

import pandas as pd

from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.table import Table
from astropy.table import vstack
import sys

def filename_to_weightname( filename):
    name_list = list(filename)
    name_list[-11] = 'w'
    return ''.join(name_list)

    
class Decam_pipeline(object):

    #def __init__(self, low_limit, high_limit):
    #    self.low_limit = low_limit
    #    self.high_limit = high_limit
    

    def __init__(self, input_filename_g=None, input_filename_i=None, output_dir=os.getcwd(), sex_psf_config='default_psf.sex', sex_config='default.sex', psfex_config='default_decam.psfex', config_dir='decam_photometry/decam_lib/config', data_dir=None):

        self.output_dir = output_dir
        self.sex_psf_config = sex_psf_config
        self.sex_config = sex_config
        self.psfex_config = psfex_config
        self.config_dir = config_dir
        self.data_dir = data_dir

        if self.data_dir is not None:
            self.input_filename_g, self.input_filename_i = self.find_obs(self.data_dir, input_filename_g, input_filename_i)
        else:
            self.input_filename_g = input_filename_g
            self.input_filename_i = input_filename_i


        
        # Get weigth names
        self.weight_name_g = filename_to_weightname(self.input_filename_g)
        self.weight_name_i = filename_to_weightname(self.input_filename_i)

    @staticmethod
    def find_obs(data_dir, input_g, input_i):
        if None in [input_g, input_i]:
            files = os.listdir(data_dir)
            g_s = []
            i_s = []
            for file in files:
                if file.endswith('_osi_g_v1.fits'):
                    g_s.append(os.path.join(data_dir, file))
                if file.endswith('_osi_i_v1.fits'):
                    i_s.append(os.path.join(data_dir, file))
            if len(g_s)>1:
                sys.exit('Currently can only run a single OB in two channels at a time')
            if len(i_s)>1:
                sys.exit('Currently can only run a single OB in two channels at a time')
            return g_s[0], i_s[0]
        else:
            return input_g, input_i
    


    def threshold_computation(self, image, hdu0): #gives 1.5 sigma detect threshold for sextractor
        
        flat_image = image.ravel()
        mean, median, std = sigma_clipped_stats(flat_image[flat_image>hdu0.header['SKYSUB']+3 ], sigma=5.0)
        return std*1.5
    
    def pysex(self, catalog_name, image, weight_image, config_file, detect_thresh): #calls swarp from python
        #image_list must be a list, and final_image_path must be a string
        subprocess_list = ['sex']
        subprocess_list.append(image)
        subprocess_list.append('-c')
        subprocess_list.append(config_file)
        subprocess_list.append('-CATALOG_NAME')
        subprocess_list.append(catalog_name)
        subprocess_list.append('-DETECT_THRESH')
        subprocess_list.append(str(detect_thresh))
        subprocess_list.append('-WEIGHT_IMAGE')
        subprocess_list.append(weight_image)
        result = subprocess.run(subprocess_list, stdout=subprocess.PIPE, cwd=self.config_dir)
        return 'done'
    
    def join_final_catalogs(self):
        final_catalog_g = pd.DataFrame() # Create dataframes
        final_catalog_i = pd.DataFrame()

        for i in range(1,10):
            catalog_hdu_g = os.path.join(self.output_dir, f'hdu{i}_g_final.cat') # Open sextractor's catalog for each HDU
            catalog_hdu_i = os.path.join(self.output_dir, f'hdu{i}_i_final.cat')
            dat_g = Table.read(catalog_hdu_g, format = 'fits', hdu = 2).to_pandas()
            dat_i = Table.read(catalog_hdu_i, format = 'fits', hdu = 2).to_pandas()
            final_catalog_g = pd.concat([final_catalog_g, dat_g]) # Conactenate catalogs
            final_catalog_i = pd.concat([final_catalog_i, dat_i])
        final_catalog_g.to_csv(f'{self.output_dir}/final_catalog_g.csv', index= False) # Save catalogs
        final_catalog_i.to_csv(f'{self.output_dir}/final_catalog_i.csv', index= False)

        
    def join_final_catalogs2(self):
        # Create tables
        final_catalog_g = Table()
        final_catalog_i = Table()

        for i in range(1, 10):
            # Open sextractor's catalog for each HDU
            catalog_hdu_g = os.path.join(self.output_dir, f'hdu{i}_g_final.cat')
            catalog_hdu_i = os.path.join(self.output_dir, f'hdu{i}_i_final.cat')
            
            dat_g = Table.read(catalog_hdu_g, format='fits', hdu=2)
            dat_i = Table.read(catalog_hdu_i, format='fits', hdu=2)
            
            # Concatenate tables
            final_catalog_g = vstack([final_catalog_g, dat_g])
            final_catalog_i = vstack([final_catalog_i, dat_i])
        
        # Save tables
        final_catalog_g.write(f'{self.output_dir}/final_catalog_g.fits', format='fits', overwrite=True)
        final_catalog_i.write(f'{self.output_dir}/final_catalog_i.fits', format='fits', overwrite=True)


    def delete_temp(self):
        for filename in os.listdir(self.output_dir):
            if filename.startswith('hdu'):
                file_path = os.path.join(self.output_dir, filename)
                os.remove(file_path)


    def photometry(self):
        # Check if the output directory exists; if not, create it
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        print(f'Running on: \n {self.input_filename_i} and {self.input_filename_g}')
        # Open the input files and split them into individual HDUs
        with fits.open(self.input_filename_g) as hdul_g, fits.open(self.input_filename_i) as hdul_i, fits.open(self.weight_name_g) as w_hdul_g, fits.open(self.weight_name_i) as w_hdul_i:
            for hdu_num in range(1, 10):
                # Get the HDU data and header from the input files
                hdu_data_g = hdul_g[hdu_num].data
                hdu_data_i = hdul_i[hdu_num].data
                hdu_header_g = hdul_g[hdu_num].header
                hdu_header_i = hdul_i[hdu_num].header

                # Get the weight HDU data and header from the input files
                w_hdu_data_g = w_hdul_g[hdu_num].data
                w_hdu_data_i = w_hdul_i[hdu_num].data
                w_hdu_header_g = w_hdul_g[hdu_num].header
                w_hdu_header_i = w_hdul_i[hdu_num].header
                
                # Save the HDU data to separate FITS files
                output_filename_g = os.path.join(self.output_dir, f'hdu{hdu_num}_g.fits')
                output_filename_i = os.path.join(self.output_dir, f'hdu{hdu_num}_i.fits')
                fits.writeto(output_filename_g, hdu_data_g, hdu_header_g, overwrite=True)
                fits.writeto(output_filename_i, hdu_data_i, hdu_header_i, overwrite=True)

                # Save the weight HDU data to seperate FITS files
                output_weightname_g = os.path.join(self.output_dir, f'hdu{hdu_num}_g_weight.fits')
                output_weightname_i = os.path.join(self.output_dir, f'hdu{hdu_num}_i_weight.fits')
                fits.writeto(output_weightname_g, w_hdu_data_g, w_hdu_header_g, overwrite=True)
                fits.writeto(output_weightname_i, w_hdu_data_i, w_hdu_header_i, overwrite=True)
                
                # Compute 1.5 sigma thresholds for sextractor
                thresh_g = self.threshold_computation(image= hdu_data_g, hdu0= hdul_g[0])
                thresh_i = self.threshold_computation(image= hdu_data_i, hdu0 = hdul_i[0])

                # Run sextractor on each HDU
                print('Running initial sextractor')
                sextractor_command_g = f'sex {output_filename_g} -c {self.sex_config} -CATALOG_NAME {output_filename_g[:-5]}.cat -DETECT_THRESH {thresh_g} -WEIGHT_IMAGE {output_weightname_g}'
                sextractor_command_i = f'sex {output_filename_i} -c {self.sex_config} -CATALOG_NAME {output_filename_i[:-5]}.cat -DETECT_THRESH {thresh_i} -WEIGHT_IMAGE {output_weightname_i}'
                subprocess.run(sextractor_command_g, shell=subprocess.PIPE, cwd= self.config_dir)
                subprocess.run(sextractor_command_i, shell= subprocess.PIPE, cwd= self.config_dir)
                #self.pysex(catalog_name= output_filename_g[:-5], image= output_filename_g, weight_image=output_weightname_g, detect_thresh= thresh_g, config_file= self.sex_config)
                
                # Build a PSF model with psfex
                print('Building PSF model')
                sextractor_output_filename_g = f'{output_filename_g[:-5]}.cat'
                sextractor_output_filename_i = f'{output_filename_i[:-5]}.cat'
                psfex_command_g = f'psfex {sextractor_output_filename_g} -c {self.psfex_config} -PSF_DIR {self.output_dir}'
                psfex_command_i = f'psfex {sextractor_output_filename_i} -c {self.psfex_config} -PSF_DIR {self.output_dir}'
                subprocess.run(psfex_command_g, shell= subprocess.PIPE, cwd= self.config_dir)
                subprocess.run(psfex_command_i, shell=subprocess.PIPE, cwd= self.config_dir)
                
                # Perform final PSF photometry with sextractor using the PSF model from psfex
                print('Building final catalog')
                sextractor_psf_command_g = f'sex {output_filename_g} -c {self.sex_psf_config} -CATALOG_NAME {output_filename_g[:-5]}_final.cat -PSF_NAME {sextractor_output_filename_g[:-4]}.psf -WEIGHT_IMAGE {output_weightname_g} -ANALYSIS_THRESH  {thresh_g} -DETECT_THRESH {thresh_g}' 
                sextractor_psf_command_i = f'sex {output_filename_i} -c {self.sex_psf_config} -CATALOG_NAME {output_filename_i[:-5]}_final.cat -PSF_NAME {sextractor_output_filename_i[:-4]}.psf -WEIGHT_IMAGE {output_weightname_i} -ANALYSIS_THRESH  {thresh_i} -DETECT_THRESH {thresh_i}'
                subprocess.run(sextractor_psf_command_g, shell= subprocess.PIPE, cwd= self.config_dir)
                subprocess.run(sextractor_psf_command_i, shell= subprocess.PIPE, cwd= self.config_dir)

if __name__ == '__main__':
    input_filename_g= '/Users/mncavieres/Documents/2023-1/Investigacion2/Data/DECAM/Magwake9/c4d_201111_032132_osi_g_v1.fits'
    input_filename_i = '/Users/mncavieres/Documents/2023-1/Investigacion2/Data/DECAM/Magwake9/c4d_201111_035302_osi_i_v1.fits'
    output_dir = '/Users/mncavieres/Documents/2023-1/Investigacion2/Data/DECAM/Magwake9/workdir'
    sex_psf_config = 'default_psf.sex'
    sex_config  = 'default.sex'
    psfex_config = 'default_decam.psfex'
    config_dir  = 'pipeline_library/decam_lib/config'

    pipeline_test = Decam_pipeline(input_filename_g=input_filename_g, input_filename_i= input_filename_i,
                                    output_dir= output_dir, sex_psf_config= sex_psf_config, sex_config=sex_config,
                                    psfex_config= psfex_config, config_dir= config_dir)
    
    # Perform PSF photometry
    pipeline_test.photometry()

    # Make final catalogs
    pipeline_test.join_final_catalogs2()

    # Delete temporary files
    pipeline_test.delete_temp()