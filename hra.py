import pyglet
from pyglet.window import key
from pyglet import gl
import math
import random

ROTATION_SPEED = 4  # radians per second
ACCELERATION = 50
LASER_SPEED = 90

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
player_image = pyglet.image.load(r'./images/playerShip3_red.png')
player_image2 = pyglet.image.load(r'./images/playerShip1_orange.png')
speed_array = [18,6,9,15,20, 40]
asteroid_big_images = [pyglet.image.load(r'./images/meteorGrey_big' + str(i) + '.png') for i in range(1,5)]
asteroid_med_images = [pyglet.image.load(r'./images/meteorGrey_med' + str(i) + '.png') for i in range(1,3)]
asteroid_small_images = [pyglet.image.load(r'./images/meteorGrey_small' + str(i) + '.png') for i in range(1,3)]
asteroid_tiny_images = [pyglet.image.load(r'./images/meteorGrey_tiny' + str(i) + '.png') for i in range(1,3)]
# asteroid_all_images = asteroid_big_images + asteroid_med_images
laser_image = pyglet.image.load(r'./images/laserRed07.png')


pressed_keys = set()
#objects = []

def key_press(symbol, modificator):
    if symbol == key.LEFT:
        pressed_keys.add('left')
    if symbol == key.RIGHT:
        pressed_keys.add('right')
    if symbol == key.UP:
        pressed_keys.add('faster')
    if symbol == key.SPACE:
        pressed_keys.add('laser')

def key_stop(symbol, modificator):
    if symbol == key.LEFT:
        pressed_keys.discard('left')
    if symbol == key.RIGHT:
        pressed_keys.discard('right')
    if symbol == key.UP:
        pressed_keys.discard('faster')
    if symbol == key.SPACE:
        pressed_keys.discard('laser')

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

    # def draw_circle(self):
    #     x = self.x
    #     y = self.y
    #     radius = (self.sprite.height + self.sprite.width)/4
    #
    #     iterations = 20
    #     s = math.sin(2*math.pi / iterations)
    #     c = math.cos(2*math.pi / iterations)
    #
    #     dx, dy = radius, 0
    #
    #     gl.glBegin(gl.GL_LINE_STRIP)
    #     for i in range(iterations+1):
    #         gl.glVertex2f(x+dx, y+dy)
    #         dx, dy = (dx*c - dy*s), (dy*c + dx*s)
    #     gl.glEnd()

    def delete(self):
        objects.remove(self)
        self.sprite.delete()

class Spaceship(SpaceObject):
    def details(self, image, batch):
        self.x = window.width //2
        self.y = window.height //2
        self.image = image
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, batch = batch)
        self.radius = (self.sprite.height + self.sprite.width)/4
        self.shoot_limit = 0.3

    def tick(self,dt):
        self.shoot_limit -= 1*dt
        if 'left' in pressed_keys:
            self.rotation = self.rotation + dt * ROTATION_SPEED
        if 'right' in pressed_keys:
            self.rotation = self.rotation - dt * ROTATION_SPEED
        if 'faster' in pressed_keys:
            self.x_speed += dt * ACCELERATION * math.cos(self.rotation)
            self.y_speed += dt * ACCELERATION * math.sin(self.rotation)
        if ('laser' in pressed_keys) and (self.shoot_limit < 0):
            self.shoot_limit = 0.3
            laser = Laser(self.x,self.y, self.rotation, self.x_speed + 1,self.y_speed + 1)
            laser.details(laser_image,batch)
            objects.append(laser)
        for object in objects:
            if type(object) == Asteroid :
                if overlaps(object,self) == True:
                    self.delete()
                    return
        super().tick(dt)


class Asteroid(SpaceObject):
    def details(self, image, batch, level):
        self.image = image
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, batch = batch)
        self.radius = (self.sprite.height + self.sprite.width)/4
        self.level = level
    def become_smaller(self):
        if self.level == 0:
            print('medium')
            image_size = random.choice(asteroid_med_images)
        elif self.level == 1:
            print('small')
            image_size = random.choice(asteroid_small_images)
        elif self.level == 2:
            print('tiny')
            image_size = random.choice(asteroid_tiny_images)
        else:
            print('nothing')
            return
        self.level += 1
        asteroid_1 = Asteroid(self.x, self.y,self.x_speed, -self.y_speed, self.rotation)
        asteroid_2 = Asteroid(self.x, self.y, -self.x_speed, self.y_speed, self.rotation)
        asteroid_1.details(image_size,batch,self.level)
        asteroid_2.details(image_size,batch,self.level)
        objects.append(asteroid_1)
        objects.append(asteroid_2)


class Laser(SpaceObject):
    def __init__(self, x, y, rotation, x_speed, y_speed):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.x_speed = LASER_SPEED * math.cos(self.rotation)
        self.y_speed = LASER_SPEED * math.sin(self.rotation)
        self.time = 0
    def details(self, image, batch):
        self.image = image
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, batch = batch)
        self.radius = (image.height)/2
    def tick(self, dt):
        self.time += dt
        if self.time >= 3:
            self.delete()
            return
        for object in objects:
            if type(object) == Asteroid :
                if overlaps(object,self) == True:
                    self.delete()
                    object.become_smaller()
                    object.delete()
                    return
        super().tick(dt)


spaceship = Spaceship(window.width //2, window.height //2,1,1,math.pi/2)
spaceship.details(player_image,batch)
asteroid1 = Asteroid(window.width //2, 50, random.choice(speed_array),random.choice(speed_array),0)
asteroid1.details(random.choice(asteroid_big_images),batch,0)
asteroid2 = Asteroid(50, window.height //2, random.choice(speed_array),-random.choice(speed_array),0)
asteroid2.details(random.choice(asteroid_big_images),batch,0)


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
    # for object in objects:
    #     object.draw_circle()



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
