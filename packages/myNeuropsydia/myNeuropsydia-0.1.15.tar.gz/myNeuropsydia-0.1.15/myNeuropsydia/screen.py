# -*- coding: utf-8 -*-
"""
Module initializing screen object and screen values.
"""
import os
import pygame
import time as builtin_time

from .path import * 

'''
# Change neuropsydia.screen to "__main__" When building API documentation. This is to avoid sphinx to run this code, otherwise the documentations fails to be built. "neuropsydia.screen" to make it work.
if __name__ == "myNeuropsydia.screen":

    prkrt = 0
 
    pygame.display.set_icon(pygame.image.load(Path.logo() + 'icon.png'))
    screen = pygame.display.set_mode((0,0), pygame.SRCALPHA | pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
    print('screen called')
    pygame.display.set_caption('Neuropsydia')
    screen_width, screen_height = screen.get_size()
    monitor_diagonal = 24  # inch
 
else:
    print('OOPS')
    print(__name__)
    screen = "Placeholder"
    screen_width, screen_height = 0, 0
    monitor_diagonal = 24
    
'''
class Font_Cache_Init:
    
    def __init__(self):
        self.cache = {}  #Initialize an empty cache
        
    def get(self,font_path,size):
        
        if not (font_path,int(size)) in self.cache:  #if not in cache,
            if os.path.exists(font_path):  #if the path leads to a font,
                self.cache[font_path,int(size)] = pygame.font.Font(font_path, int(size))  
              
            else:
                self.cache[font_path,int(size)] = pygame.font.SysFont(font_path, int(size))  #load a system font
        
        return(self.cache[font_path,int(size)])
    
    
    
class Time():
    
    """
    A class object to wait some time, get time, control time and such.
    Its methods (functions) are:
        - reset()
        - control()
        - wait()
        - get()
    See those for further informations.

    Note that by default, there is already a Time class object called "time" (lowercase) that is initialized at neuropsydia's loading. For the sake of clarity, use this one (e.g., n.time.wait() ), especially for wait() and control() functions.

    Parameters
    ----------
    None

    Returns
    ----------
    None

    Example
    ----------
    >>> import neuropsydia as n
    >>> n.start()
    >>> myclock = n.Time()
    >>> time_passed_since_myclock_creation = myclock.get()
    >>> myclock.reset()
    >>> time_passed_since_reset = myclock.get()
    >>> n.close()

    Authors
    ----------
    Dominique Makowski

    Dependencies
    ----------
    - pygame
    - time
    """
    
    def __init__(self):
        
        self.clock = builtin_time.perf_counter()
        self.pygame_clock = pygame.time.Clock()


    def reset(self):
        
        """
        Reset the clock of the Time object.

        Parameters
        ----------
        None

        Returns
        ----------
        None

        Example
        ----------
        >>> import neuropsydia as n
        >>> n.start()
        >>> time_passed_since_neuropsydia_loading = n.time.get()
        >>> n.time.reset()
        >>> time_passed_since_reset = n.time.get()
        >>> n.close()

        Authors
        ----------
        Dominique Makowski

        Dependencies
        ----------
        - pygame
        - time
        """
        
        self.clock = builtin_time.perf_counter()
        self.pygame_clock = pygame.time.Clock()


    def control(self, frequency=60):
        
        """
        Control time. Must be placed in a while loop and, each time the program runs through it, checks if the time passed is less than a certain amount (the frequency, by default 60, so 1/60 seconds). If true, the program stops and wait what needed before continuing, so that each loop takes at least 1/frequency seconds to be complete.

        Parameters
        ----------
        frequency = int, optional
            The minimum frequency you want the loop to run at

        Returns
        ----------
        None

        Example
        ----------
        >>> import neuropsydia as n
        >>> n.start()
        >>> while n.time.get() < 5:
        >>>     n.time.control()
        >>>     print(n.time.get())
        >>> n.close()

        Authors
        ----------
        Dominique Makowski

        Dependencies
        ----------
        - pygame
        - time
        """
        
        self.pygame_clock.tick_busy_loop(frequency)
        

    def get(self, reset=True):
        
        """
        Get time since last initialisation / reset.

        Parameters
        ----------
        reset = bool, optional
            Should the clock be reset after returning time?

        Returns
        ----------
        float
            Time passed in milliseconds.

        Example
        ----------
        >>> import neuropsydia as n
        >>> n.start()
        >>> time_passed_since_neuropsydia_loading = n.time.get()
        >>> n.time.reset()
        >>> time_passed_since_reset = n.time.get()
        >>> n.close()

        Authors
        ----------
        Dominique Makowski

        Dependencies
        ----------
        - pygame
        - time
        """
        
        t = (builtin_time.perf_counter()-self.clock)*1000

        if reset is True:
            self.reset()
            
        return(t)


    def wait(self, 
             time_to_wait, unit="ms", frequency=60, 
             round_by_frame=True, skip=None):
        
        """
        Wait some time.

        Parameters
        ----------
        time_to_wait = int
            Time to wait
        unit = str
            "min" for minutes, "s" for seconds, "ms" for milliseconds, or "frame" for a certain amount of frames (depending on the frequency parameter)
        frequency = int
            should be a multiple of your monitor's refresh rate
        round by frame = bool
            should the waiting time be rounded to match an exact number of frame / refresh cycles? (e.g., on a 60Hz monitor, 95ms will be rounded to 100, because the monitor is refreshed every 16.6667ms)
        skip = str
            Shoud there be a key to skip the waiting. Default to None.

        Returns
        ----------
        float
            Actual time waited in milliseconds

        Example
        ----------
        >>> import neuropsydia as n
        >>> n.start()

        >>> n.write("let's wait 500ms", round_by_frame = False)
        >>> n.refresh()
        >>> wait_time = n.time.wait(520)
        >>> n.newpage("white")
        >>> n.write("I waited for " + str(wait_time) + "ms")
        >>> n.refresh()
        >>> wait_time = n.time.wait(520, round_by_frame = True)
        >>> n.newpage("white")
        >>> n.write("I waited for " + str(wait_time) + "ms")
        >>> n.refresh()
        >>> n.time.wait(3, unit = "s")

        >>> n.close()

        Authors
        ----------
        Dominique Makowski

        Dependencies
        ----------
        - pygame
        - time
        """
        
        t0 = builtin_time.perf_counter()
        if unit == "min":
            time_to_wait = time_to_wait * 60
            unit = "s"
            
        if unit == "s":
            time_to_wait = time_to_wait * 1000
            unit = "ms"
            
        if unit == "ms":
            if round_by_frame is True:
                time_to_wait = round(time_to_wait / (1/frequency*1000))
                time_to_wait = round(time_to_wait * (1/frequency*1000))
                
        if unit == "frame":
            time_to_wait = time_to_wait * (1/frequency*1000)

        if skip is None:
            pygame.time.delay(time_to_wait)  # In milliseconds
            
        else:
            response(allow=skip, time_max=time_to_wait)
            
        return((builtin_time.perf_counter()-t0)*1000)


    def now(self):
        
        """
        Returns current (absolute) date and time.

        Parameters
        ----------
        None

        Returns
        ----------
        datetime
            Current date and time.

        Example
        ----------
        >>> import neuropsydia as n
        >>> n.start()

        >>> n.time.now()

        >>> n.close()

        Authors
        ----------
        Dominique Makowski

        Dependencies
        ----------
        - datetime
        """
        
        return(datetime.datetime.now())
 
    
 
    
def init():
    
    global Font
    Font = Font_Cache_Init() 
    
    global time
    time = Time()
    
    pygame.display.set_icon(pygame.image.load(Path.logo() + 'icon.png'))
    global screen 
    screen = pygame.display.set_mode((0,0), pygame.SRCALPHA | pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
    print('screen called once')
    pygame.display.set_caption('Neuropsydia')
    
    global screen_width
    global screen_height
    screen_width, screen_height = screen.get_size()
    
    global monitor_diagonal
    monitor_diagonal = 24  # inch