"""
Stimulus classes.

Each class is is derived from stimpack.visual_stim.base.BaseProgram, which handles the GL context and shader programs

"""

from PIL import Image
import numpy as np
from stimpack.visual_stim.base import BaseProgram
from stimpack.visual_stim.trajectory import make_as_trajectory, return_for_time_t
from stimpack.visual_stim import shapes
from stimpack.visual_stim import util
import copy

from stimpack.visual_stim.gabor_patterns import generate_gabor_filters

def convert_float_to_rgb(data):
    data -= data.min()
    data /= data.max()
    data *= 255
    data = data.astype(np.uint8)
    
    return data

class ShowImage(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen, num_tri=14000)
        
        self.use_texture=True
        self.rgb_texture=True

    def configure(self, image_path, horizontal_extent=360, vertical_extent=180, rotate=0):
        # image = np.zeros((200,400,3))
        image = Image.open(image_path)
        image = np.array(image)
        
        image = image.astype(np.uint8)
        image = image[:,:,:3]
        
        self.rgb_texture=True

        n_steps=32

        self.add_texture_gl(image, texture_interpolation='NEAREST')

        self.stim_object = shapes.GlSphericalTexturedRect(height=vertical_extent, width=horizontal_extent, sphere_radius=1,
                                                          n_steps_x = n_steps, n_steps_y = n_steps, 
                                                          color=[1,1,1,1], texture=True).rotate(np.radians(rotate),0,0)


        self.update_texture_gl(image)
    def eval_at(self, t, subject_position={'x':0, 'y':0, 'z':0, 'theta':0, 'phi':0, 'roll':0}):
        pass
        # rotation = 0.2
        # self.stim_object = self.stim_object.rotate(np.radians(rotation),0,0)

class ShowGaborOrtho(BaseProgram):
    def __init__(self, screen):
        super().__init__(screen=screen, num_tri=14000)
        
        self.use_texture = True
        # gray scale
        self.rgb_texture = False

    def configure(self, stimulus_params, presentation_params, horizontal_extent=360, vertical_extent=180, rotate=0):
        self.rgb_texture = False
        assert type(stimulus_params) == dict
        self.wavelength = stimulus_params['wavelength']
        self.stim_size_x = stimulus_params['size_x']
        self.stim_size_y = stimulus_params['size_y']
        self.stim_sigma_x = stimulus_params['sigma_x']
        self.stim_sigma_y = stimulus_params['sigma_y']
        self.stim_sigma_mask = stimulus_params['sigma_mask']
        
        self.orientation_list = presentation_params['orientation']
        self.iti_list = presentation_params['iti']
        self.dur_list = presentation_params['dur']
        
        self.gabor_dict = {
            orientation: convert_float_to_rgb(generate_gabor_filters(size_x=self.stim_size_x,
                                                                     size_y=self.stim_size_y,
                                                                     wavelength=self.wavelength,
                                                                     orientation=orientation,
                                                                     sigma_x=self.stim_size_x,
                                                                     sigma_y=self.stim_sigma_y,
                                                                     sigma_mask=self.stim_sigma_mask))
            for orientation in np.unique(self.orientation_list)
        }
        
        n_steps = 32
        
        first_show = self.gabor_dict[self.orientation_list[0]]
        print(first_show.shape, first_show.dtype)
        self.idle = (np.ones(first_show.shape)*0.5).astype(np.uint8) # gray screen
        self.add_texture_gl(first_show, texture_interpolation='NEAREST')
        self.stim_object = shapes.GlSphericalTexturedRect(height=vertical_extent, width=horizontal_extent, sphere_radius=1,
                                                                n_steps_x = n_steps, n_steps_y = n_steps, 
                                                                color=[1,1,1,1], texture=True).rotate(np.radians(rotate),0,0)
        self.update_texture_gl(first_show)
        
        # record the info useful to controling the stimulus
        self.cur_onset = 0
        self.cur_stim_idx = 0
        self.show_flag = False
        
        print(self.gabor_dict[0.0])
        
    def eval_at(self, t, subject_position={'x':0, 'y':0, 'z':0, 'theta':0, 'phi':0, 'roll':0}):
        print(self.cur_stim_idx, self.orientation_list[self.cur_stim_idx], end='\r')
        iti, dur = self.iti_list[self.cur_stim_idx], self.dur_list[self.cur_stim_idx]
        # if it is the next stimulus
        if t > self.cur_onset + dur + iti:
            self.cur_stim_idx += 1
            self.cur_onset = t
            self.show_flag = False
            iti, dur = self.iti_list[self.cur_stim_idx], self.dur_list[self.cur_stim_idx]
            
        # if all stimuli have been shown
        if self.cur_stim_idx >= len(self.orientation_list):
            self.update_texture_gl(self.idle)
            return
            
        # continue presenting the same image
        if t < self.cur_onset + self.dur_list[self.cur_stim_idx]:
            if not self.show_flag:
                self.update_texture_gl(self.gabor_dict[self.orientation_list[self.cur_stim_idx]])
                self.show_flag = True
        elif t > self.cur_onset + dur and t < self.cur_onset + dur + iti:
            self.update_texture_gl(self.idle)
        # rotation = 0.2
        # self.stim_object = self.stim_object.rotate(np.radians(rotation),0,0)