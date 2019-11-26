import pygame
import os #vital to fix the mac issue pt1


# Global constants
 
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
bgblue = (24, 82, 156)
bgColour = (33, 46, 66)
platcol = (22, 19, 33)

# Character
widthChar = 64
heightChar = 64
gravity = 2.5
jumpHeight = -27.5
playerBehind = 13

# Get current state of character
movingLeft = False
movingRight = False
isJump = False
walkCount = 0

#Sprite for the character
char = pygame.image.load("assets/player1.png")
charDead = pygame.image.load("assets/player_dead.png")

# Background
bg = pygame.image.load("assets/bg.png")
groundTile = pygame.image.load("assets/ground_tile1.png")
bgY = 0
bgX = 0

# Game icon
gameIcon = char
pygame.display.set_icon(gameIcon)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def redrawWindow():
    global walkCount

 
class Player(pygame.sprite.Sprite):
    """
    This class represents the bar at the bottom that the player controls.
    """
 
    # -- Methods
    def __init__(self):
        """ Constructor function """
 
        # Call the parent's constructor
        super().__init__()

        global char
        # Set player to sprite image and keep alpha levels the same a png source
        self.image = char.convert_alpha()
        self.image.blit(self.image, (0, 0))
 
        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
        
        # Make player look like it's under the gras, move by a few pixels.  
        self.rect[3] -= playerBehind 
 
        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0
 
        # List of sprites we can bump against
        self.level = None
 
    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()
 
        # Move left/right
        self.rect.x += self.change_x
 
        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
 
        # Move up/down
        self.rect.y += self.change_y
 
        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
 
            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
 
            # Stop our vertical movement
            self.change_y = 0
 
    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 2
        else:
            global gravity
            self.change_y += gravity
 
        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height
 
    def jump(self):
        """ Called when user hits 'jump' button. """
 
        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down 1
        # when working with a platform moving down.
        self.rect.y += 1
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 1
 
        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            global jumpHeight
            global movingLeft
            global movingLeft
            global isJump
            global walkCount
            self.change_y = jumpHeight
            movingLeft = False
            movingRight = False 
            isJump = True
            walkCount = 0
 
    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -6
        global movingLeft, movingRight
        movingLeft = True
        movingRight = False
 
    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 6
        global movingLeft, movingRight
        movingLeft = False
        movingRight = True
 
    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0
        walkCount = 0
 
 
class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """
 
    def __init__(self, width, height):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()
        global groundTile
        self.image = pygame.Surface([width, height])
        
        self.image = groundTile.convert_alpha()
        self.image.blit(groundTile, (0, 0))

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
 
 
class Level():
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """
 
    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving
            platforms collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player
 
        # How far this world has been scrolled left/right
        self.world_shift = 0
 
    # Update everythign on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()
 
    def draw(self, screen):
        """ Draw everything on this level. """
        # Draw the background
        global bgY
        global bgX
        screen.blit(bg, (bgX, bgY))
 
        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
 
    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll
        everything: """
 
        # Keep track of the shift amount
        self.world_shift += shift_x
 
        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x
 
        for enemy in self.enemy_list:
            enemy.rect.x += shift_x
 
 
# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """
 
    def __init__(self, player):
        """ Create level 1. """
 
        # Call the parent constructor
        Level.__init__(self, player)
 
        self.level_limit = -1000
 
        # Array with width, height, x, and y of platform
        level = [[210, 70, 500, 450],
                 [210, 70, 800, 350],
                 [210, 70, 1000, 450],
                 [210, 70, 1120, 230],
                 [1000, 50, 0, SCREEN_HEIGHT-50],
                 [1200, 50, 1400, SCREEN_HEIGHT-50]
                 ]
 
        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)
 
 
# Create platforms for the level
class Level_02(Level):
    """ Definition for level 2. """
 
    def __init__(self, player):
        """ Create level 1. """
 
        # Call the parent constructor
        Level.__init__(self, player)
 
        self.level_limit = -1000
 
        # Array with type of platform, and x, y location of the platform.
        level = [[210, 90, 450, 480],
                 [210, 30, 850, 370],
                 [210, 30, 1000, 480],
                 [210, 30, 1120, 230],
                 [1000, 50, 0, SCREEN_HEIGHT-50],
                 [1200, 50, 1400, SCREEN_HEIGHT-50]
                 ]
 
        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)
 
 
def main():
    """ Main Program """
    pygame.init()
 
    # Set the height and width of the screen
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
 
    pygame.display.set_caption("Side-scrolling Platformer")
 
    # Create the player
    player = Player()
 
    # Create all the levels
    level_list = []
    level_list.append(Level_01(player))
    level_list.append(Level_02(player))
 
    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]
 
    active_sprite_list = pygame.sprite.Group()
    player.level = current_level
 
    player.rect.x = 340
    player.rect.y = 450
    active_sprite_list.add(player)
 
    # Loop until the user clicks the close button.
    done = False
 
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
 
    def game_over():

        # If game over is true, do game over action - can be further edited to add text to screen, 
        # can possibly also add a 'click enter to restart' function later
        player.image.blit(charDead , (0, 0))
    
    
    
    
    
    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_SPACE:
                    player.jump()
 
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()
 
        # Update the player.
        active_sprite_list.update()
 
        # Update items in the level
        current_level.update()
 
        # If the player gets near the right side, shift the world left (-x)
        if player.rect.right >= 500:
            diff = player.rect.right - 500
            player.rect.right = 500
            current_level.shift_world(-diff)
 
        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= 120:
            diff = 120 - player.rect.left
            player.rect.left = 120
            current_level.shift_world(diff)
 
        if player.rect.bottom == SCREEN_HEIGHT: 
            game_over() #works without the break, but break seems to happen before colour change now
            break #stops player from continuing after hitting floor
    
    
    
        # If the player gets to the end of the level, go to the next level
        current_position = player.rect.x + current_level.world_shift
        if current_position < current_level.level_limit:
            player.rect.x = 120
            if current_level_no < len(level_list)-1:
                current_level_no += 1
                current_level = level_list[current_level_no]
                player.level = current_level
 
        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        redrawWindow
        current_level.draw(screen)
        active_sprite_list.draw(screen)
 
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
 
        # Limit to 60 frames per second
        clock.tick(30)
 
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
 
    while True: #vital for mac issue pt2
        e = pygame.event.poll() 
        if e.type == pygame.QUIT:
            break
    
    
    
    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()
    os._exit(0) #vital for the mac issue pt3
    
    
if __name__ == "__main__":
    main()



# TODO

# - Read that drawing the elements on screen on the while loop is not the most efficinet way to do it. Create a function where all the code to draw should be.
# - Make player jump faster, more gravitiy needed. Feels too floaty.
# - Add momentum to player when moving.
# - Add icon to app when open.
# - Invert gravity when boots are worn.

# CHANGES
# - Jump has been changed to space.
# - Game icon changed


# https: // www.youtube.com/watch?v = UdsNBIzsmlI
