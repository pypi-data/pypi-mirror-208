import pygame, sys, time, base64, os, json

#pygame initialization
version = "Beta 1.1.2.1"
print(f"\nAdditional hello from pygameHat {version} :D")
print("\nThis version may not be compatible with older versions")

pygame.init()
pygame.font.init()
try:
    pygame.mixer.init()
except:
    print("WARNING: Failed to initialize audio!")

#main objects
class Object:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.sprite = None
        self.visible = True
        self.active_timers = {}
        self.tags = []
    
    def draw(self):
        draw_sprite(self.sprite, self.x, self.y)
    
    def step(self):
        pass
    def key_just_pressed(self, key):
        pass
    def key_just_released(self, key):
        pass
    def is_colliding(self, object):
        pass
    def on_destroy(self):
        pass
    def on_alarm(self, alarm):
        pass


    def add_timer(self, time, name):
        self.active_timers[name] = time
    
    def decrement_active_timers(self):
        dead_timers = []

        for timer in self.active_timers:
            self.active_timers[timer] -= delta_time
            if self.active_timers[timer] < 0:
                dead_timers.append(timer)
                self.on_alarm(timer)
        
        for timer in dead_timers:
            self.active_timers.pop(timer)

class Room:
    def __init__(self, background=(50, 50, 50), layers={"default": []}, instances=[]):
        self.background = background
        self.layers = layers
        self.instances = instances

class Sprite:
    def __init__(self, index, spritesheet_data=(1, 1), speed=60, collision=False, offset="upper-left", looping=True, size=None):
        if type(index) == type(pygame.Surface((0, 0))):
            self.index = index
        else:
            self.index = pygame.image.load(index).convert_alpha()

        self.speed = speed
        self.x_frames, self.y_frames = spritesheet_data

        if size:
            resize_sprite(self, size)

        self.x_size, self.y_size = self.index.get_width()/(self.x_frames), self.index.get_height()/(self.y_frames)
        
        self.x_frames -= 1
        self.y_frames -= 1

        self.current_x_frame = 0
        self.current_y_frame = 0
        self.timer = 1/self.speed
        self.loop = looping
        self.on_last_frame = False

        self.collision = collision
        self.collision_shape = self.reload_collision_shape()
    
        #Setting sprite offset
        if offset == "middle-center":
            self.x_offset, self.y_offset = self.x_size/2, self.y_size/2
        elif offset == "upper-left":
            self.x_offset, self.y_offset = 0, 0
        elif offset == "upper-center":
            self.x_offset, self.y_offset = self.x_size/2, 0
        elif offset == "upper-right":
            self.x_offset, self.y_offset = self.x_size, 0
        elif offset == "middle-left":
            self.x_offset, self.y_offset = 0, self.y_size/2
        elif offset == "middle-right":
            self.x_offset, self.y_offset = self.x_size, self.y_size/2
        elif offset == "lower-left":
            self.x_offset, self.y_offset = 0, self.y_size
        elif offset == "lower-center":
            self.x_offset, self.y_offset = self.x_size/2, self.y_size
        elif offset == "lower-right":
            self.x_offset, self.y_offset = self.x_size, self.y_size
        elif offset == "":
            self.x_offset, self.y_offset = self.x_size, self.y_size
        else:
            self.x_offset, self.y_offset = offset

        self.collision_shape.x = self.x_offset
        self.collision_shape.y = self.y_offset

    def play(self):
        self.on_last_frame = False
        self.current_x_frame = 0
        self.current_y_frame = 0      

    def set_alpha(self, value):
        self.index.set_alpha(value)

    def animate(self):
        self.timer -= delta_time
        if self.timer <= 0:
            if self.current_x_frame < self.x_frames:
                self.current_x_frame += 1
            elif self.current_y_frame < self.y_frames:
                self.current_x_frame = 0
                self.current_y_frame += 1
            elif self.loop:
                self.play()
            else:
                self.on_last_frame = True
            self.timer = 1/self.speed

    def update_collision_shape_position(self, x, y):
        self.collision_shape.x = x-self.x_offset
        self.collision_shape.y = y-self.y_offset

        return self.collision_shape

    def reload_collision_shape(self):
        self.x_size, self.y_size = self.index.get_width()/(self.x_frames+1), self.index.get_height()/(self.y_frames+1)
        self.collision_shape = self.index.get_rect(width=self.x_size, height=self.y_size)
        return self.collision_shape

class Sound:
    def __init__(self, file, large=False):
        if pygame.mixer.get_init():
            if large:
                self.sound = pygame.mixer_music.load(file)

            self.sound = pygame.mixer.Sound(file)
        else:
            print("WARNING:", file, "cannot be loaded!")
            self.sound = None
    
    def play(self, loops=0):
        if self.sound:
            self.sound.play(loops)
    
    def stop(self):
        if self.sound:
            self.sound.stop()

class Font:
    def __init__(self, size, path="default", color=(255, 255, 255), background_color=None):
        if path == "default":
            self.font = pygame.font.Font(None, size)
        else:
           self.font = pygame.font.Font(path, size)
        
        self.color = color
        self.background_color = background_color
    
    def measure_size(self, text_to_measure):
        return self.font.render(text_to_measure, True, (0, 0, 0)).get_size()

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

class Console:
    def __init__(self):
        self.text = ""
        self.opened = False
    
    def display(self):
        if self.opened:
            screen.blit(debug_font.render(">>"+self.text, True, (255, 255, 255), (0, 0, 0)), (0, 0))
    
    def switch(self):
        if self.opened:
            self.opened = False
            self.text = ""
        else:
            self.opened = True
    
    def input(self, key, unicode):

        if key == pygame.K_F10 and Settings.enable_console:
            self.switch()
            key = ""
        
        if self.opened:
            self.text += unicode
        if key == pygame.K_RETURN:
            text_to_return = self.text
            self.text = ""
            return text_to_return
        elif key == pygame.K_BACKSPACE:
            self.delete_from_end()
    
    def delete_from_end(self):
        if len(self.text) > 0:
            self.text = self.text[:-2]
        
class SurfaceStringifier:
    #Massive thanks to Chat-GPT for telling me about base64

    def to_surface(self, string, size):
        return pygame.image.fromstring(base64.b64decode(string), size, "RGBA")

    def to_string(self, surface):
        return base64.b64encode(pygame.image.tostring(surface, "RGBA")).decode()
surfaceStringifier = SurfaceStringifier()
class SaveManager:
    def save(self, jsonfile, path):
        saveable = json.dumps(jsonfile, indent=4)
        with open(path, "w") as file:
            file.write(saveable)
            file.close()
        return saveable
    def load(self, path):
        with open(path, "rb") as file:
            readable = file.read()
            file.close()
        return json.loads(readable)
saveManager = SaveManager()

#game settings
class Settings:
    window_size = (1200, 700)
    room_size = (0, 0)
    window_title =  "pygameHat "+version
    fullscreen = False
    icon = None
    enable_console = True
    fps = 60
    font = "default"

    shameless_ad = True

class RoomGotChanged(Exception):
    pass

temp_icon = surfaceStringifier.to_surface("7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f//v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f//v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//39/f/9/f3//f39//+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/+/ksP/v5LD/7+Sw/+/ksP+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V//v5LD/7+Sw/+/ksP/v5LD/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/uXpX/7l6V/+5elf/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/3CSvv//////cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP9wkr7//////3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw//////////////////////9wkr7/cJK+/3CSvv9wkr7/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv//8gD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7///IA///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv//8gD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP9wkr7/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7///IA///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/cJK+/3CSvv9wkr7/cJK+/3CSvv9wkr7/cJK+///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP//8gD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD///IA///yAP//8gD///IA///yAP//8gD///IA///yAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw///yAP//8gD///IA///yAP//////////////////////7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD///IA///yAP//8gD///IA///yAP////////IA///yAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/AAAA/wAAAP8AAAD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw///yAP//8gD///IA///yAP//8gD////////yAP//8gD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP8AAAD/AAAA/wAAAP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/wAAAP8AAAD/AAAA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP//8gD///IA///yAP//8gD///IA///yAP//8gD///IA/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/+/ksP/v5LD/7+Sw/w==", (70, 70))
temp_icon = pygame.transform.scale(temp_icon, (32, 32))

#first initializations
debug_font = pygame.font.Font
title_font = pygame.font.Font
console_opened = False
console = Console()
delta_time = 0
current_time = 0

screen = pygame.surface.Surface(Settings.window_size)
camera = Camera()
screen_size = (0, 0)

current_room = Room()
changed_room = False

def init():
    global screen, screen_size, debug_font, title_font

    if Settings.icon:
        pygame.display.set_icon(pygame.image.load(Settings.icon))
    else:
        pygame.display.set_icon(temp_icon)

    if Settings.font == "default":
        debug_font = pygame.font.Font(None, 25)
        title_font = pygame.font.Font(None, 100)
    else:
        debug_font = pygame.font.Font(Settings.font, 25)
        title_font = pygame.font.Font(Settings.font, 100)

    monitor = pygame.display.set_mode(Settings.window_size)

    rSX, rSY = Settings.room_size
    if not rSX and not rSY:
        Settings.room_size = Settings.window_size

    pygame.display.set_caption(Settings.window_title)
    screen.blit(title_font.render("Made with Pygame Hat", True, (255, 255, 255)), (100, 100))
    screen.blit(title_font.render(version, True, (255, 255, 255)), (100, 200))
    screen.blit(title_font.render("OWO", True, (255, 255, 255)), (100, 400))

    if Settings.shameless_ad:
        screen = pygame.transform.scale(screen, Settings.room_size).convert()
        monitor.blit(screen, (0, 0))
        pygame.display.flip()
        time.sleep(1.5)
    screen = pygame.surface.Surface(Settings.room_size)
    screen_size = Settings.window_size

def compile_for_windows(main_file, output_directory="./", icon=None):
    monitor = pygame.display.set_mode((900, 500))
    pygame.display.set_icon(temp_icon)
    pygame.display.set_caption("Compiler")
    monitor.blit(pygame.font.Font(None, 100).render("Please stand by", True, (255, 255, 255)), (100, 50))
    monitor.blit(pygame.font.Font(None, 100).render("(=>wO=)", True, (255, 255, 255)), (100, 150))
    pygame.display.flip()

    comm = ""
    if icon:
        comm = "--icon=%s" % icon
    
    os.system(f"pyinstaller --onefile --noconsole --distpath={output_directory} {comm} {main_file}")

    monitor.fill((0, 0, 0))
    monitor.blit(pygame.font.Font(None, 100).render("Done compiling!", True, (3, 252, 48)), (100, 50))
    monitor.blit(pygame.font.Font(None, 100).render("(=OwO=)", True, (3, 252, 48)), (100, 150))
    pygame.display.flip()

def add_object_instance(object, layer, position="default"):
    if position != "default":
        object.x, object.y = position
    current_room.layers[layer].append(object)
    return object

def find_object_by_class(object, multiple=False):
    found_objects = []

    for layer in current_room.layers:
        for instance in current_room.layers[layer]:
            if instance.__class__ == object.__class__:
                    found_objects.append(instance)
        
    if len(found_objects) > 0:
        if multiple:
            return found_objects
        else:
            return found_objects[-1]
    else:
        return None

def find_objects_by_tags(tag_list, searchtype="all"):
    found_objects = []

    if len(tag_list) > 0:
        for layer in current_room.layers:
            for instance in current_room.layers[layer]:
                appearances = 0
                for tag in tag_list:
                    if tag in instance.tags:
                        appearances += 1
                if searchtype == "all" and appearances == len(tag_list) or searchtype == "any" and appearances > 0 or searchtype == "exall" and appearances == 0 or searchtype == "exany" and appearances < len(tag_list):
                    found_objects.append(instance)
    return found_objects

def collide_objects(object1, object2):
    if object1 != object2 and object1.sprite and object1.sprite.collision and object2.sprite and object2.sprite.collision:
        object1_shape = object1.sprite.update_collision_shape_position(object1.x, object1.y)
        object2_shape = object2.sprite.update_collision_shape_position(object2.x, object2.y)
        if object1_shape.colliderect(object2_shape):
            return object2

def collide_point(point, object):
    pointX, pointY = point
    pointX += camera.x
    pointY += camera.y

    if object.sprite and object.sprite.collision:
        object_shape = object.sprite.update_collision_shape_position(object.x, object.y)

        if object_shape.collidepoint((pointX, pointY)):
            return object

def screen_position_to_ingame_position(position):
    pX, pY = position
    rSX, rSY = Settings.room_size
    sSX, sSY = screen_size

    tSX = sSX/rSX
    tSY = sSY/rSY

    pX += camera.x+1*tSX
    pY += camera.y+1*tSY

    return pX//tSX, pY//tSY

def get_mouse_position():
    return screen_position_to_ingame_position(pygame.mouse.get_pos())

def destroy_object(object):
    for layer in current_room.layers:
        for instance in current_room.layers[layer]:
            if object == instance:
                object.on_destroy()
                current_room.layers[layer].remove(instance)

def draw_sprite(sprite, x, y):
        if sprite:
            screen.blit(sprite.index, (x-camera.x-sprite.x_offset, y-camera.y-sprite.y_offset), (sprite.x_size*sprite.current_x_frame, sprite.y_size*sprite.current_y_frame, sprite.x_size, sprite.y_size))
            sprite.animate()

def resize_sprite(sprite, dimensions):
    #:todo fix offset
    sx, sy = dimensions
    sprite.index = pygame.transform.scale(sprite.index, (int(sx*(sprite.x_frames+1)), int(sy*(sprite.y_frames+1))))
    sprite.reload_collision_shape()

    return sprite

def draw_font(position, font, text, color="default", background_color="default"):
    if color == "default":
        color = font.color
    else:
        color = color
    if background_color == "default":
        bg_color = font.background_color
    else:
        bg_color = background_color

    x, y = position
    screen.blit(font.font.render(text, True, color, bg_color), (x-camera.x, y-camera.y))

def change_room(room):
    global current_room, changed_room
    current_room = room
    changed_room = True


def start():
    timeB = 0
    last_input = None
    last_input_released = None
    console_text = ""
    global delta_time, current_time
    global screen, screen_size
    global changed_room

    if Settings.fullscreen:
        monitor = pygame.display.set_mode(Settings.window_size, pygame.FULLSCREEN)
    else:
        monitor = pygame.display.set_mode(Settings.window_size, pygame.RESIZABLE)

    running = True
    while running:
        pygame.time.Clock().tick(Settings.fps)

        current_time = time.time()
        delta_time = current_time-timeB
        timeB = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                last_input = event.key
                #console management
                console_text = console.input(event.key, event.unicode)

            elif event.type == pygame.KEYUP:
                #handling keyups for objects
                last_input_released = event.key
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                last_input = event.button
            
            elif event.type == pygame.MOUSEBUTTONUP:
                last_input_released = event.button
            
            elif event.type == pygame.VIDEORESIZE:
                screen_size = (event.w, event.h)

        #background                
        if type(current_room.background) == Sprite:
            draw_sprite(current_room.background, 0, 0)
        else:
            screen.fill(current_room.background)
    
        #object handling
        try:
            for layer in current_room.layers:
                for instance in current_room.layers[layer]:
                    #object drawing and processing
                    if instance.visible:
                        instance.draw()
                    instance.step()
                    instance.decrement_active_timers()
                    #collision processing
                    for layer2 in current_room.layers:
                        for instance2 in current_room.layers[layer2]:
                            obj = collide_objects(instance, instance2)
                            if obj:
                                instance.is_colliding(obj)
                    #inputs
                    if last_input:
                        instance.key_just_pressed(last_input)
                    if last_input_released:
                        instance.key_just_released(last_input_released)
                    
                    if changed_room:
                        raise RoomGotChanged
        except RoomGotChanged:
            changed_room = False
            screen.fill(current_room.background)
        
        console.display()

        monitor.blit(pygame.transform.scale(screen, screen_size), (0, 0))
        pygame.display.flip()

        last_input = None
        last_input_released = None

        #console_handling v2
        if console_text:
            try:
                exec(console_text)
            except:
                print("Something went wrong!")
            console_text = None
