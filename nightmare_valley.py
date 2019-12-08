import pygame
import os  # vital to fix the mac issue pt1
from moviepy.editor import VideoFileClip #Module needed to play video.

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 640

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

clock = pygame.time.Clock()
pygame.display.set_caption("Pyoneers")

def getImage(source):
    return pygame.image.load("assets/{}".format(source))

def playVideo(videoToPlay):
    global play
    if play:
        videoToPlay.preview()
        play = False
    else:
        pass

# Global variables
FPS = 40
levelLimit = -1000

# Character
gravity = 4
gravityIsNegative = False
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

font = pygame.font.Font("assets/PressStart2P.ttf", 26)

text = "You Died. Press 'r' to restart, "
# text = font.render("You Died. Press 'r' to restart, ", True, (0, 128, 0))
text1_1 = font.render("or 'q' to quit.", True, (0, 128, 0))
text2 = font.render("Welcome. Please click to start", True, (0, 128, 0))
text3 = font.render("Paused. Press 'p' to unpause", True, (0, 128, 0))
welcomeText = "ps. Press spacebar to jump."
bootsText = "ps. Press 'a' to invert gravity."
noText = ""
currentText = text

strList = [welcomeText, bootsText]

introOn = True

bgMusic = "assets/audio/bg_music.ogg"
clip = VideoFileClip("assets/intro_game.mp4")
play = False

# Player sprites
charRight = [getImage("playerRight.png"), getImage("playerRight2.png")]
charLeft = [getImage("playerLeft.png"), getImage("playerLeft2.png")]
charStanding = [getImage("playerStanding1.png"), getImage("playerStanding2.png"), getImage("playerStanding3.png"), getImage("playerStanding4.png"), getImage("playerStanding2.png"), getImage(
    "playerStanding5.png"), getImage("playerStanding1.png"), getImage("playerStanding2.png"), getImage("playerStanding3.png"), getImage("playerStanding1.png"), getImage("playerStanding2.png"), getImage("playerStanding3.png")]
charJump = getImage("playerJump.png")
charDead = getImage("playerDead.png")
jumpRight = getImage("jumpRight.png")
jumpLeft = getImage("jumpLeft.png")

# Background
menuBg = getImage("menu_bg.png")
currentBg = menuBg
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


class Player(pygame.sprite.Sprite):
    """
    This class represents the player.
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
        self.rect[2] -= playerBehind

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

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

    def invertGravity(self):
        global gravity
        global gravityIsNegative

        if not gravityIsNegative:
            gravity = -4
            gravityIsNegative = True
        elif gravityIsNegative:
            gravity = +4
            gravityIsNegative = False

    def jump(self):
        #  Called when user hits 'jump' button.
        global jumpHeight, movingLeft, movingRight, standing, isJumpRight, isJumpLeft, walkCount12, walkCount2

        # move down a bit and see if there is a platform below us. Move down 2 pixels because it doesn't work well if we only move down 1 when working with a platform moving down.
        self.rect.y += 1
        platform_hit_list = pygame.sprite.spritecollide(
            self, self.level.platform_list, False)
        self.rect.y -= 1

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = jumpHeight
            # Set player animation when jumping
            if movingLeft:
                isJumpLeft = True
            elif movingRight:
                isJumpRight = True
            walkCount12 = 0
            walkCount2 = 0

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
        
        def spriteGroup():
            return pygame.sprite.Group()

        self.platform_list = spriteGroup()
        self.item_list = spriteGroup()
        self.item_message_list1 = spriteGroup()
        self.item_message_list2 = spriteGroup()

        self.spriteList = [
            self.item_message_list1,
            self.item_message_list2,
            self.platform_list,
            self.item_list,
        ]

        self.message_list = [
            self.item_message_list1,
            self.item_message_list2,
        ]

        self.player = player

        # How far this world has been scrolled left/right
        self.world_shift = 0

    # Update everythign on this level
    def update(self):
        """ Update everything in this level."""
        for i in range(len(self.spriteList)):
            self.spriteList[i].update()
            self.spriteList[i].draw(screen)

    def drawBg(self, whatBg, screen):
        """ Draw background """
        global bgY
        global bgX
        screen.blit(whatBg, (bgX, bgY))
        
    def drawText(self):
        """ Draw background """
        global currentText

        def text_objects():
            textSurface = font.render(currentText, False, (255, 255, 255))
            return textSurface, textSurface.get_rect()
        
        text_objects()
        
        TextSurf, TextRect = text_objects()
        TextRect.center = ((SCREEN_WIDTH/2), (SCREEN_HEIGHT/2))
        screen.blit(TextSurf, TextRect)
        print(TextRect, TextSurf)

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll
        everything: """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for i in range(len(self.spriteList)):
            for item in self.spriteList[i]: 
             item.rect.x += shift_x


# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.level_limit = levelLimit

        levelLayout = [
            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7, 1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],

            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],

            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5, 1.7, 1.7, 1.7, 1.7, 1.7, 1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],

            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],

            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],

            [
                0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7, 1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],

            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.2, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],

            [
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.5, 1.6, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],

            [
                1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.3, 0.0, 1.5, 1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],

            [
                1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 1.1, 1.0, 1.0, 1.2, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 1.1, 1.0, 1.0, 1.2, 0.0, 1.1, 1.0, 1.2, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ]
        ]

        def updateLevelImages(classType, imageToUpdate, spriteList):
            block = classType(imageToUpdate)
            block.rect.x += x
            block.rect.y += y
            spriteList.add(block)

        y = 0
        for platform in levelLayout:
            x = 0
            for tile in platform:
                if tile == 1:
                    updateLevelImages(Platform, groundTileTop, self.platform_list)
                elif tile == 1.1:
                    updateLevelImages(Platform, groundTileCorner, self.platform_list)
                elif tile == 1.2:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, True, False), self.platform_list)
                elif tile == 1.3:
                    updateLevelImages(Platform, pygame.transform.rotate(groundTileTop, -90), self.platform_list)
                elif tile == 1.4:
                    updateLevelImages(Platform, pygame.transform.rotate(groundTileTop, 90), self.platform_list)
                elif tile == 1.5:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, False, True), self.platform_list)
                elif tile == 1.6:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, True, True), self.platform_list)
                elif tile == 1.7:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileTop, False, True), self.platform_list)
                elif tile == 2:
                    updateLevelImages(Platform, groundTileInner, self.platform_list)
                elif tile == 3:
                    updateLevelImages(Platform, noticeBoard, self.item_message_list1)
                elif tile == 4:
                    updateLevelImages(Platform, portal, self.item_list)
                elif tile == 4.1:
                    updateLevelImages(Platform, pygame.transform.rotate(portal, 90), self.platform_list)
                elif tile == 5:
                    updateLevelImages(Platform, vine, self.item_list)
                elif tile == 6:
                    updateLevelImages(Platform, boot1, self.item_message_list2)
                elif tile == 7:
                    updateLevelImages(Platform, house, self.item_list)
                x += 64
            y += 64


def main():

    # Displays objects
    def redrawWindow():
        global introOn
        global strList

        # Shows intro screen
        if introOn:
            current_level.drawBg(menuBg, screen)

        # Shows game level    
        if not introOn:
            animatePlayer()
            # Define what is drwan on screen
            current_level.drawBg(currentBg, screen)
            for i in range(len(strList)):
                showMessage(current_level.message_list[i], strList[i])

            active_sprite_list.draw(screen)

            # Update items in the level
            current_level.update()
            active_sprite_list.update()
        
        pygame.display.flip()

    def animatePlayer():
        global walkCount12
        global walkCount2
        if walkCount12 + 1 >= 28:
            walkCount12 = 0
        elif walkCount2 + 1 >= 7:
            walkCount2 = 0

        def setImage(newImage):
            player.image = newImage.convert_alpha()

        if movingLeft and not gravityIsNegative:
            setImage(charLeft[walkCount2//3])
            walkCount2 += 1
        elif movingRight and not gravityIsNegative:
            setImage(charRight[walkCount2//3])
            walkCount2 += 1
        elif isJumpLeft:
            setImage(jumpLeft)
        elif isJumpRight:
            setImage(jumpRight)
        elif gravityIsNegative:
            setImage(pygame.transform.flip(
                charStanding[walkCount12//3], False, True))
        elif gravityIsNegative and movingLeft:
            setImage(pygame.transform.flip(
                charLeft[walkCount2//3], False, True))
        elif gravityIsNegative and movingRight:
            setImage(pygame.transform.flip(
                charRight[walkCount2//3], False, True))
        elif standing:
            setImage(charStanding[walkCount12//3])
            walkCount12 += 1

    def playSound(soundToPlay):
        if pygame.mixer.music.get_busy():
            pass
        else:
            pygame.mixer.music.load(soundToPlay)
            pygame.mixer.music.play()

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
                elif event.key == pygame.K_RETURN:
                   player.jump()
                elif event.key == pygame.K_a:
                   player.invertGravity()
                   player.jump()
                elif event.key == pygame.K_r: #respawn function by calling the main loop over current scenario
                   main()
                elif event.key == pygame.K_q: # quit function
                    pygame.quit()
                    os._exit(0)
                elif event.key == pygame.K_p:
                    pause()
                    unpause()
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

    def pause(): # a simple pause function to allow the player to temporarily stop the game

        currentBg.fill((95, 95, 55))
        currentBg.blit(text3,
        (420 - text3.get_width() // 2, 240 - text3.get_height() // 2))

        redrawWindow()

    def unpause():
        
        global bg
        
        paused = True
        
        while paused == True:
            
            for event in pygame.event.get():  
              if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    bg = getImage("bg.png")
                    redrawWindow()
                    player.stop()
                    paused = False  
                elif event.key == pygame.K_q:
                    pygame.quit()
                    os._exit(0)
                else:
                   pass

    def showMessage(message, text):
        global bg
        global currentBg
        global currentText
        global noText
        global play
        
        # location based event put with other location based events
        for i in message:
            if player.rect.right > (i.rect.x - 100) and player.rect.right < (i.rect.x + 100):
                currentText = text
                current_level.drawText()
            else:
                currentText = noText

    # Define what happens when player dies
    def game_over():
        player.image.blit(charDead, (0, 0))
        currentBg.fill((100, 100, 100))
        currentBg.blit(text,
                (500 - text.get_width() // 2, 240 - text.get_height() // 2))
        currentBg.blit(text1_1,
                (500 - text1_1.get_width() // 2, 340 - text.get_height() // 2))

    def game_over2():

        global bg

        over = True

        while over == True:

            for event in pygame.event.get():
              if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    bg = getImage("bg.png")
                    redrawWindow()
                    main()
                    over = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    os._exit(0)
                else:
                   continue
    
    # Intro screen for when you boot up the game
    def gameIntro(): 
        global bg
        global currentBg
        global menuBg
        global play
        global introOn

        if introOn:
            currentBg = menuBg
            current_level.drawBg(currentBg, screen)
            # Checks screen is clicked  
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                        bg = getImage("bg.png")
                        introOn = False
                        play = True
                        currentBg = bg

    
    # Loop until the user clicks the close button.
    done = False

    # Create the player
    player = Player()

    # Create all the levels
    level_list = Level_01(player)

    # Set the current level
    current_level = level_list

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = 450
    active_sprite_list.add(player)

    # -------- Main Program Loop -----------
    while not done:
        
        gameIntro()

        # print(Level_01(player).item_list.)

        if player.rect.bottom == SCREEN_HEIGHT or player.rect.bottom <= 0:
            game_over()
            redrawWindow()
            game_over2()

        userEvents()
        clock.tick(FPS)
        moveCam(500, 120)
        playVideo(clip)
        playSound(bgMusic)
        # showMessage(current_level.message_list, welcomeText)
        # showMessage(current_level.item_message_list2, bootsText)
        redrawWindow()

    # # vital for mac issue pt2
    # while True:
    #     e = pygame.event.poll()
    #     if e.type == pygame.QUIT:
    #         break

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
        # - House smoke
    # https://www.youtube.com/watch?v=UdsNBIzsmlI
