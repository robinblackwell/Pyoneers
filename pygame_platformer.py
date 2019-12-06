import pygame
import os  # vital to fix the mac issue pt1

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 640

pygame.init()

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

# Global variables
FPS = 40
levelLimit = -1000

# Character
gravity = 3
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

last_fired = 0


def getImage(source):
    return pygame.image.load("assets/{}".format(source))


# Player sprites
charRight = [getImage("playerRight.png"), getImage("playerRight2.png")]
charLeft = [getImage("playerLeft.png"), getImage("playerLeft2.png")]
charStanding = [getImage("playerStanding1.png"), getImage("playerStanding2.png"), getImage("playerStanding3.png"), getImage("playerStanding4.png"), getImage("playerStanding2.png"), getImage("playerStanding5.png"), getImage("playerStanding1.png"), getImage("playerStanding2.png"), getImage("playerStanding3.png"),getImage("playerStanding1.png"), getImage("playerStanding2.png"), getImage("playerStanding3.png")]
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
    
        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        for enemy in enemy_hit_list:
            if enemy.rect.top > self.rect.bottom - 20:
                enemy.kill()
                self.change_y = -20
                
        block_hit_list = blocklist.spritecollide(self, self.level.platform_list, False)

        for block in block_hit_list:
            # Reset our position based on the left/right of the object.
            if block.change_x < 0:
                self.rect.right = block.rect.left
            else:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
        
        block_hit_list = blocklist.spritecollide(self, self.level.platform_list, False)

        for block in block_hit_list:
            if block.change_x != 0:
                if block.change_y < 0:
                    self.rect.bottom = block.rect.top
                else:
                    self.rect.top = block.rect.bottom
        
        block_hit_list = blocklist.spritecollide(self, self.level.platform_list, False)

        for block in block_hit_list:
            if self.rect.bottom == block.rect.top:
                self.change_x += block.rect.x
                
        block_hit_list = blocklist.spritecollide(self, self.level.platform_list, False)                

        for block in self.level.platform_list:
            if block.rect.bottom > block.boundary_bottom or block.rect.top < block.boundary_top:
                block.change_y *= -1
     
            cur_pos = block.rect.x - self.level.world_shift
            if cur_pos < block.boundary_left or cur_pos > block.boundary_right:
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
            if not gravityIsNegative:
                gravity *= -1
                gravityIsNegative = True
            elif gravityIsNegative:
                gravity *= +1
                gravityIsNegative = False
            self.jump()
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
         
    def __init__(self, tileType, boundary_top = 0, boundary_bottom = 0, boundary_left = 0, boundary_right = 0, change_x = 0, change_y = 0):
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
 
    isLadder = False
    
    def update(self):
        
        if self.isLadder == False:

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
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
        
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


class Level():
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving
            platforms collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.item_list = pygame.sprite.Group()
        self.boot_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.projectile_list = pygame.sprite.Group()
        self.ladder_list = pygame.sprite.Group()

        self.player = player

        # How far this world has been scrolled left/right
        self.world_shift = 0

    # Update everythign on this level
    def update(self):
        """ Update everything in this level."""
        self.item_list.update()
        self.platform_list.update()
        self.boot_list.update()
        self.enemy_list.update()
        self.projectile_list.update()
        self.ladder_list.update()

    def drawBg(self, screen):
        """ Draw background """
        global bgY
        global bgX
        screen.blit(bg, (bgX, bgY))
        
    def drawLevel(self, screen):
        """ Draw everything on this level. """
        # Draw all the sprite lists that we have
        self.item_list.draw(screen)
        self.platform_list.draw(screen)
        self.boot_list.draw(screen)
        self.enemy_list.draw(screen)
        self.projectile_list.draw(screen)
        self.ladder_list.draw(screen)
        

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll
        everything: """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for item in self.item_list:
            item.rect.x += shift_x
            
        for boot in self.boot_list:
            boot.rect.x += shift_x
            
        for enemy in self.enemy_list:
            enemy.rect.x += shift_x
            
        for projectile in self.projectile_list:
            projectile.rect.x += shift_x
        
        for ladder in self.ladder_list:
            ladder.rect.x += shift_x

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
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  ],

            [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5, 1.7, 1.7, 1.7, 1.7, 1.7, 1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  ],
                        
            [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],
                        
            [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.1, 8.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],
                        
            [
            0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.5, 8.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7, 1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  ],

            [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.2, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],
                        
            [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.5, 1.6, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  ],
                        
            [
            1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.3, 0.0, 1.5, 1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ],
                        
            [
            1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.3, 0.0, 0.0, 1.1, 1.0, 1.0, 1.2, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 1.1, 1.0, 1.0, 1.2, 0.0, 1.1, 1.0, 1.2, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.1, 1.2, 0.0, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ]
        ]

        def updateLevelImages(classType, imageToUpdate, isCollidable, isBoot, isLadder, isMoving):
            if isMoving:
                block = classType(imageToUpdate, boundary_left = x, boundary_right = x + (3*64), change_x = 1)
            else:
                block = classType(imageToUpdate)
            block.rect.x += x
            block.rect.y += y
            if isBoot:
                self.boot_list.add(block)
            elif isCollidable:
                if isLadder:
                    block.isLadder = True
                    self.ladder_list.add(block)
                else:
                    self.platform_list.add(block)
            elif not isCollidable:
                self.item_list.add(block)
            
            
        y = 0
        for platform in levelLayout:
            x = 0
            for tile in platform:
                if tile == 1:
                    updateLevelImages(Platform, groundTileTop, True, False, False, False)
                elif tile == 1.1:
                    updateLevelImages(Platform, groundTileCorner, True, False, False, False)
                elif tile == 1.2:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, True, False), True, False, False, False)
                elif tile == 1.3:
                    updateLevelImages(Platform, pygame.transform.rotate(groundTileTop, -90), True, False, False, False)
                elif tile == 1.4:
                    updateLevelImages(Platform, pygame.transform.rotate(groundTileTop, 90), True, False, False, False)
                elif tile == 1.5:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, False, True), True, False, False, False)
                elif tile == 1.6:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, True, True), True, False, False, False)
                elif tile == 1.7:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileTop, False, True), True, False, False, False)
                elif tile == 2:
                    updateLevelImages(Platform, groundTileInner, True, False, False, False)
                elif tile == 3:
                    updateLevelImages(Platform, noticeBoard, False, False, False, False)
                elif tile == 4:
                    updateLevelImages(Platform, portal, False, False, False, False)
                elif tile == 4.1:
                    updateLevelImages(Platform, pygame.transform.rotate(portal, 90), True, False, False, False)
                elif tile == 5:
                    updateLevelImages(Platform, vine, True, False, True, False)
                elif tile == 6:
                    updateLevelImages(Platform, boot1, True, True, False, False)
                elif tile == 7:
                    updateLevelImages(Platform, house, False, False, False, False)
                elif tile == 8:
                    updateLevelImages(Platform, groundTileTop, True, False, False, True)
                elif tile == 8.1:
                    updateLevelImages(Platform, groundTileCorner, True, False, False, True)
                elif tile == 8.2:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, True, False), True, False, False, True)
                elif tile == 8.3:
                    updateLevelImages(Platform, pygame.transform.rotate(groundTileTop, -90), True, False, False, True)
                elif tile == 8.4:
                    updateLevelImages(Platform, pygame.transform.rotate(groundTileTop, 90), True, False, False, True)
                elif tile == 8.5:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, False, True), True, False, False, True)
                elif tile == 8.6:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileCorner, True, True), True, False, False, True)
                elif tile == 8.7:
                    updateLevelImages(Platform, pygame.transform.flip(groundTileTop, False, True), True, False, False, True)
                x += 64
            y += 64
        
        enemy01 = Enemy01()
        enemy01.rect.x = 750
        enemy01.rect.y = 450
        enemy01.player = self.player
        enemy01.level = self
        self.enemy_list.add(enemy01)


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
            setImage(pygame.transform.flip(charStanding[walkCount12//3], False, True))
        elif gravityIsNegative and movingLeft:
            setImage(pygame.transform.flip(charLeft[walkCount2//3], False, True))
        elif gravityIsNegative and movingRight:
            setImage(pygame.transform.flip(charRight[walkCount2//3], False, True))
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
        global last_fired

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if pygame.sprite.spritecollide(player, player.level.ladder_list, False):
                    if event.key == pygame.K_SPACE:
                        player.go_up()
                elif event.key == pygame.K_LEFT:
                   player.go_left()
                elif event.key == pygame.K_RIGHT:
                   player.go_right()
                elif event.key == pygame.K_SPACE:
                   player.jump()
                elif event.key == pygame.K_LCTRL:
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
                        pass
                elif event.key == pygame.K_a:
                   player.invertGravity()
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
        if player.rect.bottom == SCREEN_HEIGHT or player.rect.bottom <= 0:
            game_over()
            pygame.quit()
            break
        for enemy in player.level.enemy_list:
            if pygame.sprite.spritecollide(player, player.level.enemy_list, False):
                game_over()
                pygame.quit()
        
        # Projectile collision condition
        for projectile in player.level.projectile_list:
            if projectile.rect.x > player.rect.x + 450 or projectile.rect.x < player.rect.x - 450:
                projectile.kill()
            for enemy in player.level.enemy_list:
                projectile_enemy_hit = pygame.sprite.spritecollide(projectile, player.level.enemy_list, False)
                for x in projectile_enemy_hit:
                    projectile.kill()
                    enemy.kill()
            projectile_platform_hit = pygame.sprite.spritecollide(projectile, player.level.platform_list, False)
            for y in projectile_platform_hit:
                projectile.kill()
        
        userEvents()
        clock.tick(FPS)
        moveCam(500, 120)
        redrawWindow()
    
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
    # - House smoke


# https: // www.youtube.com/watch?v = UdsNBIzsmlI
# https: // www.youtube.com/watch?v = HCWI2f7tQnY