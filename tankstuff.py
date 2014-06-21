'''
Created on Jun 19, 2014

@author: Student
'''

import gamebox
import random
import math

class Barrier():
    block_size_x = 10
    block_size_y = 10
    price = 50
    
    def __init__(self, x, y, width, height):
        self.blocks = []
        for i in range(width):
            for j in range(height):
                blockx = x + Barrier.block_size_x * i
                blocky = y + Barrier.block_size_y * j
                block = gamebox.from_color(blockx, blocky, "red", Barrier.block_size_x, Barrier.block_size_y)
                self.blocks.append(block)
    
    def draw(self, camera):
        for b in self.blocks:
            camera.draw(b)
        
    def check(self, killers):
        for block in self.blocks:
            for killer in killers:
                if block.touches(killer) and (killer in killers) and (block in self.blocks):
                    self.blocks.remove(block)
                    killers.remove(killer)
    
    def check_collision(self, thing):
        for block in self.blocks:
            if thing.touches(block):
                thing.move_to_stop_overlapping(block)
        
            
        

class Bullet(gamebox.SpriteBox):
    def __init__(self, x , y, dir):
        gamebox.SpriteBox.__init__(self, x, y, None, "yellow", 3, 3)
        self.speedy, self.speedx  = dir
        self.duration = 30
        self.alive = True
            
    def tick(self):
        self.move_speed()
        self.duration -= 1
        if self.duration <= 0:
            self.alive = False


class Tank(gamebox.SpriteBox):
    price = 500
    def __init__(self, x, y, image, images = None): 
        gamebox.SpriteBox.__init__(self, x, y, image, None)
        
        # Handle Animation
        self.images = images
        self.animation_step = 0
        self.facing = 0
        self.reloading = False 
        self.reload_time = 10
        self.ammo = 5 
        self.delay = 5
        
    def fire_bullet(self):
        if self.ammo > 0 and not self.reloading and self.delay == 0 and random.randint(0,5) == 3:
            self.ammo -= 1
            self.delay = 5
            
            dx = math.cos(math.radians(self.facing + 90)) * 8
            dy = math.sin(math.radians(self.facing + 90)) * 8
            b = Bullet(self.x, self.y, ((dx,dy)))
            return b
        
        if self.ammo == 0 and not self.reloading:
            self.reloading = True
        
        if self.reloading and self.delay > 0:
            self.delay -= 1
            
        if self.reloading and self.delay == 0:
            self.ammo += 1
        
        if self.reloading and self.ammo == 5:
            self.reload_time = False
        
        return False
    
    def rotate(self, angle):
        self.facing += angle
        return gamebox.SpriteBox.rotate(self, angle)
        
    def turn_left(self):
        self.rotate(2)
    
    def turn_right(self):
        self.rotate(-2)
    
    def forward(self):
        self.speedx = int(math.cos(math.radians(self.facing)) * 2)
        self.speedy = int(math.sin(math.radians(self.facing)) * -2)
        self.animation_step -= 1
    
    def backward(self):
        self.speedx = int(math.cos(math.radians(self.facing)) * 5) * -2
        self.speedy = int(math.sin(math.radians(self.facing)) * -5) * -2
        self.animation_step += 1
    
    def tick(self):
        self.facing = self.facing % 360
        self.move_speed()
        if (self.speedx > 0):
            self.speedx -= 1
        if (self.speedy > 0):
            self.speedy -= 1
        if (self.speedx < 0):
            self.speedx += 1
        if (self.speedy < 0):
            self.speedy += 1
            
        if self.reloading:
            self.ammo += 1
            if self.ammo == 10:
                self.reloading = False
    
        if self.delay > 0:
            self.delay -= 1
        
        self.image = self.images[self.animation_step % len(self.images)]
 
        
class Button():
    def __init__(self, x, y, color = "blue",text_color = "green", image = None, text = None, width = 50, height = 50):
        self.x, self.y = x, y
        self.box = gamebox.from_color(x, y, color, width, height)
        self.text_color = text_color
        self.text = text 
        self.image = image
        
    def draw(self, camera):
        camera.draw(self.box)
        if self.text:
            t = gamebox.from_text(self.x, self.y, self.text, 'arial', 10, self.text_color)
            camera.draw(t)
            
    def clicked(self, camera):
        mx, my = camera.mousex, camera.mousey
        mouse_box = gamebox.from_color(mx, my, "white", 1, 1)
        return mouse_box.touches(self.box)

class Mine(gamebox.SpriteBox):
    range = 50
    price = 100
    image = None 
    def __init__(self, x, y):
        if not Mine.image:
            gamebox.SpriteBox.__init__(self, x, y, image = None,color = "white", w = 10, h = 10)
        else:
            gamebox.SpriteBox.__init__(self, x, y, Mine.image,None, 15, 15)
        self.live = True
        
    def explode(self):
        self.live = False
        return Boom(self.x, self.y, Mine.range)

class Boom(gamebox.SpriteBox):
    duration = 5
    image = None
    def __init__(self, x, y, size):
        if not Boom.image:
            gamebox.SpriteBox.__init__(self, x, y, None, "orange", size, size)
        else:
            gamebox.SpriteBox.__init__(self, x, y, Boom.image, None , size, size)
        self.life = Boom.duration
        self.alive = True
    
    def tick(self):
        self.life -= 1
        if self.life <= 0:
            self.alive = False

class ButtonStateMachine():
    def __init__(self):
        self.state = None
        
    def has_state(self):
        return (not self.state == None)
    
    def clear_state(self):
        self.state = None
    
    def set_state(self, state):
        self.state = state
        
    def __eq__(self, value):
        return self.state == value
    