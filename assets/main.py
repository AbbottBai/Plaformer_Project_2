import pygame
import os
import copy
from random import randint

pygame.init()

clock = pygame.time.Clock()

window_width = 640
window_height = 512

window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Platform Game")

def create_background(width, height, colour_name, floor_name):
    image_path = os.path.join("background", colour_name)
    tile = pygame.image.load(image_path)
    _, _, tile_width, tile_height = tile.get_rect()
    tile_coords = []

    for i in range(height // tile_height):
        for j in range(width // tile_width):
            temp_coords = [j * tile_width, i * tile_height]
            tile_coords.append(temp_coords)
        # Renders 1 tile in x direction beyond game window
        l_coords = [0 - tile_width, i * tile_height]
        tile_coords.append(l_coords)
        r_coords = [width, i * tile_height]
        tile_coords.append(r_coords)

    # Deleting bottom row tiles and appending the grass floor.
    row_elements = width // tile_width
    for k in range(row_elements):
        tile_coords.pop(-1)

    default_coords = copy.deepcopy(tile_coords)

    image_path = os.path.join("background", floor_name)
    floor = pygame.image.load(image_path)
    _, _, floor_width, floor_height = floor.get_rect()
    floor_coords = []
    for l in range(row_elements):
        floor_coord = [(floor_width * l), (height - tile_height)]
        floor_coords.append(floor_coord)

    l_floor = [0 - tile_width, height - tile_height]
    floor_coords.append(l_floor)
    r_floor = [width, height - tile_height]
    floor_coords.append(r_floor)

    floor_default = copy.deepcopy(floor_coords)

    return (tile, tile_coords, tile_width, tile_height, floor, floor_coords,
            floor_height, default_coords, floor_default)

(tile, tile_coords, tile_width, tile_height, floor, floor_coords, floor_height, default_coords,
 floor_default) = create_background(window_width, window_height,"Brown.png",
                                    "grass.png")


class platform:
    def __init__(self, image_name):
        self.image_name = image_name
        self.image_path = os.path.join("platform", self.image_name)
        self.platform_image = pygame.image.load(self.image_path).convert_alpha()
        self.platform_rect = self.platform_image.get_rect()
        self.platform_mask = pygame.mask.from_surface(self.platform_image)
        self.length = randint(1, 6) * 32
        self.link_surface = pygame.Surface((self.length, 8))
        self.x_range = randint(-window_width, window_width * 2)
        self.y_range = randint(0, window_height - 64 * 2)
        self.coord = [self.x_range, self.y_range]

    def link(self):
        for i in range(0, self.length // 32):
            self.link_surface.blit(self.platform_image, (32 * i, 0))

    def draw(self, window):
        self.link()
        window.blit(self.link_surface, (self.coord[0], self.coord[1]))

platforms = []
for i in range(randint(5, 10)):
    platforms.append(platform("brown.png"))


def load_sprite(sprite_width, sprite_height, sheet_name, sprite_amount):
    right_sprites = []
    image_path = os.path.join("sprites", "ninja_frog", sheet_name)
    sprite_sheet = pygame.image.load(image_path).convert_alpha()
    for i in range(sprite_amount):
        sprite = sprite_sheet.subsurface((i * sprite_width), 0, sprite_width, sprite_height)
        right_sprites.append(sprite)

    return right_sprites


r_jump = load_sprite(32, 32, "jump.png", 1)
r_fall = load_sprite(32, 32, "fall.png", 1)
r_run = load_sprite(32, 32, "run.png", 12)
r_idle = load_sprite(32, 32, "idle.png", 11)

l_run = []
for i in range(len(r_run)):
    l_image = pygame.transform.flip(r_run[i], True, False)
    l_run.append(l_image)

l_idle = []
for i in range(len(r_idle)):
    idle = pygame.transform.flip(r_idle[i], True, False)
    l_idle.append(idle)

l_jump = pygame.transform.flip(r_jump[0], True, False)


class player:
    def __init__(self, x, y, width, height, velocity, l_boundary, r_boundary):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.velocity = velocity
        self.l_boundary = l_boundary
        self.r_boundary = r_boundary

        self.gravity = 1
        self.jump_vel = 20
        self.jump_height = 20
        self.left = False
        self.right = False
        self.moving = False
        self.jumping = False
        self.run_count = 0
        self.idle_count = 0
        self.left_background_shift = False
        self.right_background_shift = False
        self.movement_counter = 0

    def move_player(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            self.left_background_shift = False
            self.left = True
            self.right = False
            self.moving = True
            self.movement_counter -= self.velocity
            if self.x >= self.l_boundary:
                self.x -= self.velocity
            else:
                self.right_background_shift = True

        elif key[pygame.K_d]:
            self.right_background_shift = False
            self.left = False
            self.right = True
            self.moving = True
            self.movement_counter += self.velocity
            if self.x + self.width <= self.r_boundary:
                self.x += self.velocity
            else:
                self.left_background_shift = True

        else:
            self.moving = False
            self.left_background_shift = False
            self.right_background_shift = False

        if key[pygame.K_w]:
            self.jumping = True

        if self.jumping:
            self.y -= self.jump_vel
            self.jump_vel -= self.gravity
            if self.jump_vel < - self.jump_height:
                self.jump_vel = self.jump_height
                self.jumping = False

    def draw_player(self, window):
        self.move_player()
        if self.jumping:
            self.idle_count = 0
            self.run_count = 0
            if self.left:
                window.blit(l_jump, (self.x, self.y))
            else:
                window.blit(r_jump[0], (self.x, self.y))

        else:
            if not self.moving:
                self.run_count = 0
                if self.idle_count >= 33:
                    self.idle_count = 0

                if self.left:
                    window.blit(l_idle[self.idle_count // 3], (self.x, self.y))
                    self.idle_count += 1
                elif self.right:
                    window.blit(r_idle[self.idle_count // 3], (self.x, self.y))
                    self.idle_count += 1
                else:
                    window.blit(r_idle[self.idle_count // 3], (self.x, self.y))
                    self.idle_count += 1

            else:
                self.idle_count = 0
                if self.run_count >= 36:
                    self.run_count = 0

                if self.left:
                    window.blit(l_run[self.run_count // 3], (self.x, self.y))
                    self.run_count += 1
                elif self.right:
                    window.blit(r_run[self.run_count // 3], (self.x, self.y))
                    self.run_count += 1

man = player(window_width // 2, window_height - 64 - 32, 32,
             32, 5, 200, window_width - 200)

def display(tile, tile_coords, floor, floor_coords, window):
    for coords in tile_coords:
        window.blit(tile, coords)

    for coordinates in floor_coords:
        window.blit(floor, coordinates)

    for i in range (len(platforms)):
        platforms[i].draw(window)

    man.draw_player(window)

    pygame.display.update()


# Main game loop
run = True
render_platforms = bool
origin = man.movement_counter
chunk = 0
chunk_record = []

while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if man.left_background_shift:
        for i in range(len(tile_coords)):
            tile_coords[i][0] += -man.velocity + 3
        for i in range(len(floor_coords)):
            floor_coords[i][0] += -man.velocity

        for i in range(len(platforms)):
            platforms[i].coord[0] += -man.velocity

    elif man.right_background_shift:
        for i in range(len(tile_coords)):
            tile_coords[i][0] += man.velocity - 3
        for i in range(len(floor_coords)):
            floor_coords[i][0] += man.velocity

        for i in range (len(platforms)):
            platforms[i].coord[0] += man.velocity

    if tile_coords[0][0] <= -tile_width or tile_coords[0][0] >= tile_width:
        tile_coords.clear()
        tile_coords = copy.deepcopy(default_coords)

    if floor_coords[0][0] <= -tile_width or floor_coords[0][0] >= tile_width:
        floor_coords.clear()
        floor_coords = copy.deepcopy(floor_default)
        

    if (man.movement_counter - origin <= -window_width or man.movement_counter + origin >= window_width
            and render_platforms == False):
        render_platforms = True
    else:
        render_platforms = False

    if render_platforms:
        # Left off-screen
        platform.x_range = randint(origin - window_width * 3, origin - window_width)
        for i in range(randint(5, 10)):
            platforms.append(platform("brown.png"))
        # Right off-screen
        platform.x_range = randint(origin + window_width, origin + window_width * 3)
        for i in range(randint(5, 10)):
            platforms.append(platform("brown.png"))

        origin = man.movement_counter
        render_platforms = False

    display(tile, tile_coords, floor, floor_coords, window)


pygame.quit()
