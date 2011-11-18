from tkinter import Tk, Canvas, Button, Entry
import math
import time

class Circle2D:
    def __init__(self, id, canvas, angle, radius=10, velocity=3):
        self.angle = angle
        self.radius = radius
        self.id = id
        self.canvas = canvas
        self.velocity = velocity
        self.vector = (self.velocity*math.cos(self.angle*(math.pi/180))),(self.velocity*math.sin(self.angle*(math.pi/180)))

    def update(self):
        self.canvas.move(self.id, self.vector[0], self.vector[1])

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
        distance = math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
        angleInRadians = math.acos((x2-x1)/distance)        
        angleInDegrees = math.degrees(angleInRadians)
        if(y1 > y2):
            angleInDegrees += (180-angleInDegrees)*2
        print(distance, angleInDegrees)
        radius = 10
        circleId = self.canvas.create_oval(x1-radius,y1-radius,x1+radius,y1+radius, tags="circle", fill="yellow")
        circle = Circle2D(circleId, self.canvas, angleInDegrees, 10)
        self.entities.append(circle)
        self.canvas.delete(self.currentLine)

    def loop(self):
        currentTime = time.time()
        if(currentTime - self.lastUpdateTime > 1/30):
            self.lastUpdateTime = currentTime
            self.update()
        self.canvas.update()

    def update(self):
        for entity in self.entities:
            entity.update()
            

    def endWorld(self):
        self.running=False
        exit(0)


tk = Tk()
world = World(tk)
while(world.running):
    world.loop()    
