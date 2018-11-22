import pyglet
from pyglet.window import key
from pyglet import gl
import math
import random

ROTATION_SPEED = 4  # radians per second
ACCELERATION = 50

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
player_image = pyglet.image.load(r'./images/playerShip3_red.png')
player_image2 = pyglet.image.load(r'./images/playerShip1_orange.png')
speed_array = [18,6,9,15,20, 40]
asteroid_big_images = [pyglet.image.load(r'./images/meteorGrey_big' + str(i) + '.png') for i in range(1,5)]
asteroid_med_images = [pyglet.image.load(r'./images/meteorGrey_med' + str(i) + '.png') for i in range(1,3)]
asteroid_small_images = [pyglet.image.load(r'./images/meteorGrey_small' + str(i) + '.png') for i in range(1,3)]
asteroid_tiny_images = [pyglet.image.load(r'./images/meteorGrey_tiny' + str(i) + '.png') for i in range(1,3)]
asteroid_all_images = asteroid_big_images + asteroid_med_images

pressed_keys = set()

def key_press(symbol, modificator):
    if symbol == key.LEFT:
        pressed_keys.add('left')
    if symbol == key.RIGHT:
        pressed_keys.add('right')
    if symbol == key.UP:
        pressed_keys.add('faster')

def key_stop(symbol, modificator):
    if symbol == key.LEFT:
        pressed_keys.discard('left')
    if symbol == key.RIGHT:
        pressed_keys.discard('right')
    if symbol == key.UP:
        pressed_keys.discard('faster')


class SpaceObject:
    def __init__(self, x, y, x_speed, y_speed, rotation):
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.rotation = rotation

    def tick(self, dt):
        self.y = self.y + dt * self.y_speed
        self.x = self.x + dt * self.x_speed
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.rotation = 90 - math.degrees(self.rotation)
        if self.x > window.width:
            self.x = 0
        if self.x < 0:
            self.x = window.width
        if self.y > window.height:
            self.y = 0
        if self.y < 0:
            self.y = window.height
        # moving sprite at the beginning of the window when it reaches the end of it

class Spaceship(SpaceObject):
    def details(self, image, batch):
        # self.window = window
        self.x = window.width //2
        self.y = window.height //2
        self.image = image
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, batch = batch)
        # self.sprite.x_speed = self.x_speed
        # self.sprite.y_speed = self.y_speed

    def tick(self,dt):
        if 'left' in pressed_keys:
            self.rotation = self.rotation + dt * ROTATION_SPEED
        if 'right' in pressed_keys:
            self.rotation = self.rotation - dt * ROTATION_SPEED
        if 'faster' in pressed_keys:
            self.x_speed += dt * ACCELERATION * math.cos(self.rotation)
            self.y_speed += dt * ACCELERATION * math.sin(self.rotation)
        super().tick(dt)


class Asteroid(SpaceObject):
    def details(self, image, batch):
        # self.x = 0
        # self.y = window.height //2
        self.image = image
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, batch = batch)

spaceship = Spaceship(window.width //2, window.height //2,1,1,math.pi/2)
spaceship.details(player_image,batch)
# spaceship2 = Spaceship(window.width /4, window.height /4,1,1,math.pi/4)
# spaceship2.details(player_image2,batch)
asteroid1 = Asteroid(window.width //2, 50, random.choice(speed_array),random.choice(speed_array),0)
asteroid1.details(random.choice(asteroid_big_images),batch)
asteroid2 = Asteroid(50, window.height //2, random.choice(speed_array),-random.choice(speed_array),0)
asteroid2.details(random.choice(asteroid_big_images),batch)


objects = [
    spaceship,
    asteroid1,
    asteroid2,
]

def draw():
    window.clear()
    for x_offset in (-window.width, 0, window.width):
        for y_offset in (-window.height, 0, window.height):
            # Remember the current state
            gl.glPushMatrix()
            # Move everything drawn from now on by (x_offset, y_offset, 0)
            gl.glTranslatef(x_offset, y_offset, 0)
            # Draw
            batch.draw()
            # Restore remembered state (this cancels the glTranslatef)
            gl.glPopMatrix()

    # batch.draw()

window.push_handlers(
    on_draw=draw,
    on_key_press=key_press,
    on_key_release=key_stop,
)
for object in objects:
    pyglet.clock.schedule(object.tick)
pyglet.app.run()
