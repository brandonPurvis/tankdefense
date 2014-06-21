'''
Created on Jun 19, 2014

@author: Student
'''

import pygame
import gamebox
import tankstuff
import random

def generate_tanks(amount, xmin, xmax, ymin, ymax):
    tanks = []
    for i in range(amount):
        rx, ry = random.randint(xmin,xmax), random.randint(ymin,ymax)
        tank = tankstuff.Tank(rx, ry,tank_sprite_sheet[0],tank_sprite_sheet[:8])
        tank.rotate(180)
        tanks.append(tank)
    return tanks



def tick(keys):
    global score
    global cash
    global wave
    global wave_started
    global tank_count
    global tick_count
    global ticks_per_second
    global timer
    global T
    
    # Count Tick
    if not wave_started:
        tick_count += 1
        if tick_count % ticks_per_second == 0:
            tick_count = 0
            timer -= 1
            
        if timer <= 0:
            enemy_tanks.extend(generate_tanks(tank_count, 600, 800, 0, 600))
            wave_started = True
            
    
    # Draw Objects
    camera.clear("black")
    camera.draw(background)
    
    camera.draw(king)
    
    # Remove Dead Bullets
    for bullet in bullets:
        if not bullet.alive:
            bullets.remove(bullet)
    
    # Move Bullets 
    for bullet in bullets:
        bullet.tick()
        if bullet.touches(king):
            print("King Killed")
            gamebox.pause()
        camera.draw(bullet)
    
    # Check Barriers
    for barrier in barriers:
        barrier.check(bullets)
        barrier.draw(camera)
        
        for etank in enemy_tanks:
            barrier.check_collision(etank)
    
    # Draw Mines
    for mine in mines:
        camera.draw(mine)
    
    kills = 0
    for tank in enemy_tanks:
        if (tank.y > king.y):
            if (tank.facing > 180 - 45):
                tank.turn_right()
        else:
            if (tank.facing < 180 + 45):
                tank.turn_left()
        
        for mine in mines:
            if not mine.live:
                mines.remove(mine)
            elif tank.touches(mine):
                boom = mine.explode()
                booms.append(boom)
        
        for boom in booms:
            if tank.touches(boom):
                if tank in enemy_tanks:
                    enemy_tanks.remove(tank)
                    kills += 1
                    
    cash += int(TANK_VALUE * (kills**2))
    
    for etank in enemy_tanks:

        etank.forward() 
        etank.tick()
        
        bullet = etank.fire_bullet()
        if bullet:
            bullets.append(bullet)
        camera.draw(etank)
    
    # Draw Booms 
    for boom in booms:
        boom.tick()
        camera.draw(boom)
        if not boom.alive:
            booms.remove(boom)
        
    for b in buttons:
        b.draw(camera)
        
    # Buttons
    if camera.mouseclick:
        
        if button_state_machine.has_state():
            s = button_state_machine.state
            mx, my = camera.mousex, camera.mousey
            if s == "BARRIER":
                if cash >= tankstuff.Barrier.price:
                    cash -= tankstuff.Barrier.price
                    barriers.append(tankstuff.Barrier(mx, my, 2, 4))
            elif s == "TURRET":
                pass
            elif s == "MINE":
                # Mine cannot be place touching another mine
                if cash >= tankstuff.Mine.price:
                    new_mine = tankstuff.Mine(mx, my)
                    touching = False
                    for mine in mines:
                        if new_mine.touches(mine):
                            touching = True
                            break
                    if not touching:
                        cash -= tankstuff.Mine.price
                        mines.append(new_mine)
                    
            print(button_state_machine.state)
            button_state_machine.clear_state()
        
        else:
            for b in buttons:
                
                if b.clicked(camera):
                    if b.text == "START":
                        if timer > 0 and not wave_started:
                            timer = 0
                    else:
                        button_state_machine.set_state(b.text)
    
    if not button_state_machine.has_state():
        if pygame.K_m in keys:
            button_state_machine.set_state("MINE")
            
        elif pygame.K_b in keys:
            button_state_machine.set_state("BARRIER")
            
        elif pygame.K_k in keys:
            button_state_machine.set_state("TURRET")
    
    # Wave Compleated
    if len(enemy_tanks) == 0 and wave_started:
        wave += 1
        tank_count += 1
        score += cash
        timer = PRE_WAVE_TIME
        wave_started = False
    
    if button_state_machine.has_state():
        placing_info = gamebox.from_text(650, 10, "PLACING: " + button_state_machine.state, "arial", 
                                         25, "white", True)
        camera.draw(placing_info)
     
    score_text = gamebox.from_text(700, 575, "SCORE: " + str(score), "arial", 20, "white", bold = True)
    cash_text = gamebox.from_text(700, 555, "CASH: " + str(cash), "arial", 20, "white", bold = True)
    wave_text = gamebox.from_text(50, 10, "WAVE: " +  str(wave), "arial", 20, "white", bold = True)
    wave_timer = gamebox.from_text(400, 25, str(timer) if timer != 0 else "WAVE START!", "arial", 40, "white", bold = True)
    camera.draw(score_text)
    camera.draw(cash_text)
    camera.draw(wave_text)
    camera.draw(wave_timer)
    
    # Display
    camera.display()


# Variables
wave = 1
score = 0
cash = 100
tank_count = 1
timer = 45
tick_count = 0

wave_started = False

PRE_WAVE_TIME = 30
TANK_VALUE = 100

# Camera
camera = gamebox.Camera(800, 600)

# Images
tank_image_url = "http://www.xnaresources.com/images/tutorialimages/sprites/MulticolorTanks.png"
tank_sprite_sheet = gamebox.load_sprite_sheet(tank_image_url, 8, 8)

background_path = "background001.png"
background = gamebox.from_image(400, 300, background_path)

boom_image_url = "http://flashvhtml.com/html/img/action/explosion/Explosion_Sequence_A%2012.png"
tankstuff.Boom.image = boom_image_url

mine_image_path = "mine001.png"
tankstuff.Mine.image = mine_image_path

#Game Objects
enemy_tanks = []
friendly_tanks = []
bullets = []
barriers = []
mines = []
turrets = []
buttons = []
booms = []

# Add Objects 
button_state_machine = tankstuff.ButtonStateMachine()
barriers.append(tankstuff.Barrier(150, 150, 5, 30))
mines.append(tankstuff.Mine(400, 300))

# BUTTONS 
buttons.append(tankstuff.Button(25, 575,color = "grey", text_color = "black", text = "MINE"))
buttons.append(tankstuff.Button(75, 575, text = "TURRET"))
buttons.append(tankstuff.Button(125, 575,color = "grey", text_color = "black", text = "BARRIER"))
buttons.append(tankstuff.Button(175,575,color = "green", text_color = "black", text = "START"))

# THINGS
king = gamebox.from_color(100, 300, "yellow", 25, 25)


ticks_per_second = 60

# keep this line the last one in your program
gamebox.timer_loop(ticks_per_second, tick)