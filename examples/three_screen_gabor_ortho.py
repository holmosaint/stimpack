#!/usr/bin/env python3
from stimpack.visual_stim.stim_server import launch_stim_server
from stimpack.visual_stim.screen import Screen, SubScreen

from time import sleep
import numpy as np
from itertools import product
from datetime import datetime

def main():
    pass


if __name__ == '__main__':
    main()
        # This must contain a file called stimuli.py that defines the custom stimuli
    PATH_TO_CUSTOM_STIMULI = './example_custom_module/'

    # Import the custom stimulus module onto server
    # Make two subscreen / screen objects at 90 degrees to one another
    monitor_id = 1
    subscreen_1 = SubScreen(pa=(-1.5, 0,   -0.75),
                            pb=(-0.5, 0.5, -0.75),
                            pc=(-1.5, 0,    0.75),

                            viewport_ll=(-1, -1),
                            viewport_width=2,
                            viewport_height=2)
    
    screen_1 = Screen(subscreens=[subscreen_1],
                      x_display=':1',
                      display_index=monitor_id,
                      fullscreen=True,
                      vsync=True)

    # Now let's make a second screen looking to the left of the first screen monitor_id = 1
    monitor_id = 2
    subscreen_2 = SubScreen(pa=(-0.5, 0.5, -0.75),
                            pb=( 0.5, 0,   -0.75),
                            pc=(-0.5, 0.5,  0.75),

                            viewport_ll=(-1, -1),
                            viewport_width=2,
                            viewport_height=2)
    
    screen_2 = Screen(subscreens=[subscreen_2],
                      x_display=':1',
                      display_index=monitor_id,
                      fullscreen=True,
                      vsync=True)

    # Now let's make a third screen looking to the left of the first screen monitor_id = 2
    monitor_id = 3
    subscreen_3 = SubScreen(pa=( 0.5, 0,   -0.75),
                            pb=( 1.5, 0,   -0.75),
                            pc=( 0.5, 0.5,  0.75),

                            viewport_ll=(-1, -1),
                            viewport_width=2,
                            viewport_height=2)
    
    screen_3 = Screen(subscreens=[subscreen_3],
                      x_display=':1',
                      display_index=monitor_id,
                      fullscreen=True,
                      vsync=True)

    # Launch the stim server
    screens = [screen_1, screen_2, screen_3]

    # Launch the stim server
    manager = launch_stim_server(screens)
    sleep(2)

    # Import the custom stimulus module
    manager.import_stim_module(PATH_TO_CUSTOM_STIMULI)

    # Set the background color of the screen
    manager.set_idle_background(0.5)

    # define the stimulus parameters
    stimulus_params = {
        'wavelength': 0.75,
        'sigma_x': 10,
        'sigma_y': 10,
        'sigma_mask': 0.75,
        'size_x': 10,
        'size_y': 10
    }

    # define the presentation parameters
    orientations = [0, 90]
    itis = [3]
    durs = [0.25, 0.5, 1, 2]
    repetitions = 30
    presentation_params = np.array(list(product(orientations, durs, itis)))
    presentation_params = np.repeat(presentation_params, repeats=repetitions, axis=0)
    current_date = datetime.now().strftime("%Y%m%d")
    np.random.seed(int(current_date))
    jitter = np.random.randn(presentation_params.shape[0])
    presentation_params[:, 2] += jitter
    np.random.shuffle(presentation_params)
    total_time = presentation_params[1:].sum()
    presentation_params = {
        'orientation': list(presentation_params[:, 0]),
        'iti': list(presentation_params[:, 1]),
        'dur': list(presentation_params[:, 2]),
    }

    # Present 5 epochs of the stimulus
    rotation = 0
    # Load a stimulus - here ShowImage is a new stimulus class found within the custom module directory
    manager.load_stim(name='ShowGaborOrtho', 
                      stimulus_params=stimulus_params, 
                      presentation_params=presentation_params, 
                      vertical_extent=180, horizontal_extent=180, 
                      rotate=rotation)

    # Start the stimulus
    manager.start_stim()

    # Stim time: client waits for 4 seconds while server shows the stimulus
    sleep(total_time)

    # Stop the stimulus
    manager.stop_stim(print_profile=True)