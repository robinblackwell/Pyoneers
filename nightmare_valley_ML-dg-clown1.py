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
FPS = 24
levelLimit = -1000

# Character
gravity = 2.5
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
last_enemy = 0
kill_count = 0

fontMedium = pygame.font.Font("assets/IBMPlexSerif-Medium.ttf", 22)
font = pygame.font.Font("assets/IBMPlexSerif-Bold.ttf", 24)
fontPressStart = pygame.font.Font("assets/PressStart2P.ttf", 26)

text = font.render("You Died. Press 'r' to restart, ", True, (0, 128, 0))
text1_1 = font.render("or 'q' to quit.", True, (0, 128, 0))
text2 = font.render("Welcome. Please click to start", True, (0, 128, 0))
text3 = font.render("Paused. Press 'p' to unpause", True, (0, 128, 0))
welcomeText1 = "Welcome to Nightmare Valley, the place where nightmares are manufactured."
welcomeText2 = "We hope you have a horrible visit <3."
welcomeText3 = "ps.  Press spacebar to jump."
bootsText = "ps2.  Press 'a' to invert gravity."
noText = ""
currentText = text

strList = [
    welcomeText1, welcomeText2, welcomeText3, bootsText
    ]

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
groundTile_platform = getImage("ground/groundTile_platform.png")

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
        self.direction = 1
        self.hasBoot = False

    def update(self):
        # Gravity
        self.calc_grav()

        global isJumpLeft
        global isJumpRight

        # Move left/right
        self.rect.x += self.change_x

        # See if we hit anything
        blocklist = pygame.sprite
        block_hit_list = blocklist.spritecollide(self, self.level.platform_list, False)

        for block in block_hit_list:
            # If we are moving right, set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
        
#        for block in block_hit_list:
#            # If we are moving right, set our right side to the left side of the item we hit
#            if block.change_x < 0:
#                self.rect.right = block.rect.left
#            elif block.change_x > 0:
#                # Otherwise if we are moving left, do the opposite.
#                self.rect.left = block.rect.right
        
        boot_hit = blocklist.spritecollide(self, self.level.boot_list, False)
        for boot in boot_hit:
            boot.kill()
            self.hasBoot = True

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = blocklist.spritecollide(self, self.level.platform_list, False)

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
    
#        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
#        for enemy in enemy_hit_list:
#            if enemy.rect.top > self.rect.bottom - 40:
#                enemy.kill()
#                self.change_y = -20
                
#        block_hit_list = blocklist.spritecollide(self, self.level.platform_list, False)
#
#        for block in block_hit_list:
#            # Reset our position based on the left/right of the object.
#            if block.change_x < 0:
#                self.rect.right = block.rect.left
#            else:
#                # Otherwise if we are moving left, do the opposite.
#                self.rect.left = block.rect.right
#        
#        block_hit_list = blocklist.spritecollide(self, self.level.platform_list, False)
#
#        for block in block_hit_list:
#            if block.change_x != 0:
#                if block.change_y < 0:
#                    self.rect.bottom = block.rect.top
#                else:
#                    self.rect.top = block.rect.bottom
#        
#        block_hit_list = blocklist.spritecollide(self, self.level.platform_list, False)
#
#        for block in block_hit_list:
#            if self.rect.bottom == block.rect.top:
#                self.change_x += block.rect.x
                
        block_hit_list = blocklist.spritecollide(self, self.level.platform_list, False)                

        for block in self.level.platform_list:
            cur_pos_y = block.rect.y + self.level.world_shift_y
            if cur_pos_y > block.boundary_bottom or cur_pos_y < block.boundary_top:
                block.change_y *= -1
     
            cur_pos_x = block.rect.x - self.level.world_shift_x
            if cur_pos_x < block.boundary_left or cur_pos_x > block.boundary_right:
                block.change_x *= -1

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
            
        # See if we are on a ladder.
        if pygame.sprite.spritecollide(self, self.level.ladder_list, False):
            if self.change_y == 0: # Change this if you want to cling on to the ladder
                self.change_y = 1

    def invertGravity(self):
        global gravity
        global gravityIsNegative
        
        if self.hasBoot == True:
            gravity *= -1
            if not gravityIsNegative:
                gravityIsNegative = True
                self.jump()
            elif gravityIsNegative:
                gravityIsNegative = False
        else:
            pass

    def jump(self):
        #  Called when user hits 'jump' button.
        global jumpHeight, movingLeft, movingRight, standing, isJumpRight, isJumpLeft, walkCount12, walkCount2

        # move down a bit and see if there is a platform below us. Move down 2 pixels because it doesn't work well if we only move down 1 when working with a platform moving down.
        self.rect.y += 1
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 1

            # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = jumpHeight
            # Set player animation for when jumping 
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
        self.direction = -1
        movingLeft = True
        movingRight = False
        standing = False

    def go_right(self):
        # Called when the user hits the right arrow.
        global movingLeft, movingRight, standing
        self.change_x = playerVel
        self.direction = 1
        movingRight = True
        movingLeft = False
        standing = False
        
    def go_up(self):
        global movingLeft, movingRight, standing, walkCount12, walkCount2, isJumpLeft, isJumpRight
        self.change_y = -playerVel*2.5
#        movingLeft = False
#        movingRight = False
#        isJumpRight = False
#        isJumpLeft = False
#        standing = True
#        walkCount12 = 0
#        walkCount2 = 0

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
        

class Projectile(pygame.sprite.Sprite): # basic projectile class
    
    def __init__(self,direction): #taken as player x and y so projectile fires from their position
        
        super().__init__()
        
        self.image = pygame.Surface([10,10]) # surface, colour,( x, y, width, height)
        self.image.fill((0, 0, 0))
        
        self.rect = self.image.get_rect()
        
        self.change_x = direction * 10
        
    def update(self):
        self.rect.x += self.change_x


class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """
         
    def __init__(self, tileType, x = 0, y = 0, boundary_left = 0, boundary_right = 0, boundary_top = 0, boundary_bottom = 0, change_x = 0, change_y = 0):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()
        self.tileType = tileType
        self.image = self.tileType.convert_alpha()
        self.image.blit(self.tileType, (0, 0))
        
        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
        
        self.boundary_top = boundary_top
        self.boundary_bottom = boundary_bottom
        self.boundary_left = boundary_left
        self.boundary_right = boundary_right
        
        self.change_x = change_x
        self.change_y = change_y
        
        self.rect.x += x
        self.rect.y += y
    
    def update(self):

        # Move left/right/up/down
        self.rect.x += self.change_x
        self.rect.y += self.change_y


class Enemy(pygame.sprite.Sprite):
    
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

        # move down a bit and see if there is a platform below us. Move down 2 pixels because it doesn't work well if we only move down 1 when working with a platform moving down.
        self.rect.y += 1
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 1
    
            # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = jumpHeight
            # Set player animation for when jumping
            
class Enemy01(Enemy):

    # Set speed vector of enemy
    change_x = 0
    change_y = 0
    
    def update(self):
        """ Move the enemy. """
        # Gravity
        self.calc_grav()
 
        # Move left/right
        if self.player.rect.x < self.rect.x:
            self.change_x = -playerVel/2
        if self.player.rect.x > self.rect.x:
            self.change_x = playerVel/2
        if self.player.rect.x == self.rect.x:
            self.change_x = 0
        
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
 
        # Jump up platform if player above
#        if self.player.rect.bottom + 50 < self.rect.bottom:
#            for platform in self.level.platform_list:
#                if ((((self.rect.x + 10) == platform.rect.x-50) and self.change_x > 0) or (((self.rect.x + 10) == platform.rect.x+platform.image.get_size()[0]+50) and self.change_x < 0)) and (self.rect.y < platform.rect.y+150):
#                    self.jump()
    
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
            

class Enemy02(Enemy):

    # Set speed vector of enemy
    change_x = -4
    change_y = 0
    
    def update(self):
        """ Move the enemy. """
        # Gravity
        self.calc_grav()
        
        self.rect.x += self.change_x
        
        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
                self.change_x *= -1
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
                self.change_x *= -1
        
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
            
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if block.edge == True:
                self.change_x *= -1
                
class Enemy03(Enemy):

    # Set speed vector of enemy
    change_x = 0
    change_y = 0
    
    def updateAI(self,predictedVelocityx,predictedVelocityy) : #(3) updateAI gives paddle a new position when called
        self.change_x = predictedVelocityx
        if predictedVelocityy-2 < 0: #One possibility for jumping is this 'if' clause
            self.jump()
        #self.change_y = predictedVelocityy-3 #Another possibility for jumping
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
        
        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        for enemy in enemy_hit_list:
            if enemy.rect.top > self.rect.bottom - 20:
                enemy.kill()
                self.points += 100
                self.change_y = -5
    
    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -8
        self.direction = -1
 
    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 8
        self.direction = 1
        
    def go_up(self):
        self.change_y = -6
        
    def go_down(self):
        self.change_y = 6
 
    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0


class Level():
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

# TODO
    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving
            platforms collide with the player. """

        def spriteGroup():
            return pygame.sprite.Group()

        self.platform_list = spriteGroup()
        self.item_list = spriteGroup()
        self.boot_list = spriteGroup()
        self.enemy_list = spriteGroup()
        self.projectile_list = spriteGroup()
        self.ladder_list = spriteGroup()
        self.portal_list = spriteGroup()
        self.item_message_list1 = spriteGroup()
        self.item_message_list2 = spriteGroup()
        self.item_message_list3 = spriteGroup()
        self.item_message_list4 = spriteGroup()

        self.spriteList = [
            self.platform_list,
            self.item_list,
            self.boot_list,
            self.enemy_list,
            self.projectile_list,
            self.ladder_list,
            self.portal_list,
            self.item_message_list1,
            self.item_message_list2,
            self.item_message_list3,
            self.item_message_list4,
        ]

        self.message_list = [
            self.item_message_list1,
            self.item_message_list2,
            self.item_message_list3,
            self.item_message_list4,
        ]

        self.player = player

        # How far this world has been scrolled left/right
        self.world_shift_x = 0
        self.world_shift_y = 0

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

    def shift_world(self, shift_x, shift_y):
        """ When the user moves left/right and we need to scroll
        everything: """

        # Keep track of the shift amount
        self.world_shift_x += shift_x
        self.world_shift_y += shift_y

        # Go through all the sprite lists and shift
        # Go through all the sprite lists and shift
        for i in range(len(self.spriteList)):
            for item in self.spriteList[i]:
             item.rect.x += shift_x
             item.rect.y += shift_y
            
    def addObjects(self,levelLayout):
        y = 0
        for platform in levelLayout:
            x = 0
            for tile in platform:
                if tile == 1:
                    self.platform_list.add(Platform(groundTileTop, x, y))
                elif tile == 1.1:
                    self.platform_list.add(Platform(groundTileCorner,x,y))
                elif tile == 1.2:
                    self.platform_list.add(Platform(pygame.transform.flip(groundTileCorner, True, False),x,y))
                elif tile == 1.3:
                    self.platform_list.add(Platform(pygame.transform.rotate(groundTileTop, -90),x,y))
                elif tile == 1.4:
                    self.platform_list.add(Platform(pygame.transform.rotate(groundTileTop, 90),x,y))
                elif tile == 1.5:
                    self.platform_list.add(Platform(pygame.transform.flip(groundTileCorner, False, True),x,y))                    
                elif tile == 1.6:
                    self.platform_list.add(Platform(pygame.transform.flip(groundTileCorner, True, True),x,y))                    
                elif tile == 1.7:
                    self.platform_list.add(Platform(pygame.transform.flip(groundTileTop, False, True),x,y))                    
                elif tile == 2:
                    self.platform_list.add(Platform(groundTileInner,x,y))
                elif tile == 2.1:
                    self.item_message_list1.add(Platform(groundTileInner,x,y))
                elif tile == 2.2:
                    self.item_message_list2.add(Platform(groundTileInner,x,y))
                elif tile == 2.3:
                    self.platform_list.add(Platform(groundTileTop, x, y))
                    self.item_message_list4.add(Platform(groundTileTop, x, y))
                elif tile == 3:
                    self.item_message_list3.add(Platform(noticeBoard, x, y))
                elif tile == 4:
                    self.portal_list.add(Platform(portal,x,y))
                elif tile == 4.1:
                    self.item_list.add(Platform(pygame.transform.rotate(portal, 90),x,y))
                elif tile == 5:
                    self.ladder_list.add(Platform(vine,x,y))
                elif tile == 6:
                    self.boot_list.add(Platform(boot1,x,y))
                elif tile == 7:
                    self.item_list.add(Platform(house,x,y))
                elif tile == 8:
                    self.platform_list.add(Platform(groundTile_platform,x,y))
                elif tile == 8.1:
                    self.platform_list.add(Platform(groundTile_platform,x,y,x,x+(3*64),0,0,2,0))
                x += 64
            y += 64


# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)
        
        from level_01_layout import levelLayout
        self.addObjects(levelLayout)
        
#        enemy01 = Enemy01()
#        enemy01.rect.x = 750
#        enemy01.rect.y = 450
#        enemy01.player = self.player
#        enemy01.level = self
#        self.enemy_list.add(enemy01)
        
#        enemy02 = Enemy02()
#        enemy02.rect.x = 500
#        enemy02.rect.y = 450
#        enemy02.player = self.player
#        enemy02.level = self
#        self.enemy_list.add(enemy02)
        

class Level_02(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)
        
        from level_02_layout import levelLayout
        self.addObjects(levelLayout)


class Level_03(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)
        
        from level_03_layout import levelLayout
        self.addObjects(levelLayout)


#AI
import pandas as pd #(1) The ML step
from sklearn.tree import DecisionTreeRegressor

pong = pd.read_csv("gamedata-RB.csv")

X= pong.drop(columns=['enemy02.change_x','enemy02.change_y'])
y_1= pong['enemy02.change_x']
y_2=pong['enemy02.change_y']
clf = DecisionTreeRegressor(max_depth=3)

df = pd.DataFrame(columns=['player.rect.x-enemy02.rect.x', 'player.rect.y-enemy02.rect.y']) #Features

def main(current_level_no = 1):

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
    level_list.append(Level_02(player))
    level_list.append(Level_03(player))

    # Set the current level
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    if current_level_no == 0:
        player.rect.x = 340
        player.rect.y = 450
    if current_level_no == 1:
        player.rect.x = 550
        player.rect.y = 100
    if current_level_no == 2:
        player.rect.x = 1408
        player.rect.y = 3008
    player.change_y = 0
    active_sprite_list.add(player)

    # Displays objects
    def redrawWindow():
        global introOn
        global strList

        animatePlayer()

        # Shows intro screen
        if introOn:
            current_level.drawBg(menuBg, screen)
            active_sprite_list.draw(menuBg)

        # Shows game level
        if not introOn:
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
        global introOn

        if walkCount12 + 1 >= 28:
            walkCount12 = 0
        elif walkCount2 + 1 >= 7:
            walkCount2 = 0

        def setImage(newImage):
            player.image = newImage.convert_alpha()

        if movingLeft and not gravityIsNegative:
            setImage(charLeft[walkCount2//3])
            walkCount2 += 1
        if movingRight and not gravityIsNegative:
            setImage(charRight[walkCount2//3])
            walkCount2 += 1
        if isJumpLeft:
            setImage(jumpLeft)
        if isJumpRight:
            setImage(jumpRight)
        if gravityIsNegative:
            setImage(pygame.transform.flip(charStanding[walkCount12//3], False, True))
        if gravityIsNegative and movingLeft:
            setImage(pygame.transform.flip(charLeft[walkCount2//3], False, True))
        if gravityIsNegative and movingRight:
            setImage(pygame.transform.flip(charRight[walkCount2//3], False, True))
        if standing and not introOn:
            setImage(charStanding[walkCount12//3])
            walkCount12 += 1
        if introOn:
            setImage(pygame.transform.scale(charStanding[walkCount12//3], (int(player.rect.x * 0.9), int(player.rect.y * 1.5))))
            walkCount12 += 1

    def moveCamHorizontal(rightShift, leftShift):
        if player.rect.right >= rightShift:
            diff_x = player.rect.right - rightShift
            player.rect.right = rightShift
            current_level.shift_world(-diff_x,0)
        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= leftShift:
            diff_x = leftShift - player.rect.left
            player.rect.left = leftShift
            current_level.shift_world(+diff_x,0)
    
    def moveCamVertical(upShift, downShift):
        if player.rect.top <= upShift:
            diff_y = player.rect.top - upShift
            player.rect.top = upShift
            current_level.shift_world(0,-diff_y)
        if player.rect.bottom >= downShift:
            diff_y = downShift - player.rect.bottom
            player.rect.bottom = downShift
            current_level.shift_world(0,+diff_y)

    def playSound(soundToPlay):
        if pygame.mixer.music.get_busy():
            pass
        else:
            pygame.mixer.music.load(soundToPlay)
            pygame.mixer.music.play()

    def userEvents():
        global movingRight
        global movingLeft
        global standing
        global walkCount12
        global walkCount2
        global last_fired

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if pygame.sprite.spritecollide(player, player.level.ladder_list, False):
                    if event.key == pygame.K_SPACE:
                        player.go_up()
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()
#                if event.key == pygame.K_a:
#                    enemy02.go_left()
#                if event.key == pygame.K_d:
#                    enemy02.go_right()
#                if event.key == pygame.K_w:
#                    enemy02.jump()
                if event.key == pygame.K_r:  # respawn function by calling the main loop over current scenario
                    main(current_level_no)
                if event.key == pygame.K_q:  # quit function
                    pygame.quit()
                    os._exit(0)
                if event.key == pygame.K_p:
                    pause()
                    unpause()
                if event.key == pygame.K_LCTRL:
                    if len(player.level.projectile_list) < 1:
                        projectile = Projectile(player.direction)
                        projectile.rect.x = player.rect.x + 12.5
                        projectile.rect.y = player.rect.y + 20
                        player.level.projectile_list.add(projectile)
                        last_fired = pygame.time.get_ticks()
                    elif pygame.time.get_ticks() - last_fired > 2000:
                        projectile = Projectile(player.direction)
                        projectile.rect.x = player.rect.x + 12.5
                        projectile.rect.y = player.rect.y + 20
                        player.level.projectile_list.add(projectile)
                        last_fired = pygame.time.get_ticks()
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
#                if event.key == pygame.K_a and enemy02.change_x < 0:
#                    enemy02.stop()
#                if event.key == pygame.K_d and enemy02.change_x > 0:
#                    enemy02.stop()


    def pause(): # a simple pause function to allow the player to temporarily stop the game

        currentBg.fill((95, 95, 55))
        currentBg.blit(text3,
        (420 - text3.get_width() // 2, 240 - text3.get_height() // 2))

        redrawWindow()

    def unpause():
        
        global currentBg
        
        paused = True
        
        while paused == True:
            
            for event in pygame.event.get():  
              if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    currentBg = getImage("bg.png")
                    redrawWindow()
                    player.stop()
                    paused = False  
                elif event.key == pygame.K_q:
                    pygame.quit()
                    os._exit(0)
                else:
                   pass

    def showMessage(message, text):
        global currentText
        global noText
        
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
        redrawWindow()

    def game_over2():

        global currentBg

        over = True

        while over == True:

            for event in pygame.event.get():
              if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    currentBg = getImage("bg.png")
                    redrawWindow()
                    main(current_level_no)
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
                                 
#    def spawn_arena_enemy():
#        
#        global last_enemy
#        global enemy02
#        global kill_count
#      
#        if kill_count < 10:
#        
#            enemy_spawn = random.randint(0,1)
#        
#        
#            if enemy_spawn == 1:
#                enemy02 = Enemy01()
#                enemy02.rect.x = 200
#                enemy02.rect.y = 150
#            else:
#                enemy02 = Enemy02()
#                enemy02.rect.x = 850
#                enemy02.rect.y = 550
#        
#            enemy02.player = player
#            enemy02.level = current_level
#            player.level.enemy_list.add(enemy02)
#        
#        else:
#            enemy03 = Enemy01()
#            enemy04 = Enemy01()
#            enemy05 = Enemy01()
#            
#            enemy03.rect.x = 850
#            enemy03.rect.y = 550
#            enemy03.player = player
#            enemy03.level = current_level
#            player.level.enemy_list.add(enemy03)
#            
#            enemy04.rect.x = 850
#            enemy04.rect.y = 350
#            enemy04.player = player
#            enemy04.level = current_level
#            player.level.enemy_list.add(enemy04)
#            
#            enemy05.rect.x = 850
#            enemy05.rect.y = 150
#            enemy05.player = player
#            enemy05.level = current_level
#            player.level.enemy_list.add(enemy05)
#        
#        
#        last_enemy = pygame.time.get_ticks()
    
    trigger = 0
    
    # -------- Main Program Loop -----------
    while not done:
        
        gameIntro()
        global kill_count
        
        if current_level_no == 1:
            if trigger == 0:
                enemy02 = Enemy03()
                enemy02.rect.x = 225
                enemy02.rect.y = 125
                enemy02.player = player
                enemy02.level = current_level
                player.level.enemy_list.add(enemy02)
                trigger = 1

        if player.rect.bottom == SCREEN_HEIGHT or player.rect.bottom <= 0:
            game_over()
            game_over2()
#        for enemy in player.level.enemy_list:
#            if pygame.sprite.spritecollide(player, player.level.enemy_list, False):
#                game_over()
#                game_over2()
        
        # Projectile collision condition
        for projectile in player.level.projectile_list:
            if projectile.rect.x > player.rect.x + 450 or projectile.rect.x < player.rect.x - 450:
                projectile.kill()
            for enemy in player.level.enemy_list:
                projectile_enemy_hit = pygame.sprite.spritecollide(projectile, player.level.enemy_list, False)
                for x in projectile_enemy_hit:
                    projectile.kill()
                    enemy.kill()
                    kill_count += 1
            projectile_platform_hit = pygame.sprite.spritecollide(projectile, player.level.platform_list, False)
            for y in projectile_platform_hit:
                projectile.kill()
                
        for portal in player.level.portal_list:
            portal_hit = pygame.sprite.spritecollide(player, player.level.portal_list, False)
            if portal_hit:
                if current_level_no == 0:
                    player.rect.x = 550
                    player.rect.y = 100
                if current_level_no == 1:
                    player.rect.x = 1408
                    player.rect.y = 3008
                player.change_y = 0
                if current_level_no < len(level_list)-1:
                    current_level_no += 1
                    current_level = level_list[current_level_no]
                    player.level = current_level
                else:
                    # Out of levels. This just exits the program.
                    # You'll want to do something better.
                    done = True
    
#        current_time = pygame.time.get_ticks() 
#        if current_level_no == 1:
#           if current_time > last_enemy + 2000:
#               if len(player.level.enemy_list) < 3:
#                spawn_arena_enemy()
#               else:
#                    pass
#           else:
#               pass
        
        #AI for enemy
        toPredict = df.append({'player.rect.x-enemy02.rect.x': (player.rect.x-enemy02.rect.x), 'player.rect.y-enemy02.rect.y': (player.rect.y-enemy02.rect.y)}, ignore_index= True)
        #print(clf.predict(toPredict))
        enemy02.updateAI(clf.fit(X,y_1).predict(toPredict),clf.fit(X,y_2).predict(toPredict))
        
        userEvents()
        clock.tick(FPS)
        if current_level_no != 1:
            moveCamHorizontal(500, 120)
        if current_level_no == 2:
            moveCamVertical(300, 600)
        
        playVideo(clip)
        playSound(bgMusic)
        # showMessage(current_level.message_list, welcomeText)
        # showMessage(current_level.item_message_list2, bootsText)
        redrawWindow()

    # vital for the mac issue pt3
    pygame.quit()
    os._exit(0) 

    
#    # Loop until the user clicks the close button.
#    done = False
#
#    # Create the player
#    player = Player()
#
#    # Create all the levels
#    level_list = Level_01(player)
#
#    # Set the current level
#    current_level = level_list
#
#    active_sprite_list = pygame.sprite.Group()
#    player.level = current_level
#
#    player.rect.x = 340
#    player.rect.y = 450
#    active_sprite_list.add(player)
#
#    pygame.quit()
#    os._exit(0)


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


# https: // www.youtube.com/watch?v = UdsNBIzsmlI
# https: // www.youtube.com/watch?v = HCWI2f7tQnY