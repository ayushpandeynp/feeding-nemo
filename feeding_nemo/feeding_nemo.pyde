add_library('minim')

import random, os, datetime, math

path = os.getcwd()

WIDTH = 1280
HEIGHT = 795

# this is to set random direction for every Fish object during __init__() (also nemo and enemies as they inherit from Fish class)
directions = [LEFT, RIGHT]

# font for text (LEVEL, TIMER, SCORE)
font = loadFont(path + "/fonts/bebas_neue.vlw")
audio = Minim(this)

class Fish():
    def __init__(self, posX, posY, size, img, speed):
        
        # the x and y coordinates of the obj, x and y seemed confusing so I've used posX and posY
        self.posX = posX
        self.posY = posY
        
        self.rotation = 0
        
        # image path for nemo and enemies
        self.img = loadImage(path + "/images/" + img)
        
        # instead of radius, i've called it size so that we can take this variable to compare nemo's size and enemies' size when they're near
        self.size = size

        # this speed determines the increment for posX and posY when the obj moves around the screen, see mouseHandler()
        self.speed = speed
        
        # initializing random direction for nemo and enemies
        self.direction = random.choice(directions)
        
        # this is to crop every characters image
        # like in super mario, there's one single image for mario and then prof. crops it to show movement animation at every certain frameCount
        # for eg: in our game, the nemo_char.png has 5 nemos together
        # so we generate a random position from 0 to 4 and then multiply this value with (total image size)/5 i.e. the size of individual character (nemo or enemy)
        self.cropStart = random.randint(0, 4)
    
    def update():
        pass
    
    def display(self):
        self.update()
        
        playerCenterX, playerCenterY = self.getCenterCoordinates()
        if self.__class__.__name__ == "Player":
            self.rotation = math.atan2((mouseY - playerCenterY), (mouseX - playerCenterX))
    
        # individual image size of our character (because we have 5 images in a single PNG)
        # total image width / 5
        singleSize = self.img.width / self.imageCount
        
        # when frameCount % 5, we use the cropStart value to determine our start position (x1, y1) like (self.cropStart * singleSize, 0)
        if frameCount % 5 == 0 or frameCount == 1:
            
            # when cropStart reaches 5 we need to set it to 0 cuz 5 * singleSize is null
            self.cropStart += 1
            if self.cropStart >= self.imageCount:
                self.cropStart = 0 
                
        # checking the direction of our Fish (also nemo, enemies) and displaying them respectively
        if abs(self.rotation) > (math.pi / 2):
            self.direction = LEFT
        else:
            self.direction = RIGHT
            
        pushMatrix()
        imageMode(CENTER)
        translate(self.posX, self.posY)
        rotate(self.rotation)
        
        if self.direction == RIGHT:
            scale(1, 1)
            image(self.img, 0, 0, self.size, self.size, self.cropStart * singleSize, 0, self.cropStart * singleSize + singleSize, self.img.height)
        else:
            scale(-1, 1)
            image(self.img, 0, 0, -self.size, self.size, (self.cropStart * singleSize + singleSize), self.img.height, self.cropStart * singleSize, 0)
            
        popMatrix()
        
    def getCenterCoordinates(self):
        return self.posX + self.size / 2, self.posY + self.size / 2
        
class Player(Fish):
    def __init__(self, posX, posY, size, img, speed):
        Fish.__init__(self, posX, posY, size, img, speed)
        
        self.imageCount = 8
        self.alive = True
        
        self.eat = audio.loadFile(path + "/audio/nemo_eat.mp3")
        self.tokenEat = audio.loadFile(path + "/audio/token.mp3")
    
    def update(self):
        pass
    
class Enemy(Fish):
    def __init__(self, posX, posY, size, img, speed, imageCount):
        Fish.__init__(self, posX, posY, size, img, speed)
        self.imageCount = imageCount
        
        self.increment = [self.speed, self.speed]
        
    def update(self):
        
        if dist(self.posX, self.posY, game.nemo.posX, game.nemo.posY) < self.size / 2 + game.nemo.size / 2:
            if self.size > game.nemo.size:
                game.nemo.alive = False
            else:
                game.nemo.eat.rewind()
                game.nemo.eat.play()
                game.score += 10
                game.preys.remove(self)
        
        if (self.posX + self.size / 2 + self.speed) > game.w:
            self.rotation = math.pi
            self.increment[0] = -self.speed
        elif (self.posX - self.size / 2 - self.speed) < 0:
            self.rotation = 0
            self.increment[0] = self.speed
            
        if (self.posY + self.size / 2 + self.speed) > game.h:
            self.increment[1] = -self.speed
        elif (self.posY - self.size / 2 - self.speed) < 0:
            self.increment[1] = self.speed
        
        self.posX += self.increment[0]
        self.posY += self.increment[1]
        
class Shark(Fish):
    def __init__(self, posX, posY, size, img, speed):
        Fish.__init__(self, posX, posY, size, img, speed)

class Token():
    def __init__(self, x, y):
        self.posX = x 
        self.posY = y
        self.img = loadImage(path + "/images/token.png")
        self.size = 30
        
        self.cropStart = random.randint(1, 23)
        self.eaten = False

    def display(self):
        tokenSize = self.img.width / 23 # the sprite has 23 tokens so i divide by 23

        if frameCount % 2 == 0 or frameCount == 1:
            self.cropStart += 1
            if self.cropStart >= 23:
                self.cropStart = 0
                
        image(self.img, self.posX, self.posY, self.size, self.size, self.cropStart * tokenSize, 0, self.cropStart * tokenSize + tokenSize, self.img.height)
        
        if dist(self.posX, self.posY, game.nemo.posX, game.nemo.posY) <= (game.nemo.size / 2 + self.size / 2):
            game.nemo.tokenEat.rewind()
            game.nemo.tokenEat.play()
            game.score += 1
            game.tokens.remove(self)
        
class Game():
    def __init__(self, w, h):
        
        self.w = w
        self.h = h
        
        self.score = 0
        
        self.keyHandler = {32:False, 13:False, 27:False}

        
        # this is for the timer, we take the datetime value during __init__ and then on every frame we check time diffrence in seconds
        # then we use the getTimer() function inside Game class to get the timer format in M:S
        self.start = datetime.datetime.now()
        
        self.level = 1
        
        # the following line was here before. going through the code again, I realized it was unnecessary. I only used it for testing, so it's not required now
        # self.playerMove = {LEFT: False, RIGHT: False, UP: False, DOWN: False} 
        
        self.nemo = Player(200, 200, 80, "nemo.png", 4)
        
        self.bg = Background(self.w, self.h)
        
        # to know which screen we're in, Main Menu, the Game, GameOver screen
        self.screen = 1
        
        #self.bg_music = player.loadFile(path + "/sounds/background.mp3")
        #self.bg_music.loop()
        
        self.tokens = []
        self.npreys = 15
        
        fishCount = [6, 5, 5, 6, 6]
        self.preys = []
        for i in range(self.npreys):
            fish = random.randint(0, 4)
            self.preys.append(Enemy(random.randint(100, self.w - 100), random.randint(50, self.h - 50), self.nemo.size / 2, "fish" + str(fish + 1) + ".png", random.uniform(1.5, 3), fishCount[fish]))
                              
        self.predators = []
        for i in range(5):
            self.preys.append(Enemy(random.randint(300, self.w - 100), random.randint(50, self.h - 50), self.nemo.size * 1.5, "predator.png", random.uniform(1.5, 2.2), 9))
            
        self.background = audio.loadFile(path + "/audio/background.mp3")
        self.background.loop()
        
        
    def update(self):
        if self.screen == 0:
            self.mainMenu()
            
        elif self.screen == 2:
            textAlign(CENTER)
            textMode(CENTER)
            textSize(70)
            text("WINN!!", self.w / 2, self.h / 2)
            
        elif self.screen == 1 and self.nemo.alive:
            self.bg.display()
            self.nemo.display()
            
            #check for win or level end (idky 5 but thats how it works so :\)
            if len(self.preys) <= 5:
                self.screen = 2
            
            # the stars will apear every 25 seconds
            # the frame count part is because frame rate is 60fps so more than just one would apear without it
            if (floor((datetime.datetime.now() - self.start).total_seconds()) % 10 == 0) and (frameCount % 20 == 0 or frameCount == 1) and len(self.tokens) <= 10: 
                self.tokens.append(Token(random.randint(100, self.w - 100), random.randint(100, self.h - 100)))

            for token in self.tokens:
                token.display()
                
            for prey in self.preys:
                prey.display()
                
            # LEVEL, TIMER and SCORE
            textMode(CORNER)
            textFont(font)
            fill(255)
            
            textAlign(RIGHT)
            textSize(30)
            text("SCORE", self.w - 20, 40)
            
            textSize(22)
            text(str(self.score), self.w - 20, 65)
            
            textAlign(LEFT)
            textSize(30)
            text("LEVEL " + str(self.level), 20, 40)
            
            textSize(22)
            text(self.getTimer((datetime.datetime.now() - self.start).total_seconds()), 20, 65)
            
            # I placed the mousePressed here instead of using mousePressed() function at the end
            # cuz we need to check it every time the game updates
            # if we use mousePressed() at the end, it'll trigger the function just once
            if mousePressed:
                mouseHandler()
                
        
        else:
            textAlign(CENTER)
            textMode(CENTER)
            textSize(70)
            text("GAME OVER", self.w / 2, self.h / 2)
            
            if self.keyHandler[32] == True:
                self.screen = 1 
                global game
                game = Game(WIDTH, HEIGHT)
            
        
    # to get the TIMER format (M:S)
    def getTimer(self, seconds):
        minutes = floor(seconds / 60)
        
        timeString = ""
        
        if minutes > 0:
            timeString = str(minutes) + ":" + str(floor(seconds - (minutes * 60)))
        else:
            timeString = "0:" + str(floor(seconds))
            
        return timeString
    
    # for the MainMenu
    def mainMenu(self):
        pass


class Background():
    def __init__(self, w, h):
        self.bgImage = loadImage(path + "/images/marine.png")
        self.w = w
        self.h = h
        
        self.xShift = 0
        
        self.otherImages = []
        for i in range(3, 0, -1):
            self.otherImages.append(loadImage(path + "/images/" + str(i) + ".png"))
        
    def display(self):
        
        if game.nemo.direction == RIGHT:
            self.xShift += 2
        elif game.nemo.direction == LEFT: 
            self.xShift -= 2
        else:
            self.xShift = 0
        
        count = 1
        x = 0
        for img in self.otherImages:
            if count == 1:
                x = self.xShift//3
            elif count == 2:
                x = self.xShift//2
            else:
                x = self.xShift        
            
            widthR = x % self.w
            widthL = self.w - widthR
            
            #make the image wrap around
            imageMode(CORNER)
            image(img, 0, 0, widthL, self.h, widthR, 0, self.w, self.h)
            image(img, widthL, 0, widthR, self.h, 0, 0, widthR, self.h)
            
            count += 1
    
game = Game(WIDTH, HEIGHT)

def setup():
    size(WIDTH, HEIGHT)

def draw():
    background(game.bg.bgImage)
    game.update()
    
#i was thinking press enter if you lose or win(to go to the next level or something)
def keyPressed():
    if keyCode == 32: #and game.nemo.alive == False: # SPACEBAR
        print("hello space")
        game.keyHandler[32] = True
        
    if keyCode == 13:# ENTER
        print("hello enter")
        game.keyHandler[13] = True
    
    if keyCode == 27: #ESC
        print("hello esc")
        """end game? change game.alive to False basically 
        we don't have to use it it's just an option"""

# this is the main function that handles nemo's movement
def mouseHandler():
    
    # addition: rotate() fish while moving towards the diagonals
    
    # to get the center co-ordinates of our nemo instead of getting top left coordinates
    playerCenterX, playerCenterY = game.nemo.getCenterCoordinates()
    
    # posX and posY increment values
    # increment will be the speed of Fish
    # that's why I've used speed inside the Fish class
    # we can declare different speed for our nemo and other individual enemies as well as the shark
    increment = [0, 0]
    
    # if the mouse position is more than half of the nemo's size, we move Nemo, else it doesn't move
    if (mouseY - playerCenterY) < (-1) * (game.nemo.size / 2):
        increment[1] = -(game.nemo.speed)
        
    elif (mouseY - playerCenterY) > (game.nemo.size / 2):
        increment[1] = game.nemo.speed
    
    if (mouseX - playerCenterX) < (-1) * (game.nemo.size / 2):
        increment[0] = (-game.nemo.speed)
        
    elif (mouseX - playerCenterX) > (game.nemo.size / 2):
        increment[0] = game.nemo.speed
        
    # checking if the player is within the game window
    if game.nemo.posX + increment[0] < (game.w - game.nemo.size / 2) and game.nemo.posX + increment[0] > game.nemo.size / 2:
        game.nemo.posX += increment[0]
        
    if game.nemo.posY + increment[1] < (game.h - game.nemo.size / 2) and game.nemo.posY + increment[1] > game.nemo.size / 2:
        game.nemo.posY += increment[1] 
