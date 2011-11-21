from tkinter import Tk, Canvas, Button, Entry
import math
import time

class Circle2D:
    def __init__(self, id, canvas, angle, radius=10, velocity=5):
        self.angle = angle
        self.radius = radius
        self.id = id
        self.canvas = canvas
        self.velocity = velocity
        self.vector = (self.velocity*math.cos(self.angle*(math.pi/180))),(self.velocity*math.sin(self.angle*(math.pi/180)))

    def update(self):
        self.canvas.move(self.id, self.vector[0], self.vector[1])

    def setAngle(self, angle):
        self.angle = angle
        self.vector = (self.velocity*math.cos(self.angle*(math.pi/180))),(self.velocity*math.sin(self.angle*(math.pi/180)))

class World:
    def __init__(self, tk):
        self.running=True        
        self.tk = tk        
        self.tk.protocol("WM_DELETE_WINDOW", self.endWorld)
        self.canvas = Canvas(tk, width=640, height=480, bg="white")
        self.canvas.pack()
        self.lastUpdateTime=0
        self.entities = []
        self.initBindings()

    def initBindings(self):
        self.canvas.bind("<Button-1>", self.createLine)
        self.canvas.bind("<B1-Motion>", self.moveLine)
        self.canvas.bind("<B1-ButtonRelease>", self.createCircle)

    def createLine(self, event):        
        self.currentLine = self.canvas.create_line(event.x, event.y, event.x, event.y)

    def moveLine(self, event):
        coords = self.canvas.coords(self.currentLine)
        self.canvas.coords(self.currentLine, coords[0], coords[1], event.x, event.y)

    def createCircle(self, event):
        coords = self.canvas.coords(self.currentLine)
        x1 = coords[0]
        y1 = coords[1]
        x2 = event.x
        y2 = event.y
        if(x1==x2 and y1==y2):
            x1-=1
        distance = math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
        angleInRadians = math.acos((x2-x1)/distance)        
        angleInDegrees = math.degrees(angleInRadians)
        if(y1 > y2):
            angleInDegrees += (180-angleInDegrees)*2        
        radius = 10
        circleId = self.canvas.create_oval(x1-radius,y1-radius,x1+radius,y1+radius, tags="circle", fill="yellow")
        circle = Circle2D(circleId, self.canvas, angleInDegrees, radius)
        self.entities.append(circle)
        self.canvas.delete(self.currentLine)
        print(circleId, angleInDegrees)

    def loop(self):
        currentTime = time.time()
        if(currentTime - self.lastUpdateTime > 1/30):
            fps = 1/(currentTime - self.lastUpdateTime)
            self.lastUpdateTime = currentTime
            self.update()
            print("FPS : " + str(fps))
        self.canvas.update()

    def collisionCheck(self, entity):
        for other in self.entities:
            coords = self.canvas.coords(entity.id)
            x1 = coords[0]+10
            y1 = coords[1]+10
            r1 = entity.radius
            coords = self.canvas.coords(other.id)
            x2 = coords[0]+10
            y2 = coords[1]+10
            r2 = entity.radius
            distanceSq = math.pow((x1-x2),2)+math.pow((y1-y2),2)
            if(r1*r2 > distanceSq):
                entity.setAngle(entity.angle-180)
                other.setAngle(other.angle-180)

    def checkBounds(self, entity):
        coords = self.canvas.coords(entity.id)
        x = coords[0]
        y = coords[1]     
        radius = entity.radius
        #w = self.canvas["width"]
        w = 640
        #h = self.canvas["height"]
        h = 480
        if(x <= 0 or x+radius*2 >= w):
            angle = entity.angle
            entity.setAngle(angle+180-((angle-180)*2))
        elif(y <= 0 or y+radius*2 >= h):
            angle = entity.angle
            entity.setAngle(angle+((180-angle)*2))

    def update(self):
        for entity in self.entities:
            entity.update()
            self.checkBounds(entity)
            self.collisionCheck(entity)            

    def endWorld(self):
        self.running=False
        exit(0)


tk = Tk()
world = World(tk)
while(world.running):
    world.loop()    
