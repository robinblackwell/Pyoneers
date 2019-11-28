import pygame
import os  # vital to fix the mac issue pt1

# Global variables
FPS = 40
levelLimit = -1000

# Character
gravity = 4
jumpHeight = -27.5
playerBehind = 9
playerVel = 8

# Get current state of character
movingLeft = False
movingRight = False
isJumpRight = False
isJumpLeft = False
standing = True

isJump = False
walkCount12 = 0
walkCount2 = 0



def getImage(source):
    return pygame.image.load("assets/{}".format(source))


# Player sprites
charRight = [getImage("playerRight.png"), getImage("playerRight2.png")]
charLeft = [getImage("playerLeft.png"), getImage("playerLeft2.png")]
charStanding = [getImage("playerStanding1.png"), getImage("playerStanding2.png"), getImage("playerStanding3.png"), getImage("playerStanding4.png"), getImage(
    "playerStanding2.png"), getImage("playerStanding5.png"), getImage("playerStanding1.png"), getImage("playerStanding2.png"), getImage("playerStanding3.png"),getImage("playerStanding1.png"), getImage("playerStanding2.png"), getImage("playerStanding3.png")]
charJump = getImage("playerJump.png")
charDead = getImage("playerDead.png")
jumpRight = getImage("jumpRight.png")
jumpLeft = getImage("jumpLeft.png")

# Background
bg = getImage("bg.png")
groundTileTop = getImage("ground/groundTile_top.png")
groundTileInner = getImage("ground/groundTile_inner.png")
groundTileCorner = getImage("ground/groundTile_corner.png")

boot1 = getImage("boot/boot1.png")
house = getImage("house.png")

vine = getImage("vine.png")
noticeBoard = getImage("noticeBoard.png")
portal = getImage("portal.png")
bgY = 0
bgX = 0

# Game icon
gameIcon = getImage("icon.png")
pygame.display.set_icon(gameIcon)

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 640

pygame.init()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])


class Player(pygame.sprite.Sprite):
    """
    This class represents the bar at the bottom that the player controls.
    """

    def __init__(self):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        # Set player to sprite image and keep alpha levels the same a png source
        self.image = charStanding[0].convert_alpha()

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
        

        # Make player look like it's under the grassZ, move by a few pixels.
        self.rect[3] -= playerBehind

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.level = None

    def update(self):
        # Gravity
        self.calc_grav()

        global isJumpLeft
        global isJumpRight

        # Move left/right
        self.rect.x += self.change_x

        # See if we hit anything
        blocklist = pygame.sprite
        block_hit_list = blocklist.spritecollide(
            self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right, set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = blocklist.spritecollide(
            self, self.level.platform_list, False)
        for block in block_hit_list:
            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
            # Stop our vertical movement
            self.change_y = 0
            # Set direction of sprite on landing on a surface
            isJumpLeft = False
            isJumpRight = False
            

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
        #  Called when user hits 'jump' button.
        global jumpHeight
        global movingLeft
        global movingRight
        global standing
        global isJumpRight
        global isJumpLeft
        global walkCount12
        global walkCount2

        # TODO Needed???
        # move down a bit and see if there is a platform below us. Move down 2 pixels because it doesn't work well if we only move down 1 when working with a platform moving down.
        self.rect.y += 1
        platform_hit_list = pygame.sprite.spritecollide(
            self, self.level.platform_list, False)
        self.rect.y -= 1
    
        # TODO Needed???
        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            
            self.change_y = jumpHeight
        
        # Set player animation for when jumping 
            # if movingLeft:
            #     isJumpLeft = True
            # elif movingRight:
            #     isJumpRight = True
            # movingLeft = False
            # movingRight = False
            standing = False
            walkCount12 = 0
            walkCount2 = 0

    # Player-controlled movement:
    def go_left(self):
        # Called when the user hits the left arrow.
        global movingLeft, movingRight, standing
        self.change_x = -playerVel
        movingLeft = True
        movingRight = False
        standing = False

    def go_right(self):
        # Called when the user hits the right arrow.
        global movingLeft, movingRight, standing
        self.change_x = playerVel
        movingRight = True
        movingLeft = False
        standing = False

    def stop(self):
        # Called when the user lets off the keyboard.
        global movingLeft, movingRight, standing, walkCount12, walkCount2, isJumpLeft, isJumpRight
        self.change_x = 0
        movingLeft = False
        movingRight = False
        isJumpRight = False
        isJumpLeft = False
        standing = True
        walkCount12 = 0
        walkCount2 = 0

class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """

    def __init__(self, tileType):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()
        self.tileType = tileType
        self.image = self.tileType.convert_alpha()
        self.image.blit(self.tileType, (0, 0))

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

    def drawBg(self, screen):
        """ Draw background """
        global bgY
        global bgX
        screen.blit(bg, (bgX, bgY))
        
    def drawLevel(self, screen):
        """ Draw everything on this level. """
        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        # self.enemy_list.draw(screen)

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

        self.level_limit = levelLimit

    # Array with width, height, x, and y of platform
        # level = [[210, 70, 500, 450],
        #          [210, 70, 800, 350],
        #          [210, 70, 1000, 450],
        #          [210, 70, 1120, 230],
        #          [1000, 50, 0, SCREEN_HEIGHT-50],
        #          [1200, 50, 1400, SCREEN_HEIGHT-50]
        #          ]

        # Go through the array above and add platforms
        # for platform in level:
        #     block = Platform(groundTile)
        #     # block.rect.x = block.image.get_rect().x
        #     # block.rect.y = block.image.get_rect().y
        #     block.rect.x = platform[2]
        #     block.rect.y = platform[3]
        #     block.player = self.player
    #     self.platform_list.add(block)
        
        levelLayout = [ [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7, 1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],
                        
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],

                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],
                        
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,],
                        
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,],
                        
                        [0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,],
                        
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.2, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,],
                        
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.5, 1.6, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],
                        
                        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.3, 0.0, 1.5, 1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3,
                         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, .0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,],
                        
                        [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3,
                         0.0, 0.0, 1.1, 1.0, 1.0, 1.2, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ]
        ]

        def updateLevelImages(classType, imageToUpdate):
            block = classType(imageToUpdate)
            block.rect.x += x
            block.rect.y += y
            self.platform_list.add(block)

        y = 0
        for platform in levelLayout:
            x = 0
            for tile in platform:
                if tile == 1:
                    updateLevelImages(Platform, groundTileTop,)
                elif tile == 1.1:
                    updateLevelImages(Platform, groundTileCorner)
                elif tile == 1.2:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, True, False))
                elif tile == 1.3:
                    updateLevelImages(Platform, pygame.transform.rotate(groundTileTop, -90))
                elif tile == 1.4:
                    updateLevelImages(Platform, pygame.transform.rotate(groundTileTop, 90))
                elif tile == 1.5:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, False, True))
                elif tile == 1.6:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, True, True))
                elif tile == 1.7:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileTop, False, True))
                elif tile == 2:
                    updateLevelImages(Platform, groundTileInner)
                elif tile == 3:
                    updateLevelImages(Platform, noticeBoard)
                elif tile == 4:
                    updateLevelImages(Platform, portal)
                elif tile == 5:
                    updateLevelImages(Platform, vine)
                elif tile == 6:
                    updateLevelImages(Platform, boot1)
                elif tile == 7:
                    updateLevelImages(Platform, house)
                x += 64
            y += 64



# Create platforms for the level
class Level_02(Level):
    """ Definition for level 2. """

    def __init__(self, player):
        """ Create level 2. """

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
            block = Platform(platform[0], platform[1], groundTile)
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)



def main():

    # Game settings
    # Loop until the user clicks the close button.
    done = False
    clock = pygame.time.Clock()
    pygame.display.set_caption("Pyoneers")

    # Create the player
    player = Player()

    # Create all the levels
    level_list = []
    level_list.append(Level_01(player))
    # level_list.append(Level_02(player))

    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = 450
    active_sprite_list.add(player)

    # Displays objects
    def redrawWindow():

        animatePlayer()
        # Define what is drwan on screen
        current_level.drawBg(screen)
        active_sprite_list.draw(screen)
        current_level.drawLevel(screen)
        
        # Update items in the level
        current_level.update()
        active_sprite_list.update()
        pygame.display.flip()

    def animatePlayer():
        global walkCount12
        global walkCount2
        if walkCount12 + 1 >= 28:
            walkCount12 = 0
        elif walkCount2 + 1 >=7:
            walkCount2 = 0

        def setImage(newImage):
            player.image = newImage.convert_alpha()

        if movingLeft:
            setImage(charLeft[walkCount2//3])
            walkCount2 += 1
        elif movingRight:
            setImage(charRight[walkCount2//3])
            walkCount2 += 1
        elif isJumpLeft:
            setImage(jumpLeft)
        elif isJumpRight:
            setImage(jumpRight)
        elif standing:
            setImage(charStanding[walkCount12//3])
            walkCount12 += 1

    # TODO - remove duplication
    def moveCam(rightShift, leftShift):
        if player.rect.right >= rightShift:
            diff = player.rect.right - rightShift
            player.rect.right = rightShift
            current_level.shift_world(-diff)
        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= leftShift:
            diff = leftShift - player.rect.left
            player.rect.left = leftShift
            current_level.shift_world(+diff)

    def userEvents():
        global movingRight
        global movingLeft
        global standing
        global walkCount12
        global walkCount2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                   player.go_left()
                elif event.key == pygame.K_RIGHT:
                   player.go_right()
                elif event.key == pygame.K_SPACE:
                   player.jump()
                else:
                    movingLeft = False
                    movingRight = False
                    standing = True
                    walkCount12 = 0
                    walkCount2 = 0

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                   player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                   player.stop()

    # Define what happens when player dies
    def game_over():
        player.image.blit(charDead, (0, 0))

    # -------- Main Program Loop -----------
    while not done:
        
        if player.rect.bottom == SCREEN_HEIGHT:
            game_over()
            pygame.quit()
            break

        # If the player gets to the end of the level, go to the next level
        # current_position = player.rect.x + current_level.world_shift
        # if current_position < current_level.level_limit:
        #     player.rect.x = 120
        #     if current_level_no < len(level_list)-1:
        #         current_level_no += 1
        #         current_level = level_list[current_level_no]
        #         player.level = current_level


        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        userEvents()
        clock.tick(FPS)
        # pygame.time.delay(28)
        moveCam(500, 120)
        redrawWindow()
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    
    # vital for mac issue pt2
    while True:
        e = pygame.event.poll()
        if e.type == pygame.QUIT:
            break
    
    # vital for the mac issue pt3
    pygame.quit()
    os._exit(0) 


if __name__ == "__main__":
    main()


# TODO
# - Add boots to game.
# - Invert gravity when boots are worn.
# - Add parallax effect to BG.
# TO ANIMATE:
    # - Glowing portal 
    # - Being spit out of portal 
    # - Vine moving 
    # - Fireflies
    # - House house


# https: // www.youtube.com/watch?v = UdsNBIzsmlI
# https: // www.youtube.com/watch?v = HCWI2f7tQnY
