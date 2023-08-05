"""
napari-STPT reads zarr files and displays them
"""

import os
import sys
import napari
import numpy as np
import xarray as xr


if 'PyQt5' in sys.modules:
    from qtpy import QtCore, QtWidgets
    from qtpy.QtWidgets import QComboBox, QApplication, QCompleter, QMessageBox
    from qtpy.QtCore import QSortFilterProxyModel, Qt
else:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtWidgets import QComboBox, QApplication, QCompleter, QMessageBox
    from PySide2.QtCore import QSortFilterProxyModel, Qt
 
import SimpleITK as sitk
from scipy import ndimage, stats
import cv2
#from stardist.models import StarDist2D
from napari_animation import AnimationWidget
from PIL import Image, ImageDraw
import random
# import skimage.io
# from stardist.models import StarDist3D
#from csbdeep.utils import normalize
#from naparimovie import Movie
import math
import gc
import json
import tifffile
import pandas as pd



class ExtendedComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        # connect signals
        self.lineEdit().textEdited[str].connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)


    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))


    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)


    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)


class NapariSTPT:

    def __init__(self):
        self.scroll = None
        self.image_slice = None
        self.normalize_value = None

        self.pixel_size = None
        self.viewer = None
        self.comboBoxPath = None
        self.comboBoxResolution = None
        self.cb_C1 = None
        self.cb_C2 = None
        self.cb_C3 = None
        self.cb_C4 = None
        self.search_folder = None
        self.aligned_1 = None
        self.aligned_2 = None
        self.aligned_3 = None
        self.aligned_4 = None
        self.current_output_resolution = None

        self.cb_R_Axio = None
        # self.cb_R_Old = None
        self.cb_R_New = None
        self.spacing = [0,0,0]

        self.cb_perspective = None
        self.cb_isometric = None
        
        self.origin_x = None
        self.origin_y = None
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None

        self.spinN = None
        self.maxSizeN = None
        self.thresholdN = None
        self.slice_names = None

        self.align_x = None
        self.align_y = None
        self.corrected_align_x = None
        self.corrected_align_y = None
        self.ds1 = None
        self.ds2 = None
        self.ds4 = None
        self.ds8 = None
        self.ds16 = None
        self.ds32 = None
        
        self.m_volume_1 = None
        self.m_volume_1_multiplier = None
        self.m_volume_2 = None
        self.m_volume_2_multiplier = None
        self.m_volume_new = None

        #self.movie = None
        self.optical_slices = None
        self.nr_optical_slices = None
        self.optical_slices_available = None
        self.cb_correct_brightness_optical_section = None
        self.shape = None
        self.spacing_loaded = None

        self.crop_start_ratio_x = None
        self.crop_size_ratio_x = None
        self.crop_start_ratio_y = None
        self.crop_size_ratio_y = None

        self.crop = False
        self.old_method = False

        self.start_slice = None
        self.end_slice = None

        self.image_translation = None
        self.m_slice_spacing = None
        self.slice_spacing = None
        self.shapeText = None
        
        self.default_contrast_limits = None
        self.channels_start_at_0 = None
        
        self.bscale = None
        self.bzero = None
        
        self.layerC1 = None
        self.layerC2 = None
        self.layerC3 = None
        self.layerC4 = None
        
        self.loaded_2D = None
        self.loaded_3D = None
        
        self.bLoad3D = None
        self.bLoad2D = None
        
        self.number_of_sections = None
        
        self.image_folder = None
        self.axio = False

    def Make3DShape(self):

        output_resolution = float(self.pixel_size.text())
        
        data_length = len(self.viewer.layers['Shapes'].data[0])
        print(data_length)
        
        minX = 100000000
        maxX = 0
        minY = 100000000
        maxY = 0
        for i in range(0, data_length):
            print(self.viewer.layers['Shapes'].data[0][i])
            if minX > self.viewer.layers['Shapes'].data[0][i][1]:
                minX = self.viewer.layers['Shapes'].data[0][i][1]
            if maxX < self.viewer.layers['Shapes'].data[0][i][1]:
                maxX = self.viewer.layers['Shapes'].data[0][i][1]
            if minY > self.viewer.layers['Shapes'].data[0][i][2]:
                minY = self.viewer.layers['Shapes'].data[0][i][2]
            if maxY < self.viewer.layers['Shapes'].data[0][i][2]:
                maxY = self.viewer.layers['Shapes'].data[0][i][2]

        #print("crop to: {} {} {} {}".format(minX, maxX, minY, maxY))

        
        size_x = self.shape[0] * float(self.slice_spacing)/float(self.optical_slices) / output_resolution
        size_y = maxX
        size_z = maxY

        line_locations = []
        line_locations.append([[0, minX, minY], [size_x, minX, minY]])
        line_locations.append([[size_x, minX, minY], [size_x, size_y, minY]])
        line_locations.append([[size_x, size_y, minY], [0, size_y, minY]])
        line_locations.append([[0, size_y, minY], [0, minX, minY]])

        line_locations.append([[0, minX, size_z], [size_x, minX, size_z]])
        line_locations.append([[size_x, minX, size_z], [size_x, size_y, size_z]])
        line_locations.append([[size_x, size_y, size_z], [0, size_y, size_z]])
        line_locations.append([[0, size_y, size_z], [0, minX, size_z]])
        
        line_locations.append([[0, minX, minY], [0, minX, size_z]])
        line_locations.append([[size_x, minX, minY], [size_x, minX, size_z]])
        line_locations.append([[size_x, size_y, minY], [size_x, size_y, size_z]])
        line_locations.append([[0, size_y, minY], [0, size_y, size_z]])

        width = np.mean([size_x, size_y, size_z]) / 500
        
        self.viewer.add_shapes(np.asarray(line_locations), name = 'crop box',shape_type='line', edge_color = "white", edge_width = width)



    def MakeBoundingBox(self):
        #with napari.gui_qt():
        
        size_x = (self.shape[0]-1)# * float(self.slice_spacing)/float(self.optical_slices) / output_resolution) - 1
        size_y = (self.shape[1]-1)#  * output_resolution
        size_z = (self.shape[2]-1)#  * output_resolution

        line_locations = []
        line_locations.append([[0, 0, 0], [size_x, 0, 0]])
        line_locations.append([[size_x, 0, 0], [size_x, size_y, 0]])
        line_locations.append([[size_x, size_y, 0], [0, size_y, 0]])
        line_locations.append([[0, size_y, 0], [0, 0, 0]])

        line_locations.append([[0, 0, size_z], [size_x, 0, size_z]])
        line_locations.append([[size_x, 0, size_z], [size_x, size_y, size_z]])
        line_locations.append([[size_x, size_y, size_z], [0, size_y, size_z]])
        line_locations.append([[0, size_y, size_z], [0, 0, size_z]])
        
        line_locations.append([[0, 0, 0], [0, 0, size_z]])
        line_locations.append([[size_x, 0, 0], [size_x, 0, size_z]])
        line_locations.append([[size_x, size_y, 0], [size_x, size_y, size_z]])
        line_locations.append([[0, size_y, 0], [0, size_y, size_z]])

        width = np.mean([size_x, size_y, size_z]) / 500
        
        output_resolution = float(self.pixel_size.text())
        scale_x = float(self.slice_spacing)/float(self.optical_slices) / output_resolution
        self.viewer.add_shapes(np.asarray(line_locations), name = 'bounding box',shape_type='line', scale=(scale_x, 1, 1), edge_color = "white", edge_width = width)

    def Load(self, text):
        

        def AlignAXIO(axio_volume, sample_name, slice_names, resolution):
            
            sample_name = sample_name[:-5]
            
            new_volume = np.zeros(axio_volume.shape)

            df = pd.read_parquet(f"/home/tristan/Shared/imaxt_reg/{sample_name}/{sample_name}_EXT_AXIO_STPT_all_reg.parquet", engine='pyarrow')

            filtered_df = df[(df['ranking'] == 1) & ((df['FLAG'] == 1) | (df['FLAG'] == 0))]
            #filtered_df = df[(df['ranking'] == 1)]
            
            for index, element in enumerate(slice_names):
                
                row = filtered_df[filtered_df['D_S'] == element]
                
                if not row.empty:

                    axio_location = int(row.iloc[0, 4][1:]) - 1

                    axio_image = axio_volume[index,:,:]

                    #flip image
                    if row.iloc[0, 8] == 0.0:
                        axio_image = axio_image[::-1,:]
                    if row.iloc[0, 8] == 1.0:
                        axio_image = axio_image[:,::-1]

                    axio_image = np.asarray(axio_image)

                    M = np.array([[row.iloc[0, 24], row.iloc[0, 25], row.iloc[0, 26]/resolution], [row.iloc[0, 27], row.iloc[0, 28], row.iloc[0, 29]/resolution]])

                    rows, cols = axio_image.shape
                    affine_np_img = cv2.warpAffine(axio_image, M[:2,:], (cols, rows))

                    new_volume[axio_location,:,:] = affine_np_img

            return new_volume

        verbose = True

        load_in_reference = False
        
        
        if self.aligned_1 is not None or self.aligned_2 is not None or self.aligned_3 is not None or self.aligned_4 is not None:
            msgBox = QMessageBox()
            msgBox.setText("Loading...")
            msgBox.setInformativeText("Load in current reference space?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.Yes)
            reply = msgBox.exec_()
            if reply == QMessageBox.Yes:
                load_in_reference = True
                reference_spacing = self.spacing
    

        if load_in_reference:
            try:
                reference_size = self.aligned_1.shape
            except Exception:
                pass
            try:
                reference_size = self.aligned_2.shape
            except Exception:
                pass
            try:
                reference_size = self.aligned_3.shape
            except Exception:
                pass
            try:
                reference_size = self.aligned_4.shape
            except Exception:
                pass
            
            if verbose:
                print(f"reference_size: {reference_size}")
    
            
        # Remove previous volumes
        try:
            if not load_in_reference:
                self.viewer.layers.remove('C1')
            del self.aligned_1
            self.aligned_1 = None
        except Exception:
            pass
        try:
            if not load_in_reference:
                self.viewer.layers.remove('C2')
            del self.aligned_2
            self.aligned_2 = None
        except Exception:
            pass
        try:
            if not load_in_reference:
                self.viewer.layers.remove('C3')
            del self.aligned_3
            self.aligned_3 = None
        except Exception:
            pass
        try:
            if not load_in_reference:
                self.viewer.layers.remove('C4')
            del self.aligned_4
            self.aligned_4 = None
        except Exception:
            pass

        # Clear memory
        gc.collect()

        
        
        for folder in self.image_folders:
    
            if folder == '/data/meds1_c/storage/processed0/stpt/':
                self.old_method = True
            else:
                self.old_method = False
                
            file_name = folder + str(self.comboBoxPath.currentText()) + '/mos'
            if os.path.exists(file_name):
                self.image_folder = folder
                break
            file_name = folder + str(self.comboBoxPath.currentText()) + '/mos.zarr'
            if os.path.exists(file_name):
                self.image_folder = folder
                break
                     
        if verbose:
            print(f"folder location: " + self.image_folder)
            
        
        file_name = self.image_folder + str(self.comboBoxPath.currentText()) + '/mos'
        self.default_contrast_limits = [0,30000]
        self.thresholdN.setText("1000")
        self.channels_start = 0
        if not os.path.exists(file_name):
            file_name = self.image_folder + str(self.comboBoxPath.currentText()) + '/mos.zarr'
            self.default_contrast_limits = [0,30]
            self.thresholdN.setText("0.3")
            self.channels_start = 1
        print(file_name)

        # Try to read only the meta data using the consolidated flag as True
        # Currently not used
        try:
            self.ds1 = xr.open_zarr(file_name, consolidated=False)
            # print("not trying consolidated")
        except Exception:
            print("none-consolidated")
            self.ds1 = xr.open_zarr(file_name)

        
        # Read the image spacing
        if self.old_method:
            self.spacing = (self.ds1['S001'].attrs['scale'])
        else:
            self.spacing = [1,1]
            try:
                self.spacing[0] = float(json.loads(self.ds1.attrs['multiscale'])['metadata']['scale'][0])
                self.spacing[1] = float(json.loads(self.ds1.attrs['multiscale'])['metadata']['scale'][1])
            except:
                try:
                    self.spacing[0] = 10 * float(json.loads(self.ds1['S001'].attrs['scale'])["x"])
                    self.spacing[1] = 10 * float(json.loads(self.ds1['S001'].attrs['scale'])["y"])
                    # self.spacing[2] = 10 * float(json.loads(self.ds1['S001'].attrs['scale'])["z"])
                except:
                    print("spacing not defined")
                
                
        if load_in_reference:
            self.spacing = reference_spacing
            
            
                
        if verbose:
            print(f"spacing ({self.spacing[0]}, {self.spacing[1]})")

        # Read the parameters to convert the voxel values (bscale and bzero)
        if self.old_method:
            self.bscale = self.ds1.attrs['bscale']
            self.bzero = self.ds1.attrs['bzero']
        else:
            try:
                self.bscale = self.ds1['S001'].attrs['bscale']
                self.bzero = self.ds1['S001'].attrs['bzero']
            except:
                self.bscale = 1
                self.bzero = 0

        if verbose:
            print(f"bscale {self.bscale}, bzero {self.bzero}")

            


        # Get number of sections
        if self.axio:
            self.number_of_sections = len(list(self.ds1))
            self.optical_slices_available = 1
        else:
            if self.old_method:
                self.number_of_sections = len(set(self.ds1.attrs['cube_reg']['slice']))
            else:
                try:
                    self.number_of_sections = int(json.loads(self.ds1['S001'].attrs['raw_meta'])['sections'])
                except:
                    self.number_of_sections = int(json.loads(self.ds1.attrs['multiscale'])['metadata']['number_of_sections'])
        
        if verbose:
            print(f"Number of sections: {self.number_of_sections}")
            
            
        #print("")
        #print(self.ds1.attrs)
        #print("")

        # Read the translation values
        if self.old_method:
            self.align_x = self.ds1.attrs['cube_reg']['abs_dx']
            self.align_y = self.ds1.attrs['cube_reg']['abs_dy']
        else:
            self.align_x = []
            self.align_y = []

            for z in range(0, self.number_of_sections):
                # slice_name = f"S{(z+1):03d}"
                # self.align_x.append(self.ds1[slice_name].attrs['offsets']['x'])
                # self.align_y.append(self.ds1[slice_name].attrs['offsets']['y'])
                self.align_x.append(0)
                self.align_y.append(0)

        if verbose:
            print(f"align_x {self.align_x}")
            print(f"align_y {self.align_y}")
        

        # User defined output pixel size
        output_resolution = float(self.pixel_size.text())

        if verbose:
            print(f"output pixel size {output_resolution}")


        # Calculate at which resolution the image should be read based on the image spacing and output pixel size
        resolution = 32
        index = 5
        if (output_resolution / 0.5) < 32:
            resolution = 16
            index = 4
        if (output_resolution / 0.5) < 16:
            resolution = 8
            index = 3
        if (output_resolution / 0.5) < 8:
            resolution = 4
            index = 2
        if (output_resolution / 0.5) < 4:
            resolution = 2
            index = 1
        if (output_resolution / 0.5) < 2:
            resolution = 1
            index = 0

        if verbose:
            print(f"loading at resolution {resolution} with index {index}")
        

        # Open the image file
        if self.axio:
            ds = xr.open_zarr(file_name, group='l.{0:d}'.format(resolution))
        else:
            if self.old_method:
                gr = self.ds1.attrs["multiscale"]['datasets'][index]['path']
                ds = xr.open_zarr(file_name, group=gr)
            else:
                gr = json.loads(self.ds1.attrs["multiscale"])['datasets'][index]['path']
                ds = xr.open_zarr(file_name, group=gr)

        # Get the number of optical slices that are available
        if self.axio:
            self.optical_slices_available = 1
        else:
            self.optical_slices_available = len(ds.z)

        if verbose:
            print(f"optical slices available: {self.optical_slices_available}")
        
        # Slice spacing given by the user, which should be extracted from the file name
        self.slice_spacing = float(self.m_slice_spacing.text())

        # Get the optical slice spacing
        if self.old_method or self.axio:
            # assume that the optical slices do not overlap
            optical_section_spacing = self.slice_spacing / self.optical_slices_available
        else:
            try:
                optical_section_spacing = float(json.loads(self.ds1['S001'].attrs['raw_meta'])['zres'])
            except:
                optical_section_spacing = float(json.loads(self.ds1.attrs['multiscale'])['metadata']['optical_section_spacing'])

        if verbose:
            print(f"optical_slices zres: {optical_section_spacing}")


        # Calculate how many optical slices to use
        if self.optical_slices_available > 1:
            expected_nr_of_slices = round(self.slice_spacing / optical_section_spacing)
            if self.optical_slices_available > expected_nr_of_slices:
                self.optical_slices = expected_nr_of_slices
            else:
                self.optical_slices = self.optical_slices_available
        else:
            self.optical_slices = 1


        # Get slice names
        if self.old_method:
            self.slice_names = self.ds1.attrs['cube_reg']['slice']
        else:
            self.slice_names = []
            for z in range(0, self.number_of_sections):
                slice_name = f"S{(z+1):03d}"
                for i in range(0, self.optical_slices):
                    self.slice_names.append(slice_name)
        
        if verbose:
            print(f"slice names: {self.slice_names}")


        if verbose:
            print(f"number of optical slices used: {self.optical_slices}")

        # Make copies of the translations for all the optical slices used
        if self.old_method:
            self.corrected_align_x = self.align_x
            self.corrected_align_y = self.align_y
        else:
            self.corrected_align_x = []
            for index, value in enumerate(self.align_x):
                for i in range(0,self.optical_slices):
                    self.corrected_align_x.append(value)

            self.corrected_align_y = []
            for index, value in enumerate(self.align_y):
                for i in range(0,self.optical_slices):
                    self.corrected_align_y.append(value)


        if verbose:
            print(f"There are {len(self.corrected_align_x)} translations")

        # Set perspective view which aids the navigation
        self.viewer.window.qt_viewer.camera._3D_camera.fov = 45

        # Store the output resolution in which this volume was loaded
        self.current_output_resolution = float(self.pixel_size.text())

        # Define start slice
        if self.start_slice.text() == "":
            start_slice_number = 0
            chop_bottom = 0
        else:
            start_slice_number = int(math.floor(float(self.start_slice.text())/float(self.optical_slices)))
            chop_bottom = int(self.start_slice.text()) - (self.optical_slices * start_slice_number) 

        # Define end slice
        if self.end_slice.text() == "":
            end_slice_number = self.number_of_sections-1
            chop_top = 0
        else:
            end_slice_number = int(math.floor(float(self.end_slice.text())/float(self.optical_slices)))
            chop_top = (self.optical_slices * (end_slice_number + 1) -1) - int(self.end_slice.text()) 

        # Define number of slices
        number_of_slices = end_slice_number - start_slice_number + 1
        if verbose:
            print(f"number_of_slices {number_of_slices}")

        
        # Load the volume for each channel seperately
        if self.cb_C1.isChecked():
            print("loading C1")
            
            if self.axio:
                try:
                    volume_1_temp = (ds.sel(channel=self.channels_start, type='mosaic').to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_1_temp = (ds.sel(channel=self.channels_start).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
            else:
                try:
                    volume_1_temp = (ds.sel(channel=self.channels_start, type='mosaic', z=0).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_1_temp = (ds.sel(channel=self.channels_start, z=0).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
            
            if self.crop:
                spacing_x = resolution*0.1*self.spacing[0]
                spacing_y = resolution*0.1*self.spacing[1]

                size_y = int(math.floor((self.crop_end_x - self.crop_start_x) / spacing_x))
                size_z = int(math.floor((self.crop_end_y - self.crop_start_y) / spacing_y))
                start_y = int(math.floor(self.crop_start_x / spacing_x))
                start_z = int(math.floor(self.crop_start_y / spacing_y))
            else:
                if self.axio:
                    size_y = int(math.floor(volume_1_temp.shape[2]))
                    size_z = int(math.floor(volume_1_temp.shape[3]))
                else:
                    size_y = int(math.floor(volume_1_temp.shape[1]))
                    size_z = int(math.floor(volume_1_temp.shape[2]))
                start_y = 0
                start_z = 0
                
            volume_1 = np.zeros((self.optical_slices*number_of_slices, size_y, size_z), dtype=np.float32)
            
            if number_of_slices != volume_1_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z].shape[0]:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("One or more slices appear to be missing")
                msg.setInformativeText("Find the missing slice(s) by using the Load slice function and scrolling through the slices until an error message is displayed. Then set a Slices range to avoid this slice.")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok)
                retval = msg.exec_()
                return
            
            if self.axio:
                volume_1_temp = volume_1_temp[:,0,:,:]
                volume_1_temp = AlignAXIO(volume_1_temp, str(self.comboBoxPath.currentText()), self.slice_names, resolution)
            
            volume_1[0::self.optical_slices, :, :] = volume_1_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]
            
            for optical_slice in range(1, self.optical_slices):
                # volume_1_temp = (ds.sel(channel=self.channels_start, type='mosaic', z=optical_slice).to_array(
                # ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                # volume_1[optical_slice::self.optical_slices, :, :] = volume_1_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]
                
                try:
                    volume_1_temp = (ds.sel(channel=self.channels_start, type='mosaic', z=optical_slice).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_1_temp = (ds.sel(channel=self.channels_start, z=optical_slice).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                    
                volume_1[optical_slice::self.optical_slices, :, :] = volume_1_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]

            # Normalize the brightness changes between optical sections
            if self.cb_correct_brightness_optical_section.isChecked():
                print("correcting brightness of optical sections C1")
                self.Normalize_slices(volume_1, self.optical_slices)

            print("aligning C1")
            self.aligned_1 = self.AlignNew(volume_1, resolution, output_resolution, start_slice_number*self.optical_slices, self.spacing)
            
            if load_in_reference:
                self.aligned_1 = self.aligned_1[:,0:reference_size[1],0:reference_size[2]]
                
            self.aligned_1 = self.aligned_1[chop_bottom:self.aligned_1.shape[0]-chop_top,:,:]
            self.shape = self.aligned_1.shape
            
            if verbose:
                print(f"self.shape {self.shape}")
            
            self.viewer.add_image([self.aligned_1], name='C1', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='bop purple', contrast_limits=self.default_contrast_limits)

        if self.cb_C2.isChecked():
            print("loading C2")
            
            if self.axio:
                try:
                    volume_2_temp = (ds.sel(channel=self.channels_start + 1, type='mosaic').to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_2_temp = (ds.sel(channel=self.channels_start + 1).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
            else:
                try:
                    volume_2_temp = (ds.sel(channel=self.channels_start + 1, type='mosaic', z=0).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_2_temp = (ds.sel(channel=self.channels_start + 1, z=0).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)


            if self.crop:
                spacing_x = resolution*0.1*self.spacing[0]
                spacing_y = resolution*0.1*self.spacing[1]

                size_y = int(math.floor((self.crop_end_x - self.crop_start_x) / spacing_x))
                size_z = int(math.floor((self.crop_end_y - self.crop_start_y) / spacing_y))
                start_y = int(math.floor(self.crop_start_x / spacing_x))
                start_z = int(math.floor(self.crop_start_y / spacing_y))
            else:
                if self.axio:
                    size_y = int(math.floor(volume_2_temp.shape[2]))
                    size_z = int(math.floor(volume_2_temp.shape[3]))
                else:
                    size_y = int(math.floor(volume_2_temp.shape[1]))
                    size_z = int(math.floor(volume_2_temp.shape[2]))
                start_y = 0
                start_z = 0

            volume_2 = np.zeros((self.optical_slices*number_of_slices, size_y, size_z), dtype=np.float32)
            
            if number_of_slices != volume_2_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z].shape[0]:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("One or more slices appear to be missing")
                msg.setInformativeText("Try to set the Slices range to avoid the missing slices")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok)
                retval = msg.exec_()
                return
            
            if self.axio:
                volume_2_temp = volume_2_temp[:,0,:,:]
                volume_2_temp = AlignAXIO(volume_2_temp, str(self.comboBoxPath.currentText()), self.slice_names, resolution)
            
            volume_2[0::self.optical_slices, :, :] = volume_2_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]

            for optical_slice in range(1, self.optical_slices):
                
                try:
                    volume_2_temp = (ds.sel(channel=self.channels_start + 1, type='mosaic', z=optical_slice).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_2_temp = (ds.sel(channel=self.channels_start + 1, z=optical_slice).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                    
                # volume_2_temp = (ds.sel(channel=self.channels_start + 1, type='mosaic', z=optical_slice).to_array(
                # ).data * self.bscale + self.bzero).astype(dtype=np.float16)
                volume_2[optical_slice::self.optical_slices, :, :] = volume_2_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]

            # Normalize the brightness changes between optical sections
            if self.cb_correct_brightness_optical_section.isChecked():
                print("correcting brightness of optical sections C2")
                self.Normalize_slices(volume_2, self.optical_slices)

            print("aligning C2")
            self.aligned_2 = self.AlignNew(volume_2, resolution, output_resolution, start_slice_number*self.optical_slices, self.spacing)
            
            if load_in_reference:
                self.aligned_2 = self.aligned_2[:,0:reference_size[1],0:reference_size[2]]
                
            self.aligned_2 = self.aligned_2[chop_bottom:self.aligned_2.shape[0]-chop_top,:,:]
            self.shape = self.aligned_2.shape
            self.viewer.add_image([self.aligned_2], name='C2', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='red', contrast_limits=self.default_contrast_limits)

        if self.cb_C3.isChecked():
            print("loading C3")
            
            if self.axio:
                try:
                    volume_3_temp = (ds.sel(channel=self.channels_start + 2, type='mosaic').to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_3_temp = (ds.sel(channel=self.channels_start + 2).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
            else:
                try:
                    volume_3_temp = (ds.sel(channel=self.channels_start + 2, type='mosaic', z=0).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_3_temp = (ds.sel(channel=self.channels_start + 2, z=0).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)

            
            if self.crop:
                spacing_x = resolution*0.1*self.spacing[0]
                spacing_y = resolution*0.1*self.spacing[1]

                size_y = int(math.floor((self.crop_end_x - self.crop_start_x) / spacing_x))
                size_z = int(math.floor((self.crop_end_y - self.crop_start_y) / spacing_y))
                start_y = int(math.floor(self.crop_start_x / spacing_x))
                start_z = int(math.floor(self.crop_start_y / spacing_y))
            else:
                if self.axio:
                    size_y = int(math.floor(volume_3_temp.shape[2]))
                    size_z = int(math.floor(volume_3_temp.shape[3]))
                else:
                    size_y = int(math.floor(volume_3_temp.shape[1]))
                    size_z = int(math.floor(volume_3_temp.shape[2]))
                start_y = 0
                start_z = 0


            #print(f"start_y {start_y}, start_z {start_z}, size_y {size_y}, size_z {size_z}")

            volume_3 = np.zeros((self.optical_slices*number_of_slices, size_y, size_z), dtype=np.float32)

            # print(f"volume_3.shape {volume_3.shape}")
            # print(f"self.optical_slices {self.optical_slices}")
            # print(f"start_slice_number {start_slice_number}")
            # print(f"end_slice_number {end_slice_number}")
           
            if number_of_slices != volume_3_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z].shape[0]:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("One or more slices appear to be missing")
                msg.setInformativeText("Try to set the Slices range to avoid the missing slices")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok)
                retval = msg.exec_()
                return
            
            if self.axio:
                volume_3_temp = volume_3_temp[:,0,:,:]
                volume_3_temp = AlignAXIO(volume_3_temp, str(self.comboBoxPath.currentText()), self.slice_names, resolution)
            
            volume_3[0::self.optical_slices, :, :] = volume_3_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]
            
            for optical_slice in range(1, self.optical_slices):
#                 volume_3_temp = (ds.sel(channel=self.channels_start + 2, type='mosaic', z=optical_slice).to_array(
#                 ).data * self.bscale + self.bzero).astype(dtype=np.float32)
#                 volume_3[optical_slice::self.optical_slices, :, :] = volume_3_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]
                
                try:
                    volume_3_temp = (ds.sel(channel=self.channels_start + 2, type='mosaic', z=optical_slice).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_3_temp = (ds.sel(channel=self.channels_start + 2, z=optical_slice).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                    
                volume_3[optical_slice::self.optical_slices, :, :] = volume_3_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]

            # Normalize the brightness changes between optical sections
            if self.cb_correct_brightness_optical_section.isChecked():
                print("correcting brightness of optical sections C3")
                self.Normalize_slices(volume_3, self.optical_slices)

            print("aligning C3")
            self.aligned_3 = self.AlignNew(volume_3, resolution, output_resolution, start_slice_number*self.optical_slices, self.spacing)
            
            if load_in_reference:
                self.aligned_3 = self.aligned_3[:,0:reference_size[1],0:reference_size[2]]
                
            self.aligned_3 = self.aligned_3[chop_bottom:self.aligned_3.shape[0]-chop_top,:,:]
            self.shape = self.aligned_3.shape
            self.viewer.add_image([self.aligned_3], name='C3', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='green', contrast_limits=self.default_contrast_limits)

        if self.cb_C4.isChecked():
            print("loading C4")

            if self.axio:
                try:
                    volume_4_temp = (ds.sel(channel=self.channels_start + 3, type='mosaic').to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_4_temp = (ds.sel(channel=self.channels_start + 3).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
            else:
                try:
                    volume_4_temp = (ds.sel(channel=self.channels_start + 3, type='mosaic', z=0).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_4_temp = (ds.sel(channel=self.channels_start + 3, z=0).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)

            if self.crop:
                spacing_x = resolution*0.1*self.spacing[0]
                spacing_y = resolution*0.1*self.spacing[1]

                size_y = int(math.floor((self.crop_end_x - self.crop_start_x) / spacing_x))
                size_z = int(math.floor((self.crop_end_y - self.crop_start_y) / spacing_y))
                start_y = int(math.floor(self.crop_start_x / spacing_x))
                start_z = int(math.floor(self.crop_start_y / spacing_y))
            else:
                if self.axio:
                    size_y = int(math.floor(volume_4_temp.shape[2]))
                    size_z = int(math.floor(volume_4_temp.shape[3]))
                else:
                    size_y = int(math.floor(volume_4_temp.shape[1]))
                    size_z = int(math.floor(volume_4_temp.shape[2]))
                start_y = 0
                start_z = 0

            volume_4 = np.zeros((self.optical_slices*number_of_slices, size_y, size_z), dtype=np.float32)
            
            if number_of_slices != volume_4_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z].shape[0]:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("One or more slices appear to be missing")
                msg.setInformativeText("Try to set the Slices range to avoid the missing slices")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok)
                retval = msg.exec_()
                return
            
            if self.axio:
                volume_4_temp = volume_4_temp[:,0,:,:]
                volume_4_temp = AlignAXIO(volume_4_temp, str(self.comboBoxPath.currentText()), self.slice_names, resolution)
            
            volume_4[0::self.optical_slices, :, :] = volume_4_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]

            for optical_slice in range(1, self.optical_slices):
#                 volume_4_temp = (ds.sel(channel=self.channels_start + 3, type='mosaic', z=optical_slice).to_array(
#                 ).data * self.bscale + self.bzero).astype(dtype=np.float32)
#                 volume_4[optical_slice::self.optical_slices, :, :] = volume_4_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]
                
                try:
                    volume_4_temp = (ds.sel(channel=self.channels_start + 3, type='mosaic', z=optical_slice).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                except:
                    volume_4_temp = (ds.sel(channel=self.channels_start + 3, z=optical_slice).to_array(
                    ).data * self.bscale + self.bzero).astype(dtype=np.float32)
                    
                volume_4[optical_slice::self.optical_slices, :, :] = volume_4_temp[start_slice_number:end_slice_number+1, start_y:start_y+size_y, start_z:start_z+size_z]

            # Normalize the brightness changes between optical sections
            if self.cb_correct_brightness_optical_section.isChecked():
                print("correcting brightness of optical sections C4")
                self.Normalize_slices(volume_4, self.optical_slices)

            print("aligning C4")
            self.aligned_4 = self.AlignNew(volume_4, resolution, output_resolution, start_slice_number*self.optical_slices, self.spacing)
            
            if load_in_reference:
                self.aligned_4 = self.aligned_4[:,0:reference_size[1],0:reference_size[2]]
            
            self.aligned_4 = self.aligned_4[chop_bottom:self.aligned_4.shape[0]-chop_top,:,:]
            self.shape = self.aligned_4.shape
            self.viewer.add_image([self.aligned_4], name='C4', scale=((float(self.slice_spacing)/float(self.optical_slices)) / output_resolution, 1, 1), 
                                  blending='additive', colormap='bop blue', contrast_limits=self.default_contrast_limits)

        spacing_loaded = [float(self.slice_spacing)/float(self.optical_slices), output_resolution, output_resolution]

        self.MakeBoundingBox()

    def LoadInRegion(self, text):
        
        zoom = self.viewer.window.qt_viewer.camera.zoom
        angles = self.viewer.window.qt_viewer.camera.angles
        
        if any(i.name == 'bounding box' for i in self.viewer.layers):
            self.viewer.layers.remove('bounding box')
        
        if any(i.name == 'crop box' for i in self.viewer.layers):
            self.viewer.layers.remove('crop box')

        print(self.viewer.layers['Shapes'].data)
        data_length = len(self.viewer.layers['Shapes'].data[0])
        print(data_length)
        minX = 100000000
        maxX = 0
        minY = 100000000
        maxY = 0
        for i in range(0, data_length):
            print(self.viewer.layers['Shapes'].data[0][i])
            if minX > self.viewer.layers['Shapes'].data[0][i][1]:
                minX = self.viewer.layers['Shapes'].data[0][i][1]
            if maxX < self.viewer.layers['Shapes'].data[0][i][1]:
                maxX = self.viewer.layers['Shapes'].data[0][i][1]
            if minY > self.viewer.layers['Shapes'].data[0][i][2]:
                minY = self.viewer.layers['Shapes'].data[0][i][2]
            if maxY < self.viewer.layers['Shapes'].data[0][i][2]:
                maxY = self.viewer.layers['Shapes'].data[0][i][2]


        print("crop to: {} {} {} {}".format(minX, maxX, minY, maxY))
        print("self.origin_x: {}".format(self.origin_x))
        print("self.origin_y: {}".format(self.origin_y))
        print("self.current_output_resolution: {}".format(self.current_output_resolution))
        
        self.crop_start_x = self.origin_x + (minX * self.current_output_resolution)
        self.crop_start_y = self.origin_y + (minY * self.current_output_resolution)
        self.crop_end_x = self.origin_x + (maxX * self.current_output_resolution)
        self.crop_end_y = self.origin_y + (maxY * self.current_output_resolution)

        self.origin_x = self.crop_start_x
        self.origin_y = self.crop_start_y

        if self.aligned_1 is not None and self.cb_C1.isChecked() and any(i.name == 'C1' for i in self.viewer.layers):
            self.crop_start_ratio_x = self.aligned_1.shape[1]/minX
            self.crop_size_ratio_x = self.aligned_1.shape[1]/(maxX-minX)
            self.crop_start_ratio_y = self.aligned_1.shape[2]/minY
            self.crop_size_ratio_y = self.aligned_1.shape[2]/(maxY-minY)
        elif self.aligned_2 is not None and self.cb_C2.isChecked() and any(i.name == 'C2' for i in self.viewer.layers):
            self.crop_start_ratio_x = self.aligned_2.shape[1]/minX
            self.crop_size_ratio_x = self.aligned_2.shape[1]/(maxX-minX)
            self.crop_start_ratio_y = self.aligned_2.shape[2]/minY
            self.crop_size_ratio_y = self.aligned_2.shape[2]/(maxY-minY)
        elif self.aligned_3 is not None and self.cb_C3.isChecked() and any(i.name == 'C3' for i in self.viewer.layers):
            self.crop_start_ratio_x = self.aligned_3.shape[1]/minX
            self.crop_size_ratio_x = self.aligned_3.shape[1]/(maxX-minX)
            self.crop_start_ratio_y = self.aligned_3.shape[2]/minY
            self.crop_size_ratio_y = self.aligned_3.shape[2]/(maxY-minY)
        elif self.aligned_4 is not None and self.cb_C4.isChecked() and any(i.name == 'C4' for i in self.viewer.layers):
            self.crop_start_ratio_x = self.aligned_4.shape[1]/minX
            self.crop_size_ratio_x = self.aligned_4.shape[1]/(maxX-minX)
            self.crop_start_ratio_y = self.aligned_4.shape[2]/minY
            self.crop_size_ratio_y = self.aligned_4.shape[2]/(maxY-minY)

        self.viewer.layers.remove('Shapes')

        print(f"crop_start_x {self.crop_start_x}, crop_start_y {self.crop_start_y}, crop_size_x {self.crop_end_x}, crop_size_y {self.crop_end_y}")

        self.crop = True
        self.Load(text)
        self.crop = False

        # self.MakeBoundingBox()
        
        self.viewer.window.qt_viewer.camera.center = (self.shape[0]/2, self.shape[1]/2, self.shape[2]/2 )
        self.viewer.window.qt_viewer.camera.angles = angles
        self.viewer.window.qt_viewer.camera.zoom = zoom


    def CropToRegion(self):

        if any(i.name == 'bounding box' for i in self.viewer.layers):
            self.viewer.layers.remove('bounding box')
        
        if any(i.name == 'crop box' for i in self.viewer.layers):
            self.viewer.layers.remove('crop box')

        output_resolution = float(self.pixel_size.text())
        data_length = len(self.viewer.layers['Shapes'].data[0])
        print(data_length)
        minX = 100000000
        maxX = 0
        minY = 100000000
        maxY = 0
        for i in range(0, data_length):
            print(self.viewer.layers['Shapes'].data[0][i])
            if minX > self.viewer.layers['Shapes'].data[0][i][1]:
                minX = self.viewer.layers['Shapes'].data[0][i][1]
            if maxX < self.viewer.layers['Shapes'].data[0][i][1]:
                maxX = self.viewer.layers['Shapes'].data[0][i][1]
            if minY > self.viewer.layers['Shapes'].data[0][i][2]:
                minY = self.viewer.layers['Shapes'].data[0][i][2]
            if maxY < self.viewer.layers['Shapes'].data[0][i][2]:
                maxY = self.viewer.layers['Shapes'].data[0][i][2]



        self.origin_x = self.origin_x + (output_resolution * minX)
        self.origin_y = self.origin_y + (output_resolution * minY)

        print("crop to: {} {} {} {}".format(minX, maxX, minY, maxY))


        if self.aligned_1 is not None and self.cb_C1.isChecked() and any(i.name == 'C1' for i in self.viewer.layers):
            self.aligned_1 = self.aligned_1[:, int(
                minX):int(maxX), int(minY):int(maxY)]
            self.shape = self.aligned_1.shape
            self.viewer.layers.remove('C1')
            self.image_translation = (int(minX*output_resolution), int(minY*output_resolution))
            self.viewer.add_image([self.aligned_1], name='C1', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='bop purple', contrast_limits=self.default_contrast_limits)
        if self.aligned_2 is not None and self.cb_C2.isChecked() and any(i.name == 'C2' for i in self.viewer.layers):
            self.aligned_2 = self.aligned_2[:, int(
                minX):int(maxX), int(minY):int(maxY)]
            self.shape = self.aligned_2.shape
            self.viewer.layers.remove('C2')
            self.image_translation = (int(minX*output_resolution), int(minY*output_resolution))
            self.viewer.add_image([self.aligned_2], name='C2', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='red', contrast_limits=self.default_contrast_limits)
        if self.aligned_3 is not None and self.cb_C3.isChecked() and any(i.name == 'C3' for i in self.viewer.layers):
            self.aligned_3 = self.aligned_3[:, int(
                minX):int(maxX), int(minY):int(maxY)]
            self.shape = self.aligned_3.shape
            self.viewer.layers.remove('C3')
            self.image_translation = (int(minX*output_resolution), int(minY*output_resolution))
            self.viewer.add_image([self.aligned_3], name='C3', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='green', contrast_limits=self.default_contrast_limits)
        if self.aligned_4 is not None and self.cb_C4.isChecked() and any(i.name == 'C4' for i in self.viewer.layers):
            self.aligned_4 = self.aligned_4[:, int(
                minX):int(maxX), int(minY):int(maxY)]
            self.shape = self.aligned_4.shape
            self.viewer.layers.remove('C4')
            self.image_translation = (int(minX*output_resolution), int(minY*output_resolution))
            self.viewer.add_image([self.aligned_4], name='C4', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='bop blue', contrast_limits=self.default_contrast_limits)

            
        self.viewer.layers.remove('Shapes')
        self.MakeBoundingBox()
        

        # print(self.viewer.window.qt_viewer.camera.center)
        self.viewer.window.qt_viewer.camera.center = (self.shape[0]/2, self.shape[1]/2, self.shape[2]/2 )
        # print(self.viewer.window.qt_viewer.camera.center)

          
    def set_image_slice_value(self):
        if not self.loaded_2D:
            return
        
        self.image_slice.setText(str(self.scroll.value()))  
        
        optical_slice = self.scroll.value() % self.optical_slices_available
        z = math.floor(self.scroll.value() / self.optical_slices_available)
        
        

        if self.old_method:
            slice_name = self.slice_names[z]
        else:
            slice_name = f"S{(z+1):03d}"
        
        
        if self.cb_C1.isChecked():
            try:
                im1 = (self.ds1[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im2 = (self.ds2[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im4 = (self.ds4[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im8 = (self.ds8[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im16 = (self.ds16[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im32 = (self.ds32[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
            except:
                try:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                except:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
            
            self.layerC1.data = [im1, im2, im4, im8, im16, im32]

            # self.viewer.add_image([im1, im2, im4, im8, im16, im32], multiscale=True,
            #                           name='C1', blending='additive', colormap='bop purple', contrast_limits=self.default_contrast_limits)

        if self.cb_C2.isChecked():
            try:
                im1 = (self.ds1[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im2 = (self.ds2[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im4 = (self.ds4[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im8 = (self.ds8[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im16 = (self.ds16[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im32 = (self.ds32[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
            except:
                try:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                except:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()

            self.layerC2.data = [im1, im2, im4, im8, im16, im32]
            
            # self.viewer.add_image([im1, im2, im4, im8, im16, im32], multiscale=True,
            #                             name='C2', blending='additive', colormap='red', contrast_limits=self.default_contrast_limits)
                

        if self.cb_C3.isChecked():
            try:
                im1 = (self.ds1[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im2 = (self.ds2[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im4 = (self.ds4[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im8 = (self.ds8[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im16 = (self.ds16[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im32 = (self.ds32[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
            except:
                try:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                except:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()

            self.layerC3.data = [im1, im2, im4, im8, im16, im32]
            
            # self.viewer.add_image([im1, im2, im4, im8, im16, im32], multiscale=True,
            #                           name='C3', blending='additive', colormap='green', contrast_limits=self.default_contrast_limits)

        if self.cb_C4.isChecked():
            try:
                im1 = (self.ds1[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im2 = (self.ds2[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im4 = (self.ds4[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im8 = (self.ds8[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im16 = (self.ds16[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im32 = (self.ds32[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
            except:
                try:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                except:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()

            self.layerC4.data = [im1, im2, im4, im8, im16, im32]
            
            # self.viewer.add_image([im1, im2, im4, im8, im16, im32], multiscale=True,
            #                           name='C4', blending='additive', colormap='bop blue', contrast_limits=self.default_contrast_limits)
        


    def Load2D(self, text):
        
        self.bLoad3D.setChecked(False)
        self.bLoad2D.setChecked(True)
        
        # Remove previous bounding box
        if any(i.name == 'bounding box' for i in self.viewer.layers):
            self.viewer.layers.remove('bounding box')

        # Remove previous volumes
        try:
            self.viewer.layers.remove('C1')
            del self.aligned_1
            self.aligned_1 = None
        except Exception:
            pass
        try:
            self.viewer.layers.remove('C2')
            del self.aligned_2
            self.aligned_2 = None
        except Exception:
            pass
        try:
            self.viewer.layers.remove('C3')
            del self.aligned_3
            self.aligned_3 = None
        except Exception:
            pass
        try:
            self.viewer.layers.remove('C4')
            del self.aligned_4
            self.aligned_4 = None
        except Exception:
            pass

        
        file_name = self.image_folder + str(self.comboBoxPath.currentText()) + '/mos'
        self.default_contrast_limits = [0,30000]
        self.thresholdN.setText("1000")
        self.channels_start = 0
        if not os.path.exists(file_name):
            file_name = self.image_folder + str(self.comboBoxPath.currentText()) + '/mos.zarr'
            self.default_contrast_limits = [0,30]
            self.thresholdN.setText("0.3")
            self.channels_start = 1
        print(file_name)
        
        self.ds1 = xr.open_zarr(file_name)
        self.ds2 = xr.open_zarr(file_name, group='l.2')
        self.ds4 = xr.open_zarr(file_name, group='l.4')
        self.ds8 = xr.open_zarr(file_name, group='l.8')
        self.ds16 = xr.open_zarr(file_name, group='l.16')
        self.ds32 = xr.open_zarr(file_name, group='l.32')

        # Get number of sections
        if self.axio:
            self.number_of_sections = len(list(self.ds1))
            self.optical_slices_available = 1
        else:
            if self.old_method:
                self.number_of_sections = len(set(self.ds1.attrs['cube_reg']['slice']))
            else:    
                self.number_of_sections = int(json.loads(self.ds1['S001'].attrs['raw_meta'])['sections'])
            
            self.optical_slices_available = len(self.ds1.z)
        
        print(f"Number of sections: {self.number_of_sections}")
        print(f"optical slices available: {self.optical_slices_available}")
        
        self.scroll.setRange(0, (self.optical_slices_available*self.number_of_sections)-1)
        optical_slice = 0
        self.scroll.setValue(0)
        z = 0

    
        if self.old_method:
            #Old method
            self.bscale = self.ds1.attrs['bscale']
            self.bzero = self.ds1.attrs['bzero']

            self.slice_names = self.ds1.attrs['cube_reg']['slice']

            self.scroll.setRange(0, len(self.slice_names)-1)
            if z >= len(self.slice_names):
                z = len(self.slice_names)-1
                self.scroll.setValue(z)

            slice_name = self.slice_names[z]
        else:
            try:
                self.bscale = self.ds1['S001'].attrs['bscale']
                self.bzero = self.ds1['S001'].attrs['bzero']
            except:
                self.bscale = 1
                self.bzero = 0
            slice_name = f"S{(z+1):03d}"
            
        print("slice_name: " + slice_name)

        if self.cb_C1.isChecked():
            try:
                im1 = (self.ds1[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im2 = (self.ds2[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im4 = (self.ds4[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im8 = (self.ds8[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im16 = (self.ds16[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im32 = (self.ds32[slice_name].sel(
                    channel=self.channels_start, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
            except:
                try:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                except:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start).data * self.bscale + self.bzero).squeeze()
                
            self.layerC1 = self.viewer.add_image([im1, im2, im4, im8, im16, im32], multiscale=True,
                                      name='C1', blending='additive', colormap='bop purple', contrast_limits=self.default_contrast_limits)

        if self.cb_C2.isChecked():
            try:
                im1 = (self.ds1[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im2 = (self.ds2[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im4 = (self.ds4[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im8 = (self.ds8[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im16 = (self.ds16[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im32 = (self.ds32[slice_name].sel(
                    channel=self.channels_start + 1, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
            except:
                try:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 1, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                except:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 1).data * self.bscale + self.bzero).squeeze()

            self.layerC2 = self.viewer.add_image([im1, im2, im4, im8, im16, im32], multiscale=True,
                                        name='C2', blending='additive', colormap='red', contrast_limits=self.default_contrast_limits)
                

        if self.cb_C3.isChecked():
            try:
                im1 = (self.ds1[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im2 = (self.ds2[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im4 = (self.ds4[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im8 = (self.ds8[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im16 = (self.ds16[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im32 = (self.ds32[slice_name].sel(
                    channel=self.channels_start + 2, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
            except:
                try:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 2, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                except:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 2).data * self.bscale + self.bzero).squeeze()

            self.layerC3 = self.viewer.add_image([im1, im2, im4, im8, im16, im32], multiscale=True,
                                      name='C3', blending='additive', colormap='green', contrast_limits=self.default_contrast_limits)

        if self.cb_C4.isChecked():
            try:
                im1 = (self.ds1[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im2 = (self.ds2[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im4 = (self.ds4[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im8 = (self.ds8[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im16 = (self.ds16[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
                im32 = (self.ds32[slice_name].sel(
                    channel=self.channels_start + 3, type='mosaic', z=optical_slice).data * self.bscale + self.bzero).squeeze()
            except:
                try:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 3, z=optical_slice).data * self.bscale + self.bzero).squeeze()
                except:
                    im1 = (self.ds1[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()
                    im2 = (self.ds2[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()
                    im4 = (self.ds4[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()
                    im8 = (self.ds8[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()
                    im16 = (self.ds16[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()
                    im32 = (self.ds32[slice_name].sel(
                        channel=self.channels_start + 3).data * self.bscale + self.bzero).squeeze()

            self.layerC4 = self.viewer.add_image([im1, im2, im4, im8, im16, im32], multiscale=True,
                                      name='C4', blending='additive', colormap='bop blue', contrast_limits=self.default_contrast_limits)
        
        self.loaded_2D = True
        self.loaded_3D = False


    def Load3D(self, text):

        self.origin_x = 0
        self.origin_y = 0

        self.crop = False
        self.loaded_2D = False
        self.loaded_3D = True
        
        self.bLoad3D.setChecked(True)
        self.bLoad2D.setChecked(False)
        
        self.Load(text)



    def Align(self, volume, resolution, output_resolution, start_slice_number):

        size_multiplier = (resolution*0.1*self.spacing[0])/output_resolution
        size = (volume.shape[0], int(size_multiplier*volume.shape[1]), int(size_multiplier*volume.shape[2]))
        aligned = np.zeros(size, dtype=np.float32)
        size2D = (int(size_multiplier*volume.shape[2]), int(size_multiplier*volume.shape[1]))

        z_size = volume.shape[0]
        for z in range(0, z_size):

            fixed = sitk.GetImageFromArray(volume[z, :, :])
            fixed.SetOrigin((0, 0))

            slice_name = self.slice_names[z+start_slice_number]

            current_spacing = (self.ds1[slice_name].attrs['scale'])
            fixed.SetSpacing([resolution*0.1*current_spacing[1],resolution*0.1*current_spacing[0]])

            transform = sitk.Euler2DTransform()

            align_pos = z + start_slice_number #*self.optical_slices
            alignY = 0
            if not np.isnan(self.corrected_align_y[align_pos]):
                alignY = -self.corrected_align_y[align_pos]*0.1*current_spacing[1]

            alignX = 0
            if not np.isnan(self.corrected_align_x[align_pos]):
                alignX = -self.corrected_align_x[align_pos]*0.1*current_spacing[0]

            transform.SetTranslation([alignY, alignX])

            resampler = sitk.ResampleImageFilter()

            resampler.SetSize(size2D)
            resampler.SetOutputSpacing([output_resolution, output_resolution])
            resampler.SetOutputOrigin((0, 0))
            resampler.SetInterpolator(sitk.sitkLinear)
            resampler.SetDefaultPixelValue(0)
            resampler.SetTransform(transform)

            out = resampler.Execute(fixed)

            np_out = sitk.GetArrayFromImage(out)
            aligned[z, :, :] = np_out

        return aligned.astype(dtype=np.float32)


    def AlignNew(self, volume, resolution, output_resolution, start_slice_number, current_spacing):
        print("------------------------------------------------------------------------")
        print(f"spacing({self.spacing[0]}, {self.spacing[1]})")
        size_multiplier = (resolution*0.1*self.spacing[0])/output_resolution
        size = (volume.shape[0], int(size_multiplier*volume.shape[1]), int(size_multiplier*volume.shape[2]))
        aligned = np.zeros(size, dtype=np.float32)
        size2D = (int(size_multiplier*volume.shape[2]), int(size_multiplier*volume.shape[1]))

        z_size = volume.shape[0]
        
        for z in range(0, z_size):

            fixed = sitk.GetImageFromArray(volume[z, :, :])
            fixed.SetOrigin((0, 0))


            slice_name = self.slice_names[z+start_slice_number]
            # if self.old_method:
            #     current_spacing = (self.ds1[slice_name].attrs['scale'])
            # else:
            #     current_spacing = [0,0,0]
            #     current_spacing[0] = 10 * float(json.loads(self.ds1[slice_name].attrs['scale'])["x"])
            #     current_spacing[1] = 10 * float(json.loads(self.ds1[slice_name].attrs['scale'])["y"])
            #     #current_spacing[2] = 10 * float(json.loads(self.ds1[slice_name].attrs['scale'])["z"])

            fixed.SetSpacing([resolution*0.1*current_spacing[1],resolution*0.1*current_spacing[0]])

            transform = sitk.Euler2DTransform()
            
            
            align_pos = z + start_slice_number
            alignY = 0
            if not np.isnan(self.corrected_align_y[align_pos]):
                alignY = -self.corrected_align_y[align_pos]*0.1*current_spacing[1]

            alignX = 0
            if not np.isnan(self.corrected_align_x[align_pos]):
                alignX = -self.corrected_align_x[align_pos]*0.1*current_spacing[0]

            transform.SetTranslation([alignY, alignX])


            resampler = sitk.ResampleImageFilter()
            resampler.SetSize(size2D)
            resampler.SetOutputSpacing([output_resolution, output_resolution])
            resampler.SetOutputOrigin((0, 0))
            resampler.SetInterpolator(sitk.sitkLinear)
            resampler.SetDefaultPixelValue(0)
            resampler.SetTransform(transform)

            out = resampler.Execute(fixed)

            np_out = sitk.GetArrayFromImage(out)
            aligned[z, :, :] = np_out

        return aligned.astype(dtype=np.float32)


    def Remove_Regions(self, use_size):

        # output_resolution = float(self.pixel_size.text())
        threshold = float(self.thresholdN.text())

        if self.aligned_1 is not None and self.cb_C1.isChecked() and any(i.name == 'C1' for i in self.viewer.layers):

            threholded = self.aligned_1 > threshold
            threholded = ndimage.binary_fill_holes(threholded)
            threholded = threholded.astype(np.uint8)

            keep_n = self.spinN.value()

            for z in range(0, threholded.shape[0]):
                print('{}/{}'.format(z+1, threholded.shape[0]))

                threholded_z = threholded[z, :, :]
                volume_z = self.aligned_1[z, :, :]
                
                nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
                    threholded_z, connectivity=4)
                
                sizes = stats[:, -1]
                sizes_sorted = np.sort(sizes, axis=0)

                if use_size:
                    max_size = float(self.maxSizeN.text())
                else:
                    max_size = sizes_sorted[len(sizes_sorted)-1-keep_n]
                for i in range(1, nb_components):
                    if sizes[i] < max_size:
                        volume_z[output == i] = threshold

                self.aligned_1[z, :, :] = volume_z

            self.viewer.layers['C1'].visible = False
            self.viewer.layers['C1'].visible = True

        if self.aligned_2 is not None and self.cb_C2.isChecked() and any(i.name == 'C2' for i in self.viewer.layers):

            threholded = self.aligned_2 > threshold
            threholded = ndimage.binary_fill_holes(threholded)
            threholded = threholded.astype(np.uint8)

            keep_n = self.spinN.value()

            for z in range(0, threholded.shape[0]):
                print('{}/{}'.format(z+1, threholded.shape[0]))

                threholded_z = threholded[z, :, :]
                volume_z = self.aligned_2[z, :, :]

                nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
                    threholded_z, connectivity=4)
                sizes = stats[:, -1]
                sizes_sorted = np.sort(sizes, axis=0)

                if use_size:
                    max_size = float(self.maxSizeN.text())
                else:
                    max_size = sizes_sorted[len(sizes_sorted)-1-keep_n]
                for i in range(1, nb_components):
                    if sizes[i] < max_size:
                        volume_z[output == i] = threshold

                self.aligned_2[z, :, :] = volume_z

            self.viewer.layers['C2'].visible = False
            self.viewer.layers['C2'].visible = True

        if self.aligned_3 is not None and self.cb_C3.isChecked() and any(i.name == 'C3' for i in self.viewer.layers):
            
            threholded = self.aligned_3 > threshold
            threholded = ndimage.binary_fill_holes(threholded)
            threholded = threholded.astype(np.uint8)

            keep_n = self.spinN.value()

            for z in range(0, threholded.shape[0]):
                print('{}/{}'.format(z+1, threholded.shape[0]))

                threholded_z = threholded[z, :, :]
                volume_z = self.aligned_3[z, :, :]
                
                nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
                    threholded_z, connectivity=4)
                
                sizes = stats[:, -1]
                sizes_sorted = np.sort(sizes, axis=0)
                
                if use_size:
                    max_size = float(self.maxSizeN.text())
                else:
                    max_size = sizes_sorted[len(sizes_sorted)-1-keep_n]
                for i in range(1, nb_components):
                    if sizes[i] < max_size:
                        volume_z[output == i] = threshold
                
                self.aligned_3[z, :, :] = volume_z

            self.viewer.layers['C3'].visible = False
            self.viewer.layers['C3'].visible = True

        if self.aligned_4 is not None and self.cb_C4.isChecked() and any(i.name == 'C4' for i in self.viewer.layers):

            threholded = self.aligned_4 > threshold
            threholded = ndimage.binary_fill_holes(threholded)
            threholded = threholded.astype(np.uint8)

            keep_n = self.spinN.value()

            for z in range(0, threholded.shape[0]):
                print('{}/{}'.format(z+1, threholded.shape[0]))

                threholded_z = threholded[z, :, :]
                volume_z = self.aligned_4[z, :, :]

                nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
                    threholded_z, connectivity=4)
                sizes = stats[:, -1]
                sizes_sorted = np.sort(sizes, axis=0)

                if use_size:
                    max_size = float(self.maxSizeN.text())
                else:
                    max_size = sizes_sorted[len(sizes_sorted)-1-keep_n]
                for i in range(1, nb_components):
                    if sizes[i] < max_size:
                        volume_z[output == i] = threshold

                self.aligned_4[z, :, :] = volume_z

            self.viewer.layers['C4'].visible = False
            self.viewer.layers['C4'].visible = True


    def Remove_Small_Regions(self):
        self.Remove_Regions(True)

    def Keep_n_Regions(self):
        self.Remove_Regions(False)
    
    def add_polygon_simple(self):

        pos = int(self.viewer.cursor.position[0]/15)

        data_length = len(self.viewer.layers['Shapes'].data[0])
        print(data_length)

        new_shape = []
        for i in range(0, data_length):
            
            x = pos
            y = self.viewer.layers['Shapes'].data[0][i][1]
            z = self.viewer.layers['Shapes'].data[0][i][2]
            new_shape.append((x,y,z))

        new_shape = np.array(new_shape)
        
        shapes_layer = self.viewer.add_shapes(new_shape, shape_type='polygon', name = "Shapes", scale=(15, 15, 15),)
    
    def add_polygon(self):
        self.viewer.window.qt_viewer.update()

        output_resolution = float(self.pixel_size.text())
        
        pos = self.viewer.dims.point[0] / ((float(self.slice_spacing)/float(self.optical_slices)) / output_resolution)
        print("pos {}".format(pos))
        
        data_length = len(self.viewer.layers['Shapes'].data[0])
        print("data_length {}".format(data_length))

        contour_list = []
        z_pos = self.viewer.layers["Shapes"].data[0][0][0] # z pos
        contour = self.viewer.layers["Shapes"].data[0]
        contour_list.append([z_pos,contour])

        i = 1
        while True:
            layer_name = "Shapes [{}]".format(i)
            try:
                z_pos = self.viewer.layers[layer_name].data[0][0][0] # z pos
                contour = self.viewer.layers[layer_name].data[0]
                contour_list.append((z_pos,contour))
                i = i+1
            except:
                break

        contour_list_sorted = sorted(contour_list, key=lambda tup: tup[0])

        new_shape = []

        if pos < contour_list_sorted[0][0]:
            for i in range(0, data_length):
                x = pos
                y = float(contour_list_sorted[0][1][i][1])
                z = float(contour_list_sorted[0][1][i][2])

                print(f"x {x}, y {y}, z {z}")

                new_shape.append((x,y,z))

        elif pos > contour_list_sorted[len(contour_list_sorted)-1][0]:
            for i in range(0, data_length):
                x = pos
                y = float(contour_list_sorted[len(contour_list_sorted)-1][1][i][1])
                z = float(contour_list_sorted[len(contour_list_sorted)-1][1][i][2])

                print(f"x {x}, y {y}, z {z}")

                new_shape.append((x,y,z))
            
        else:
            z_i = 0
            for i in range(0,len(contour_list_sorted)-1):
                z_level_start = contour_list_sorted[i][0]
                z_level_end = contour_list_sorted[i+1][0]
                if pos >= z_level_start and pos <= z_level_end:
                    z_i = i

            for i in range(0, data_length):
                x1 = float(contour_list_sorted[z_i][1][i][0])
                y1 = float(contour_list_sorted[z_i][1][i][1])
                z1 = float(contour_list_sorted[z_i][1][i][2])

                x2 = float(contour_list_sorted[z_i+1][1][i][0])
                y2 = float(contour_list_sorted[z_i+1][1][i][1])
                z2 = float(contour_list_sorted[z_i+1][1][i][2])

                weight2 = (pos - x1) / (x2 - x1)
                weight = 1 - weight2

                x = pos
                y = (weight * y1) + (weight2 * y2)
                z = (weight * z1) + (weight2 * z2)
                new_shape.append((x,y,z))


        new_shape = np.array(new_shape)
        output_resolution = float(self.pixel_size.text())
        shapes_layer = self.viewer.add_shapes(new_shape, shape_type='polygon', name = "Shapes", scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1),)

    def run_remove_outside(self):

        if self.aligned_1 is not None:
            aligned1_tmp = np.copy(self.aligned_1)
        if self.aligned_2 is not None:
            aligned2_tmp = np.copy(self.aligned_2)
        if self.aligned_3 is not None:
            aligned3_tmp = np.copy(self.aligned_3)
        if self.aligned_4 is not None:
            aligned4_tmp = np.copy(self.aligned_4)

        contour_list = []
        z_pos = self.viewer.layers["Shapes"].data[0][0][0] # z pos
        contour = self.viewer.layers["Shapes"].data[0]
        contour_list.append([z_pos,contour])


        i = 1
        while True:
            layer_name = "Shapes [{}]".format(i)
            try:
                z_pos = self.viewer.layers[layer_name].data[0][0][0] # z pos
                contour = self.viewer.layers[layer_name].data[0]
                contour_list.append((z_pos,contour))
                self.viewer.layers[layer_name].visible = False
                i = i+1
            except:
                break
        contour_list_sorted = sorted(contour_list, key=lambda tup: tup[0])
        

        output_resolution = float(self.pixel_size.text())
        data_length = len(self.viewer.layers['Shapes'].data[0])
        print("data_length {}".format(data_length))

        c = 0
        width = 0
        height = 0
        if self.aligned_1 is not None:
            c, width, height = self.aligned_1.shape
        if self.aligned_2 is not None:
            c, width, height = self.aligned_2.shape
        if self.aligned_3 is not None:
            c, width, height = self.aligned_3.shape
        if self.aligned_4 is not None:
            c, width, height = self.aligned_4.shape

        for z_level in range(0,c):

            z_i = -1
            for i in range(0,len(contour_list_sorted)-1):
                z_level_start = contour_list_sorted[i][0]
                z_level_end = contour_list_sorted[i+1][0]
                if z_level >= z_level_start and z_level <= z_level_end:
                    z_i = i

            if z_i == -1:
                mask = np.zeros((width, height), dtype=int)
            else:
                polygon_values = []
                for i in range(0, data_length):
                    x1 = float(contour_list_sorted[z_i][1][i][0])
                    y1 = float(contour_list_sorted[z_i][1][i][1])
                    z1 = float(contour_list_sorted[z_i][1][i][2])

                    x2 = float(contour_list_sorted[z_i+1][1][i][0])
                    y2 = float(contour_list_sorted[z_i+1][1][i][1])
                    z2 = float(contour_list_sorted[z_i+1][1][i][2])

                    weight2 = (z_level - x1) / (x2 - x1)
                    weight = 1 - weight2

                    y = (weight * y1) + (weight2 * y2)# + (self.image_translation[0]/15)
                    z = (weight * z1) + (weight2 * z2)#  + (self.image_translation[1]/15)
                    polygon_values.append((y, z))


                img = Image.new('L', (width, height), 0)
                ImageDraw.Draw(img).polygon(polygon_values, outline=1, fill=1)

                mask = np.array(img)
                mask = np.transpose(mask, (1,0))
            
            if self.aligned_1 is not None:
                aligned1_tmp[z_level,:,:] = aligned1_tmp[z_level,:,:] * mask
            if self.aligned_2 is not None:
                aligned2_tmp[z_level,:,:] = aligned2_tmp[z_level,:,:] * mask
            if self.aligned_3 is not None:
                aligned3_tmp[z_level,:,:] = aligned3_tmp[z_level,:,:] * mask
            if self.aligned_4 is not None:
                aligned4_tmp[z_level,:,:] = aligned4_tmp[z_level,:,:] * mask

        
           

        if self.aligned_1 is not None:
            self.viewer.add_image([aligned1_tmp], name='C1_masked', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='bop purple', contrast_limits=self.default_contrast_limits)
            self.viewer.layers['C1'].visible = False
        if self.aligned_2 is not None:
            self.viewer.add_image([aligned2_tmp], name='C2_masked', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='red', contrast_limits=self.default_contrast_limits)
            self.viewer.layers['C2'].visible = False
        if self.aligned_3 is not None:
            self.viewer.add_image([aligned3_tmp], name='C3_masked', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='green', contrast_limits=self.default_contrast_limits)
            self.viewer.layers['C3'].visible = False
        if self.aligned_4 is not None:
            self.viewer.add_image([aligned4_tmp], name='C4_masked', scale=(float(self.slice_spacing)/float(self.optical_slices) / output_resolution, 1, 1), 
                                  blending='additive', colormap='bop blue', contrast_limits=self.default_contrast_limits)
            self.viewer.layers['C4'].visible = False

        self.viewer.layers['Shapes'].visible = False



    def on_combobox_changed(self):
        
        for folder in self.image_folders:
    
            if folder == '/data/meds1_c/storage/processed0/stpt/':
                self.old_method = True
            else:
                self.old_method = False
                
            file_name = folder + str(self.comboBoxPath.currentText()) + '/mos'
            if os.path.exists(file_name):
                self.image_folder = folder
                break
            file_name = folder + str(self.comboBoxPath.currentText()) + '/mos.zarr'
            if os.path.exists(file_name):
                self.image_folder = folder
                break
                     
        print(f"folder location: " + self.image_folder)
            
            

        file_name = self.image_folder + str(self.comboBoxPath.currentText()) + '/mos'
        self.default_contrast_limits = [0,30000]
        self.thresholdN.setText("1000")
        self.channels_start = 0
        if not os.path.exists(file_name):
            file_name = self.image_folder + str(self.comboBoxPath.currentText()) + '/mos.zarr'
            self.default_contrast_limits = [0,30]
            self.thresholdN.setText("0.3")
            self.channels_start = 1
        print(file_name)
        
        
        if os.path.exists(file_name + '/.zmetadata'):
            print("metadata is available")
            
            try:
                ds = xr.open_zarr(file_name, consolidated=True)
                print("")
                print("")
                print(ds.attrs['sections'])
                print("")
                print("")
                length = int(ds.attrs['sections'])

                self.scroll.setValue(0)
                self.image_slice.setText("0")
                self.slice_names = ds.attrs['cube_reg']['slice']
                self.scroll.setRange(0, len(self.slice_names))
                print(f"number of slices: {len(self.slice_names)}")
            except Exception:
                print("none-consolidated")
                pass
        else:
            print("not changing number of slices")


    def SaveVolume(self):
        widget = QtWidgets.QWidget()
        if sys.platform == 'linux':
            fname, _ = QtWidgets.QFileDialog.getSaveFileName(
                widget, 'Save file as', '/home/', "Image files (*.tiff *.mha *.nii)")
        else:
            fname, _ = QtWidgets.QFileDialog.getSaveFileName(
                widget, 'Save file as', 'c:\\', "Image files (*.tiff *.mha *.nii)")

        if fname != "":
            print(fname)

            file_name = fname#"/home/tristan/test.tiff"

            output_resolution = float(self.pixel_size.text())
            output_resolution_z = float(self.slice_spacing)/float(self.optical_slices)
            spacing = (output_resolution, output_resolution, output_resolution_z)

            volume = []

            if self.cb_C1.isChecked():
                volume.append(self.aligned_1)
                pass
            if self.cb_C2.isChecked():
                volume.append(self.aligned_2)
                pass
            if self.cb_C3.isChecked():
                volume.append(self.aligned_3)
                pass
            if self.cb_C4.isChecked():
                volume.append(self.aligned_4)
                pass

            name, extension = os.path.splitext(file_name)
            if extension == "mha" or extension == "nii" :
                volume = np.array(volume)
                # print(f"volume {volume.shape}")
                volume = np.moveaxis(volume,0,3)
                # print(f"volume {volume.shape}")

                volume_itk = sitk.GetImageFromArray(volume)
                volume_itk.SetSpacing(spacing)
                caster = sitk.CastImageFilter()
                caster.SetOutputPixelType(sitk.sitkVectorFloat32)
                volume_itk = caster.Execute(volume_itk)
                
                #sitk.WriteImage(volume_itk, file_name, useCompression=True)
                
                writer = sitk.ImageFileWriter()
                writer.SetFileName(file_name)
                writer.UseCompressionOff()
                #writer.SetCompressionLevel(0)
                writer.Execute(volume_itk)
        
            else:

                volume = np.array(volume)
                print(f"volume {volume.shape}")
                volume = np.moveaxis(volume,0,1)
                print(f"volume {volume.shape}")
                print(volume.shape)
                # tifffile.imsave(file_name, volume.astype('float32'))
                # tifffile.imwrite(file_name, volume.astype('float32'), compress=9, imagej=True, metadata={'spacing': output_resolution_z, 'unit': 'um', 'axes': 'ZCYX'})
                # tifffile.imwrite(file_name, volume.astype('float32'), compression="zlib", imagej=True, metadata={'spacing': output_resolution_z, 'unit': 'um', 'axes': 'ZCYX'})
                tifffile.imwrite(file_name, volume.astype('float32'), compression="zlib", compressionargs={'level':5}, imagej=True, metadata={'spacing': output_resolution_z, 'unit': 'um', 'axes': 'ZCYX'})

            
    def LoadVolume(self):
        widget = QtWidgets.QWidget()
        if sys.platform == 'linux':
            fname, _ = QtWidgets.QFileDialog.getOpenFileName(
                widget, 'Load file', '/home/', "Image files (*.tiff *.mha *.nii)")
        else:
            fname, _ = QtWidgets.QFileDialog.getOpenFileName(
                widget, 'Load file', 'c:\\', "Image files (*.tiff *.mha *.nii)")

        if fname != "":
            print(fname)

            file_name = fname
            
            reader = sitk.ImageFileReader()
            reader.SetFileName(file_name)
            image = reader.Execute()
            
            print(image.GetSpacing())
            np_image = sitk.GetArrayFromImage(image)
            
            self.viewer.add_image([np_image], name='Volume', scale=(float(image.GetSpacing()[2]), float(image.GetSpacing()[1]), float(image.GetSpacing()[0])), 
                      blending='additive', colormap='gray', contrast_limits=self.default_contrast_limits)
    
    def LoadMask(self):
        widget = QtWidgets.QWidget()
        if sys.platform == 'linux':
            fname, _ = QtWidgets.QFileDialog.getOpenFileName(
                widget, 'Load file', '/home/', "Image files (*.tiff *.mha *.nii)")
        else:
            fname, _ = QtWidgets.QFileDialog.getOpenFileName(
                widget, 'Load file', 'c:\\', "Image files (*.tiff *.mha *.nii)")

        if fname != "":
            print(fname)

            file_name = fname
            
            reader = sitk.ImageFileReader()
            reader.SetFileName(file_name)
            image = reader.Execute()
            
            print(image.GetSpacing())
            np_image = sitk.GetArrayFromImage(image)
            np_image = np_image.astype(np.uint8)
            
            self.viewer.add_labels([np_image], name='Mask', scale=(float(image.GetSpacing()[2]), float(image.GetSpacing()[1]), float(image.GetSpacing()[0])))

            
    def SaveSlice(self):
        widget = QtWidgets.QWidget()
        if sys.platform == 'linux':
            fname, _ = QtWidgets.QFileDialog.getSaveFileName(
                widget, 'Save file as', '/home/', "Image files (*.tiff)")
        else:
            fname, _ = QtWidgets.QFileDialog.getSaveFileName(
                widget, 'Save file as', 'c:\\', "Image files (*.tiff)")

        if fname != "":
            print(fname)

            file_name = fname#"/home/tristan/test.tiff"

            output_resolution = float(self.pixel_size.text())
            spacing = (output_resolution, output_resolution, 1)

            volume = []
            z = self.scroll.value()

            if self.cb_C1.isChecked():
                volume.append(self.aligned_1[z,:,:])
                pass
            if self.cb_C2.isChecked():
                volume.append(self.aligned_2[z,:,:])
                pass
            if self.cb_C3.isChecked():
                volume.append(self.aligned_3[z,:,:])
                pass
            if self.cb_C4.isChecked():
                volume.append(self.aligned_4[z,:,:])
                pass

            
            volume = np.array(volume)
            
            if False:
                volume = np.expand_dims(volume, axis=1)
                volume = np.moveaxis(volume,0,3)

                volume_itk = sitk.GetImageFromArray(volume)
                volume_itk.SetSpacing(spacing)
                caster = sitk.CastImageFilter()
                caster.SetOutputPixelType(sitk.sitkVectorFloat32)
                volume_itk = caster.Execute(volume_itk)
                sitk.WriteImage(volume_itk, file_name)  
            
            # volume = np.moveaxis(volume,0,2)
            # print(volume.shape)
            tifffile.imsave(file_name, volume)
            
            
    def SaveSliceOld(self):
        widget = QtWidgets.QWidget()
        if sys.platform == 'linux':
            fname, _ = QtWidgets.QFileDialog.getSaveFileName(
                widget, 'Save file as', '/home/', "Image files (*.tiff *.mha)")
        else:
            fname, _ = QtWidgets.QFileDialog.getSaveFileName(
                widget, 'Save file as', 'c:\\', "Image files (*.tiff *.mha)")

        if fname != "":
            print(fname)

            self.bscale = self.ds1.attrs['bscale']
            self.bzero = self.ds1.attrs['bzero']

            z = self.scroll.value()

            self.slice_names = self.ds1.attrs['cube_reg']['slice']

            self.scroll.setRange(0, len(self.slice_names)-1)
            if z >= len(self.slice_names):
                z = len(self.slice_names)-1
                self.scroll.setValue(z)

            slice_name = self.slice_names[z]


            output_resolution = float(self.pixel_size.text())
            spacing = (output_resolution, output_resolution)

            
            file_name = self.image_folder + str(self.comboBoxPath.currentText()) + '/mos'
            self.default_contrast_limits = [0,30000]
            self.thresholdN.setText("1000")
            self.channels_start = 0
            if not os.path.exists(file_name):
                file_name = self.image_folder + str(self.comboBoxPath.currentText()) + '/mos.zarr'
                self.default_contrast_limits = [0,30]
                self.thresholdN.setText("0.3")
                self.channels_start = 1
            print(file_name)
                
            ds32 = xr.open_zarr(file_name, group='l.32')
            im32 = (ds32[slice_name].sel(
                channel=self.channels_start + 2, type='mosaic', z=0).data * self.bscale + self.bzero).astype(dtype=np.float32)

            image_itk = sitk.GetImageFromArray(im32)
            image_itk.SetSpacing(spacing)
            caster = sitk.CastImageFilter()
            caster.SetOutputPixelType(sitk.sitkVectorFloat32)
            image_itk = caster.Execute(image_itk)
            sitk.WriteImage(image_itk, fname[0])

    def Normalize_slices(self, volume, optical_sections):
        import statistics
        print("Normalize optical sections")

        slices, size_x, size_y = volume.shape
        for i in range(1,slices):
            if i%optical_sections != 0:
                values_x = []
                values_y = []
                for j in range(10000):
                    rand_x = random.randint(1,size_x-1)
                    rand_y = random.randint(1,size_y-1)
                    if(volume[i-1,rand_x,rand_y] > 0 and volume[i,rand_x,rand_y] > 0):
                        x = volume[i,rand_x,rand_y]
                        y = volume[i-1,rand_x,rand_y]
                        values_x.append(x)
                        values_y.append(y)

                if len(values_x) > 3:
                    slope, intercept, r, p, std_err = stats.linregress(values_x, values_y)
                    volume[i,:,:] = volume[i,:,:] * slope + intercept

        return


    def Normalize(self):

        output_resolution = float(self.pixel_size.text())
        norm_value = float(self.normalize_value.text())

        if self.cb_C1.isChecked():
            self.aligned_1[0::10,:,:] = self.aligned_1[0::10,:,:] * norm_value
            self.aligned_1[1::10,:,:] = self.aligned_1[1::10,:,:] * norm_value
            self.aligned_1[2::10,:,:] = self.aligned_1[2::10,:,:] * norm_value
            self.aligned_1[3::10,:,:] = self.aligned_1[3::10,:,:] * norm_value
            self.aligned_1[4::10,:,:] = self.aligned_1[4::10,:,:] * norm_value

            self.viewer.layers.remove('C1')
            self.viewer.add_image([self.aligned_1], name='C1', scale=(float(self.slice_spacing)/float(self.optical_slices), output_resolution, output_resolution), 
                                  blending='additive', colormap='bop purple', contrast_limits=self.default_contrast_limits)


        if self.cb_C2.isChecked():  
            self.aligned_2[0::10,:,:] = self.aligned_2[0::10,:,:] * norm_value
            self.aligned_2[1::10,:,:] = self.aligned_2[1::10,:,:] * norm_value
            self.aligned_2[2::10,:,:] = self.aligned_2[2::10,:,:] * norm_value
            self.aligned_2[3::10,:,:] = self.aligned_2[3::10,:,:] * norm_value
            self.aligned_2[4::10,:,:] = self.aligned_2[4::10,:,:] * norm_value

            # with napari.gui_qt():
            self.viewer.layers.remove('C2')
            self.viewer.add_image([self.aligned_2], name='C2', scale=(float(self.slice_spacing)/float(self.optical_slices), output_resolution, output_resolution), 
                                  blending='additive', colormap='red', contrast_limits=self.default_contrast_limits)

        if self.cb_C3.isChecked():

            slices, size_x, size_y = self.aligned_3.shape
            for i in range(1,slices):
                if i%2 != 0:
                    values_x = []
                    values_y = []
                    for j in range(1000):
                        rand_x = random.randint(1,size_x-1)
                        rand_y = random.randint(1,size_y-1)
                        if(self.aligned_3[i-1,rand_x,rand_y] > 0.0 and self.aligned_3[i,rand_x,rand_y] > 0.0):
                            x = self.aligned_3[i,rand_x,rand_y]
                            y = self.aligned_3[i-1,rand_x,rand_y]
                            values_x.append(x)
                            values_y.append(y)

                    slope, intercept, r, p, std_err = stats.linregress(values_x, values_y)

                    print(slope)

                    self.aligned_3[i,:,:] = self.aligned_3[i,:,:] * slope + intercept

            self.viewer.layers.remove('C3')
            self.viewer.add_image([self.aligned_3], name='C3', scale=(float(self.slice_spacing)/float(self.optical_slices), output_resolution, output_resolution), 
                                  blending='additive', colormap='green', contrast_limits=self.default_contrast_limits)

        if self.cb_C4.isChecked():
            self.aligned_4[0::10,:,:] = self.aligned_4[0::10,:,:] * norm_value
            self.aligned_4[1::10,:,:] = self.aligned_4[1::10,:,:] * norm_value
            self.aligned_4[2::10,:,:] = self.aligned_4[2::10,:,:] * norm_value
            self.aligned_4[3::10,:,:] = self.aligned_4[3::10,:,:] * norm_value
            self.aligned_4[4::10,:,:] = self.aligned_4[4::10,:,:] * norm_value

            self.viewer.layers.remove('C4')
            self.viewer.add_image([self.aligned_4], name='C4', scale=(float(self.slice_spacing)/float(self.optical_slices), output_resolution, output_resolution), 
                                  blending='additive', colormap='bop blue', contrast_limits=self.default_contrast_limits)

    
    def SelectFolderOld(self):
        file = str(QtWidgets.QFileDialog.getExistingDirectory())
        file = file + '/'

        self.search_folder.setText(file)
        self.comboBoxPath.clear()
        for f in os.scandir(self.search_folder.text()):
            if f.is_dir():
                if os.path.exists(f.path + "/mos.zarr"):
                    s = f.path
                    s = s.replace(self.search_folder.text(), '')
                    print(s)
                    self.comboBoxPath.addItem(s)
                elif os.path.exists(f.path + "/mos"):
                    s = f.path
                    s = s.replace(self.search_folder.text(), '')
                    print(s)
                    self.comboBoxPath.addItem(s)
    
    def SelectFolder(self):
        self.old_method = False
        file_list = []
        
        file = str(QtWidgets.QFileDialog.getExistingDirectory())
        file = file + '/'
        self.image_folder = file
        self.search_folder = QtWidgets.QLineEdit(file)
        if os.path.exists(self.search_folder.text()):
            for f in os.scandir(self.search_folder.text()):
                if f.is_dir():
                    if os.path.exists(f.path + "/mos.zarr"):
                        s = f.path
                        s = s.replace(self.search_folder.text(), '')
                        file_list.append(s)
                    elif os.path.exists(f.path + "/mos"):
                        s = f.path
                        s = s.replace(self.search_folder.text(), '')
                        file_list.append(s)
                            
            print(file_list)

            file_list.sort()

            self.comboBoxPath.clear()
            for i in file_list:
                self.comboBoxPath.addItem(i)
        
    def MethodChanged(self):

        if self.cb_R_Axio.isChecked():
            self.old_method = False
            self.axio = True
            self.image_folders = {
                '/storage/imaxt.processed.2022/axio/',
                '/storage/processed.2022/axio/',
            }
            print("setting axio method")
        else:
            self.old_method = False
            self.axio = False
            self.image_folders = {
                '/storage/processed.2022/stpt/',
                '/storage/processed/stpt/',
                '/storage/imaxt.processed.2022/stpt/',
                '/data/meds1_c/storage/processed0/stpt/',
                '/storage/tristan/imaxt_zarr/'
            }
            print("setting STPT method")

        file_list = []
        for folder in self.image_folders:
            print(sys.platform)
            if sys.platform == 'linux':
                self.search_folder = QtWidgets.QLineEdit(folder)
                if os.path.exists(self.search_folder.text()):
                    for f in os.scandir(self.search_folder.text()):
                        if f.is_dir():
                            if os.path.exists(f.path + "/mos.zarr"):
                                s = f.path
                                s = s.replace(self.search_folder.text(), '')
                                file_list.append(s)
                            elif os.path.exists(f.path + "/mos"):
                                s = f.path
                                s = s.replace(self.search_folder.text(), '')
                                file_list.append(s)
                                
        else:
            self.search_folder = QtWidgets.QLineEdit('N:/stpt/')
        
        print(file_list)

        file_list.sort()

        self.comboBoxPath.clear()
        for i in file_list:
            self.comboBoxPath.addItem(i)

    def SetPerspective(self):
        if(self.cb_perspective.isChecked()):
            self.viewer.window.qt_viewer.camera._3D_camera.fov = 45
        else:
            self.viewer.window.qt_viewer.camera._3D_camera.fov = 0
            
    def MergeLayers(self):
        f1 = float(self.m_volume_1_multiplier.text())
        f2 = float(self.m_volume_2_multiplier.text())
        C1 = self.viewer.layers[self.m_volume_1.text()].data
        C2 = self.viewer.layers[self.m_volume_2.text()].data
        C_new = (f1*C1)+(f2*C2)
        self.viewer.add_image(C_new, name=self.m_volume_new.text(), scale=self.viewer.layers[self.m_volume_1.text()].scale, blending='additive', colormap='gray')
        


    def SetShapeText(self):
        print(self.viewer.layers.selection)
        
        shapes = self.viewer.add_points(properties={'box_label': "test"})
        
        shapes.text = 'box_label'
        shapes.text.color = 'white'
        shapes.text.size = 30
        shapes.anchor = 'center'
        shapes.face_color = "transparent"
        shapes.edge_color = "transparent"
        shapes.current_face_color = "transparent"
        shapes.current_edge_color = "transparent"
        shapes.edge_width = 0
        shapes.current_edge_width = 0
        shapes.out_of_slice_display = True

        def on_data(event):
            shapes.text = 'box_label'
            shapes.text.color = 'white'
            shapes.text.size = 30
            shapes.anchor = 'center'
            shapes.face_color = "transparent"
            shapes.edge_color = "transparent"
            shapes.current_face_color = "transparent"
            shapes.current_edge_color = "transparent"
            shapes.edge_width = 0
            shapes.current_edge_width = 0
            shapes.out_of_slice_display = True
            
        shapes.events.set_data.connect(on_data)
        

        
    def main(self):

        self.viewer = napari.Viewer()
        self.viewer.theme = 'dark' 

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        vbox = QtWidgets.QVBoxLayout()

        cb_group1 = QtWidgets.QButtonGroup()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        self.cb_R_Axio = QtWidgets.QRadioButton('AXIO')
        self.cb_R_Axio.setChecked(False)
        self.cb_R_Axio.toggled.connect(self.MethodChanged)
        hbox.addWidget(self.cb_R_Axio)
        # self.cb_R_Old = QtWidgets.QRadioButton('STPT Old')
        # self.cb_R_Old.setChecked(False)
        # self.cb_R_Old.toggled.connect(self.MethodChanged)
        # hbox.addWidget(self.cb_R_Old)
        self.cb_R_New = QtWidgets.QRadioButton('STPT')
        self.cb_R_New.setChecked(True)
        self.cb_R_New.toggled.connect(self.MethodChanged)
        hbox.addWidget(self.cb_R_New)
        cb_group1.addButton(self.cb_R_Axio)
        # cb_group1.addButton(self.cb_R_Old)
        cb_group1.addButton(self.cb_R_New)
        
        bSelectFolder = QtWidgets.QPushButton('Select folder')
        bSelectFolder.clicked.connect(self.SelectFolder)
        hbox.addWidget(bSelectFolder)
        
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        
        
        
        hbox = QtWidgets.QHBoxLayout()
        self.comboBoxPath = ExtendedComboBox()

        self.image_folders = {
            '/storage/processed.2022/stpt/',
            '/storage/processed/stpt/',
            '/storage/imaxt.processed.2022/stpt/',
            '/data/meds1_c/storage/processed0/stpt/',
            '/storage/tristan/imaxt_zarr/'
        }
        file_list = []
        for folder in self.image_folders:
            self.search_folder = QtWidgets.QLineEdit(folder)
            if os.path.exists(self.search_folder.text()):
                for f in os.scandir(self.search_folder.text()):
                    if f.is_dir():
                        if os.path.exists(f.path + "/mos.zarr"):
                            s = f.path
                            s = s.replace(self.search_folder.text(), '')
                            file_list.append(s)
                        elif os.path.exists(f.path + "/mos"):
                            s = f.path
                            s = s.replace(self.search_folder.text(), '')
                            file_list.append(s)

        
        file_list.sort()
        
        self.axio = False

        self.comboBoxPath.clear()
        for i in file_list:
            self.comboBoxPath.addItem(i)

        self.comboBoxPath.setMinimumWidth(300)
        self.comboBoxPath.currentIndexChanged.connect(
            self.on_combobox_changed)
        hbox.addWidget(self.comboBoxPath)
        # hbox.addStretch(1)
        self.comboBoxPath.setMaximumWidth(300)
        # self.comboBoxPath.adjustSize()
        #self.comboBoxPath.setFixedSize(500, 20)
        vbox.addLayout(hbox)
        
        layout.addLayout(vbox)
        
        vbox = QtWidgets.QVBoxLayout()

        hbox = QtWidgets.QHBoxLayout()

        hbox.addWidget(QtWidgets.QLabel("Slice spacing:"))
        self.m_slice_spacing = QtWidgets.QLineEdit("15")
        self.m_slice_spacing.setMaximumWidth(50)
        hbox.addWidget(self.m_slice_spacing)

        hbox.addWidget(QtWidgets.QLabel("Output pixel size:"))
        self.pixel_size = QtWidgets.QLineEdit("15")
        self.pixel_size.setMaximumWidth(50)
        hbox.addWidget(self.pixel_size)
        hbox.addStretch(1)
        vbox.addLayout(hbox)


        hbox = QtWidgets.QHBoxLayout()
        self.cb_correct_brightness_optical_section = QtWidgets.QCheckBox('Normalize brightness optical sections')
        self.cb_correct_brightness_optical_section.setChecked(True)
        hbox.addWidget(self.cb_correct_brightness_optical_section)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Slices range:"))
        self.start_slice = QtWidgets.QLineEdit("")
        self.start_slice.setMaximumWidth(50)
        hbox.addWidget(self.start_slice)
        hbox.addWidget(QtWidgets.QLabel("to"))
        self.end_slice = QtWidgets.QLineEdit("")
        self.end_slice.setMaximumWidth(50)
        hbox.addWidget(self.end_slice)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Load channels:"))
        self.cb_C1 = QtWidgets.QCheckBox('1')
        self.cb_C1.setChecked(True)
        hbox.addWidget(self.cb_C1)
        self.cb_C2 = QtWidgets.QCheckBox('2')
        self.cb_C2.setChecked(True)
        hbox.addWidget(self.cb_C2)
        self.cb_C3 = QtWidgets.QCheckBox('3')
        self.cb_C3.setChecked(True)
        hbox.addWidget(self.cb_C3)
        self.cb_C4 = QtWidgets.QCheckBox('4')
        self.cb_C4.setChecked(True)
        hbox.addWidget(self.cb_C4)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        self.bLoad3D = QtWidgets.QPushButton('Load volume')
        self.bLoad3D.setCheckable(True)
        self.bLoad3D.clicked.connect(self.Load3D)
        hbox.addWidget(self.bLoad3D)

        bReload3D = QtWidgets.QPushButton('Reload in shape')
        #bReload3D.setCheckable(True)
        bReload3D.clicked.connect(self.LoadInRegion)
        hbox.addWidget(bReload3D)
        bCrop = QtWidgets.QPushButton('Crop to shape')
        #bCrop.setCheckable(True)
        bCrop.clicked.connect(self.CropToRegion)
        hbox.addWidget(bCrop)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Tissue threshold value:"))
        self.thresholdN = QtWidgets.QLineEdit("0.3")
        hbox.addWidget(self.thresholdN)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Number of regions to retain:"))
        self.spinN = QtWidgets.QSpinBox()
        self.spinN.setValue(1)
        hbox.addWidget(self.spinN)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Minimal size:"))
        self.maxSizeN = QtWidgets.QLineEdit("1000")
        hbox.addWidget(self.maxSizeN)
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        bKeepN = QtWidgets.QPushButton('Show only large regions')
        #bKeepN.setCheckable(True)
        bKeepN.clicked.connect(self.Keep_n_Regions)
        hbox.addWidget(bKeepN)
        bRemoveN = QtWidgets.QPushButton('Remove small regions')
        #bRemoveN.setCheckable(True)
        bRemoveN.clicked.connect(self.Remove_Small_Regions)
        hbox.addWidget(bRemoveN)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        
        
        
        hbox = QtWidgets.QHBoxLayout()

        bSaveSlice = QtWidgets.QPushButton('Save slice')
        bSaveSlice.clicked.connect(self.SaveSlice)
        hbox.addWidget(bSaveSlice)

        bSaveVolume = QtWidgets.QPushButton('Save volume')
        bSaveVolume.clicked.connect(self.SaveVolume)
        hbox.addWidget(bSaveVolume)

        bLoadVolume = QtWidgets.QPushButton('Load volume')
        bLoadVolume.clicked.connect(self.LoadVolume)
        hbox.addWidget(bLoadVolume)

        bLoadMask = QtWidgets.QPushButton('Load mask')
        bLoadMask.clicked.connect(self.LoadMask)
        hbox.addWidget(bLoadMask)

        hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        bAddPolygon = QtWidgets.QPushButton('Add')
        #bAddPolygon.setCheckable(True)
        bAddPolygon.clicked.connect(self.add_polygon)
        bRemoveOutside = QtWidgets.QPushButton('Remove outside interpolated region')
        #bRemoveOutside.setCheckable(True)
        bRemoveOutside.clicked.connect(self.run_remove_outside)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(bAddPolygon)
        hbox.addWidget(bRemoveOutside)
        hbox.addStretch(1)
        vbox.addLayout(hbox)


        bAdd3DShape = QtWidgets.QPushButton('2D to 3D shape')
        #bAdd3DShape.setCheckable(True)
        bAdd3DShape.clicked.connect(self.Make3DShape)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(bAdd3DShape)

        hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        cb_group2 = QtWidgets.QButtonGroup()
        self.cb_perspective = QtWidgets.QRadioButton('Perspective')
        self.cb_perspective.setChecked(True)
        self.cb_perspective.toggled.connect(self.SetPerspective)
        hbox.addWidget(self.cb_perspective)
        self.cb_isometric = QtWidgets.QRadioButton('Isometric')
        self.cb_isometric.setChecked(False)
        self.cb_isometric.toggled.connect(self.SetPerspective)
        hbox.addWidget(self.cb_isometric)
        cb_group2.addButton(self.cb_perspective)
        cb_group2.addButton(self.cb_isometric)
        hbox.addStretch(1)

        vbox.addLayout(hbox)
        vbox.addStretch(1)
        
        
        
        
        
        groupbox = QtWidgets.QGroupBox("3D")
        groupbox.setCheckable(False)
        groupbox.setLayout(vbox)
        layout.addWidget(groupbox)
        #widget.setLayout(layout)
        
        
        
        
        
        

        vbox = QtWidgets.QVBoxLayout()

        self.bLoad2D = QtWidgets.QPushButton('Load slice')
        self.bLoad2D.setCheckable(True)
        self.bLoad2D.clicked.connect(self.Load2D)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.bLoad2D)

        hbox.addStretch(1)
        vbox.addLayout(hbox)
        

        hbox = QtWidgets.QHBoxLayout()
        #hbox.addWidget(QtWidgets.QLabel("Slice:"))
        self.scroll = QtWidgets.QScrollBar()
        self.scroll.setOrientation(QtCore.Qt.Horizontal)
        self.scroll.setRange(0, 100)
        self.scroll.setMinimumWidth(150)
        self.scroll.valueChanged.connect(self.set_image_slice_value)
        hbox.addWidget(self.scroll)

        self.image_slice = QtWidgets.QLineEdit("0")
        self.image_slice.setMaximumWidth(30)
        hbox.addWidget(self.image_slice)

        #hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        
        
        groupbox = QtWidgets.QGroupBox("2D")
        groupbox.setCheckable(False)
        groupbox.setLayout(vbox)
        layout.addWidget(groupbox)
        
        
        widget.setLayout(layout)
        
        
        


        #widget.setLayout(vbox)
        
        dw1 = self.viewer.window.add_dock_widget(widget, area="right")
        dw1.setWindowTitle('Main')
        
        self.comboBoxPath.setMaximumWidth(1000000)
        
        
        
        
        # Math widget
        widget_merge = QtWidgets.QWidget()
        
        vbox = QtWidgets.QVBoxLayout()
        
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Layer 1:"))
        self.m_volume_1 = QtWidgets.QLineEdit("C2")
        self.m_volume_1.setMaximumWidth(75)
        hbox.addWidget(self.m_volume_1)
        hbox.addWidget(QtWidgets.QLabel("Multiplier:"))
        self.m_volume_1_multiplier = QtWidgets.QLineEdit("-5")
        self.m_volume_1_multiplier.setMaximumWidth(50)
        hbox.addWidget(self.m_volume_1_multiplier)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Layer 2:"))
        self.m_volume_2 = QtWidgets.QLineEdit("C3")
        self.m_volume_2.setMaximumWidth(75)
        hbox.addWidget(self.m_volume_2)
        hbox.addWidget(QtWidgets.QLabel("Multiplier:"))
        self.m_volume_2_multiplier = QtWidgets.QLineEdit("1")
        self.m_volume_2_multiplier.setMaximumWidth(50)
        hbox.addWidget(self.m_volume_2_multiplier)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        hbox = QtWidgets.QHBoxLayout()
        bMerge = QtWidgets.QPushButton('Merge layers')
        #bMerge.setCheckable(False)
        bMerge.clicked.connect(self.MergeLayers)
        hbox.addWidget(bMerge)
        hbox.addWidget(QtWidgets.QLabel("Output layer:"))
        self.m_volume_new = QtWidgets.QLineEdit("C_new")
        self.m_volume_new.setMaximumWidth(75)
        hbox.addWidget(self.m_volume_new)
        
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        
        
        vbox.addStretch(1)
        widget_merge.setLayout(vbox)
        
        dw2 = self.viewer.window.add_dock_widget(widget_merge, area='right')
        dw2.setWindowTitle('Processing')
        
        
        
        # Animation widget
        animation_widget = AnimationWidget(self.viewer)
        
        dw3 = self.viewer.window.add_dock_widget(animation_widget, area='right')
        dw3.setWindowTitle('Animation')
        
        
        self.viewer.window._qt_window.tabifyDockWidget(dw1, dw2)
        self.viewer.window._qt_window.tabifyDockWidget(dw1, dw3)

        napari.run()