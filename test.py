import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

class Rec(pygame.sprite.Sprite):

    def __init__(self, x, y, w, height):

        super().__init__()

        self.b = 0
        self.image = pygame.image.load("assets/ground_tile1.png").convert()
        if w <= 70:
            self.image = pygame.transform.scale(self.image, (w, height))
        elif w > 70:
            self.image = pygame.Surface([w, height])
            while self.b < w:
                self.image.blit(pygame.image.load(
                    "assets/ground_tile1.png").convert(), (x + self.b, y))
                self.b += 70

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

pygame.init()
while True:
    size = (700, 500)

    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("My Game")

    all_sprites_list = pygame.sprite.Group()

    rec = Rec(100, 200, 140, 70)
    all_sprites_list.add(rec)
    clock = pygame.time.Clock()

done = False
