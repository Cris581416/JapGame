import pygame
from pygame import *
from pygame import surface
import random
from os import path
import sys

pygame.mixer.pre_init(22050, -16, 2, 512)
pygame.init()
pygame.mixer.init()

print(sys.path)

height = 600
width = 400
fps = 60
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption(u"ステイホーム")
screen = pygame.display.set_mode(size = (width, height))
mobSpeed = 8

# Files
imageDir = path.join(path.dirname(__file__), 'images')
titleImg = pygame.image.load(path.join(imageDir, 'title.png')).convert()
backgroundImg = pygame.image.load(path.join(imageDir, 'bckgrnd.png')).convert()
mobImg = pygame.image.load(path.join(imageDir, 'vrs.png')).convert()
pwrUpList = ['mask', 'sanitizer', 'house', 'glasses', 'vaccine']
powerupImgs = {}
for i in pwrUpList:
    j = i + '.png'
    powerupImgs[i] = pygame.image.load(path.join(imageDir, j)).convert()
charList = ['charCent', 'charLeft1', 'charLeft2', 'charRight1', 'charRight2']
charImgs = {}
for i in charList:
    j = i + '.png'
    charImgs[i] = pygame.image.load(path.join(imageDir, j)).convert()
soundDir = path.join(path.dirname(__file__), 'sounds')
sndList = ['pew', 'explosion', 'powerup']
sounds = {}
for i in sndList:
    j = i + '.wav'
    sounds[i] = pygame.mixer.Sound(path.join(soundDir, j))
    sounds[i].set_volume(0.5)
nomonkey = pygame.mixer.music.load(path.join(soundDir, 'nomonkey.wav'))
pygame.mixer.music.set_volume(0.4)
textDir = path.join(path.dirname(__file__), 'texts')
textList = ['maskDesc1', 'maskDesc2', 'sanitizerDesc1', 'sanitizerDesc2', 'houseDesc1', 'houseDesc2', 'glassesDesc1', 'glassesDesc2', 'vaccineDesc1', 'vaccineDesc2']
texts = {}
for i in textList:
    j = i + '.txt'
    texts[i] = path.join(textDir, j)

# Fonts 
arial = pygame.font.match_font('arial')
jackeyfont = pygame.font.match_font('jackeyfont')

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
purple = (74, 20, 140)

# Player Sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = charImgs['charCent']
        self.image.set_colorkey(purple)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        #pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        self.rect.centerx = width/2
        self.rect.centery = height - 25
        self.xspeed = 0
        self.health = 100
        self.shield = 3
        self.autoPilotSwitch = False
        self.charCounter = 0
    
    def changeCharacter(self, direction):
        if direction > 0:
            if self.charCounter < 0:
                self.charCounter = 0
            self.charCounter += 4/60
            if self.charCounter > 0.5:
                self.image = charImgs['charRight1']
                self.image.set_colorkey(purple)
            else:
                self.image = charImgs['charRight2']
                self.image.set_colorkey(purple)
            if self.charCounter >= 1:
                self.charCounter = 0
        elif direction < 0:
            if self.charCounter > 0:
                self.charCounter = 0
            self.charCounter -= 4/60
            if self.charCounter < -0.5:
                self.image = charImgs['charLeft1']
                self.image.set_colorkey(purple)
            else:
                self.image = charImgs['charLeft2']
                self.image.set_colorkey(purple)
            if self.charCounter <= -1:
                self.charCounter = 0
        else:
            self.image = charImgs['charCent']
            self.charCounter = 0
    
    def update(self):
        self.xspeed = 0
        keys = pygame.key.get_pressed()
        if self.autoPilotSwitch:
            autoPilot(self, mobs)
        else:
            if keys[K_LEFT]:
                self.xspeed = -5
            if keys[K_RIGHT]:
                self.xspeed = 5
        self.rect.x += self.xspeed
        self.changeCharacter(self.xspeed)
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left < 0:
            self.rect.left = 0
    
    def shoot(self):
        sounds['pew'].play()
        b = Bullet(self.rect.centerx, self.rect.y)
        allSprites.add(b)
        bullets.add(b)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.originalImage = pygame.transform.scale(mobImg, (32, 32))
        self.originalImage.set_colorkey(white)
        self.image = self.originalImage.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        # pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        self.rect.centery = -16
        self.origX = random.randrange(0, width - 32, 10)
        self.rect.x = self.origX
        global mobSpeed
        self.yspeed = random.randint(mobSpeed - 2, mobSpeed)
        self.xspeed = random.randint(-2, 2)
        self.rotAngle = 0
        self.rotSpeed = random.randint(-8, 8)
        self.lastRot = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        sleepTime = 1000/360
        if (now - self.lastRot) > sleepTime:
            self.lastRot = now
            self.rotAngle = self.rotAngle + self.rotSpeed
            newImage = pygame.transform.rotate(self.originalImage, (self.rotAngle % 360))
            oldCenter = self.rect.center
            self.image = newImage
            self.rect = self.image.get_rect()
            self.rect.center = oldCenter
    
    def update(self):
        self.rotate()
        self.rect.centery += self.yspeed
        self.rect.centerx += self.xspeed
        if self.rect.top > height or self.rect.left < (0 - 32) or self.rect.right > (width + 32) or self.xspeed == 0:
            self.rect.centery = -self.rect.height/2
            self.origX = random.randrange(0, width - 32)
            self.rect.x = self.origX
            global mobSpeed
            self.yspeed = random.randint(mobSpeed - 2, mobSpeed)
            self.xspeed = random.randint(-2, 2)
    
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((4, 16))
        self.image.fill(green)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.yspeed = -10

    def update(self):
        self.rect.bottom += self.yspeed
        if self.rect.bottom < 0:
            self.kill()
    
class Powerup(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.chooser = random.random()
        if self.chooser <= 4/15:
            self.type = 'mask'
            self.image = pygame.transform.scale2x(powerupImgs[self.type])
            self.image.set_colorkey(purple)
        elif self.chooser <= 8/15:
            self.type = 'sanitizer'
            self.image = powerupImgs[self.type]
            self.image.set_colorkey(purple)
        elif self.chooser <= 10/15:
            self.type = 'glasses'
            self.image = powerupImgs[self.type]
            self.image.set_colorkey(purple)
        elif self.chooser <= 13/15:
            self.type = 'vaccine'
            self.image = powerupImgs[self.type]
            self.image.set_colorkey(purple)
        else:
            self.type = 'house'
            self.image = powerupImgs[self.type]
            self.image.set_colorkey(purple)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.yspeed = 5

    def update(self):
        self.rect.bottom += self.yspeed
        if self.rect.top > height:
            self.kill()

class TextBox:
    def __init__(self, text, pos, rectSize, font, size, bgColor, textColor = (255, 255, 255)):
        self.fnt = pygame.font.Font(font, size)
        self.fontHeight = self.fnt.get_linesize()
        self.text = text.split(' ')  # Single words.
        self.rect = pygame.Rect(pos, rectSize)
        self.bgColor = bgColor
        self.textColor = textColor
        self.renderTextSurfaces()

    def renderTextSurfaces(self):
        """Create a new text images list when the rect gets scaled."""
        self.images = []  # The text surfaces.
        lineWidth = 0
        line = []
        # Put the words one after the other into a list if they still
        # fit on the same line, otherwise render the line and append
        # the resulting surface to the self.images list.
        for word in self.text:
            lineWidth += self.fnt.size(word)[0]
            # Render a line if the line width is greater than the rect width.
            if lineWidth > self.rect.w:
                surf = self.fnt.render(''.join(line), True, self.textColor)
                self.images.append(surf)
                line = []
                lineWidth = self.fnt.size(word)[0]

            line.append(word)

        # Need to render the last line as well.
        surf = self.fnt.render(' '.join(line), True, self.textColor)
        self.images.append(surf)

    def draw(self, screen):
        """Draw the rect and the separate text images."""
        pygame.draw.rect(screen, self.bgColor, self.rect)

        for y, surf in enumerate(self.images):
            # Don't blit below the rect area.
            if y * self.fontHeight + self.fontHeight > self.rect.h:
                break
            screen.blit(surf, (self.rect.x, self.rect.y + y * self.fontHeight))

    def scale(self, rel):
        self.rect.w += rel[0]
        self.rect.h += rel[1]
        self.rect.w = max(self.rect.w, 30)  # 30 px is the minimum width.
        self.rect.h = max(self.rect.h, 30)
        self.renderTextSurfaces()

    def move(self, rel):
        self.rect.move_ip(rel)
        self.rect.clamp_ip(screen.get_rect())
            
def createMob():
    m = Mob()
    allSprites.add(m)
    mobs.add(m)

def drawHealthBar(surface, x, y, percentage):
    if percentage < 0:
        percentage = 0
    barLength = 100
    barHeight = 10
    bar = (x + 2, y + 2, percentage * barLength / 100, barHeight)
    outline = (x, y, barLength + 4, barHeight + 4)
    pygame.draw.rect(surface, green, bar)
    pygame.draw.rect(surface, white,outline, 1)

def drawShields(surface, shields):
    x = 10
    y = 27
    im = pygame.image.load(path.join(imageDir, 'shield.png')).convert()
    im.set_colorkey(purple)
    for shield in range(shields):
        shieldRect = im.get_rect(left = x, top = y)
        surface.blit(im, shieldRect)
        x += shieldRect.width + 3

def drawText(surface, text, fontName, fontSize, x, y, boxSize = ()):
    font = pygame.font.Font(fontName, fontSize)
    textSurface = font.render(text, True, white)
    if boxSize:
        fitRect = textSurface.get_rect(midtop = (x, y))
        textRect = pygame.Rect(fitRect.x, fitRect.y, boxSize[0], boxSize[1])
    else: 
        textRect = textSurface.get_rect(midtop = (x, y))
    surface.blit(textSurface, textRect)

def flToStr(filePath):
    file = open(filePath, encoding= 'utf-8')
    str = file.read().replace("\n", " ")
    file.close()
    return str

def autoPilot(player, mbs):
    xspeed = 0
    for mob in mbs:
        """finalPos = (mob.xspeed/mob.yspeed) * (height - 25 - player.rect.width) + mob.origX
        if player.rect.left < finalPos - mob.rect.width/2 and player.rect.right > finalPos - mob.rect.width/2:
            xspeed = -5
            return xspeed
        if player.rect.left > finalPos - mob.rect.width/2 and player.rect.right < finalPos + mob.rect.width/2:
            xspeed = 5
            return xspeed"""
        if mob.rect.x > 0 + player.rect.width/2 and mob.rect.x < width - player.rect.width/2:
            player.rect.x = mob.rect.x
            player.shoot()

def hurtOrHeal(hurt):
    if hurt:
        if p1.shield > 0:
            p1.shield -= 1
        else:
            p1.health -= 25
    else:
        if p1.health < 100:
            p1.health += 25
        elif p1.shield < 3:
            p1.shield += 1

allSprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
p1 = Player()
allSprites.add(p1)
for i in range(8):
    m = Mob()
    allSprites.add(m)
    mobs.add(m)

# Loop Bools
gameOver = False
mainRunning = False
starting = True
informing = False
quit = True
looping = True

# Counter Bools/Ints
clearer = False
clearTime = 0
score = 0
difficulty = 0
autoPilotTime = 0

# Messages
introMessage1 = 'PRESS [SPACE] TO START'
introMessage2 = 'PRESS [TAB] TO SHOW'
introMessage3 = 'POWERUP INFO'
endMessage1 = "あなたのファイナルスコアは: "
textboxSize = (315, 32)
infoImgs = []
for image in powerupImgs.values():
    im = pygame.transform.scale2x(image)
    im.set_colorkey(purple)
    infoImgs.append(im)
textBoxes = []
ys = [77]
txtX = 80
txtY = 45
txtSwitch = True
for textName in textList:
    desc = TextBox(flToStr(texts[textName]), (txtX, txtY), textboxSize, jackeyfont, 15, black)
    textBoxes.append(desc)
    if txtSwitch:
        txtY += 32
        mm = txtY + 96
        ys.append(mm)
        txtSwitch = not txtSwitch
    else:
        txtY += 64
        txtSwitch = not txtSwitch

# Music
pygame.mixer.music.play(loops = -1)

while looping:
    while starting:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                starting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mainRunning = True
                    starting = False
                elif event.key == pygame.K_TAB:
                    informing = True
                    starting = False
    
        # Drawing
        screen.blit(backgroundImg, (0, 0, width, height))
        titleImg.set_colorkey(purple)
        screen.blit(titleImg, (0, 10, 400, 200))

        drawText(screen, introMessage1, jackeyfont, 30, width/2, height/2)
        drawText(screen, introMessage2, jackeyfont, 30, width/2, height/2 + 50)
        drawText(screen, introMessage3, jackeyfont, 30, width/2, height/2 + 85)

        # Display
        pygame.display.flip()


    while informing:
    # Event Handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                informing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    quit = False
                    starting = True
                    informing = False
    
        # Drawing
        screen.blit(backgroundImg, (0, 0, width, height))

        drawText(screen, 'PRESS [TAB] TO RETURN', jackeyfont, 15, width/2 - 100, 5)

        for i in range(10):
            textBoxes[i].draw(screen)

        for i in range(5):
            screen.blit(infoImgs[i], infoImgs[i].get_rect(x = 10, centery = ys[i]))

        # Displaying
        pygame.display.flip()


    while mainRunning:
        # FPS Setter
        clock.tick(fps)

        # Score Handling
        score += 1/60

        # Difficulty Handler
        difficulty += 1/60
        if difficulty >= 5:
            mobSpeed += 1
            #print(mobSpeed)
            difficulty = 0

        #Powerup Execution
        if clearer:
            clearTime += 1
        if clearTime == 300:
            for i in range(8):
                createMob()
                #print("New Mob Spawning")
            clearer = False
            clearTime = 0
    
        if p1.autoPilotSwitch:
            autoPilotTime += 1
            if autoPilotTime == 60: 
                autoPilotTime = 0
                p1.autoPilotSwitch = False

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                mainRunning = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    p1.shoot()

        # Updating
        allSprites.update()

        # Checking For Mob/Player/Bullet/Powerup Collision 
        collisions = pygame.sprite.spritecollide(p1, mobs, True, pygame.sprite.collide_circle)
        for collision in collisions:
            createMob()
            hurtOrHeal(True)
            if p1.health <= 0:
                gameOver = True
                mainRunning = False
    
        hits = pygame.sprite.groupcollide(bullets, mobs, True, True)
        for hit in hits:
            sounds['explosion'].play()
            createMob()
            if random.random() > 0.9:
                p = Powerup(hit.rect.center)
                allSprites.add(p)
                powerups.add(p)

        poweredUp = pygame.sprite.spritecollide(p1, powerups, True)
        for powerup in poweredUp:
            sounds['powerup'].play()
            if powerup.type == 'mask':
                hurtOrHeal(False)
            elif powerup.type == 'sanitizer':
                for mob in mobs:
                    mob.kill()
                clearer = True
            elif powerup.type == 'house':
                p1.health = 100
                p1.shield = 3
            elif powerup.type == 'vaccine':
                if random.random() >= 0.5:
                    p1.health = 100
                else:
                    p1.health = 25
            else:
                p1.autoPilotSwitch = True
    
        # Drawing
        screen.blit(backgroundImg, (0, 0, width, height))

        allSprites.draw(screen)

        drawText(screen, str(int(score)), arial, 20, width / 2, 10)
        
        drawHealthBar(screen, 10, 10, p1.health)

        drawShields(screen, p1.shield)

        # Displaying
        pygame.display.flip()


    endMessage2 = str(int(score)) + " です"
    while gameOver:
        # Event Handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                gameOver = False
    
        # Drawing
        screen.blit(backgroundImg, (0, 0, width, height))

        drawText(screen, endMessage1, jackeyfont, 30, width / 2, height / 2)
        drawText(screen, endMessage2, jackeyfont, 30, width / 2, (height / 2) + 35)

        # Display
        pygame.display.flip()

    if quit:
        looping = False
        pygame.quit()