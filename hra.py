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
#objects = []

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

def distance(a, b, wrap_size):
    """Distance in one direction (x or y)"""
    result = abs(a - b)
    if result > wrap_size / 2:
        result = wrap_size - result
    return result

def overlaps(a, b):
    """Returns true iff two space objects overlap"""
    distance_squared = (distance(a.x, b.x, window.width) ** 2 +
                        distance(a.y, b.y, window.height) ** 2)
    max_distance_squared = (a.radius + b.radius) ** 2
    return distance_squared < max_distance_squared

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

    def draw_circle(self):
        x = self.x
        y = self.y
        radius = (self.sprite.height + self.sprite.width)/4

        iterations = 20
        s = math.sin(2*math.pi / iterations)
        c = math.cos(2*math.pi / iterations)

        dx, dy = radius, 0

        gl.glBegin(gl.GL_LINE_STRIP)
        for i in range(iterations+1):
            gl.glVertex2f(x+dx, y+dy)
            dx, dy = (dx*c - dy*s), (dy*c + dx*s)
        gl.glEnd()

    def delete(self):
        objects.remove(self)
        self.sprite.delete()

    # def hit_by_spaceship(self,object):
    #     print(object,'hit')

class Spaceship(SpaceObject):
    def details(self, image, batch):
        # self.window = window
        self.x = window.width //2
        self.y = window.height //2
        self.image = image
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, batch = batch)
        self.radius = (self.sprite.height + self.sprite.width)/4
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
        for object in objects:
            if type(object) == Asteroid :
                if overlaps(object,self) == True:
                    self.delete()
                    return
                    # object.hit_by_spaceship(self)
        super().tick(dt)


class Asteroid(SpaceObject):
    def details(self, image, batch):
        # self.x = 0
        # self.y = window.height //2
        self.image = image
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, batch = batch)
        self.radius = (self.sprite.height + self.sprite.width)/4
    # def hit_by_spaceship(self,object):
    #     print('hit asteroid')
    #     object.delete()
    #     super().hit_by_spaceship(object)

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
    for object in objects:
        object.draw_circle()



window.push_handlers(
    on_draw=draw,
    on_key_press=key_press,
    on_key_release=key_stop,
)
#for object in objects:
#    pyglet.clock.schedule(object.tick)

def tick_all(dt):
    for object in objects:
        object.tick(dt)

pyglet.clock.schedule(tick_all)


pyglet.app.run()
