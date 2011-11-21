from tkinter import Tk, Canvas, Button, Entry
import math
import random
import time

class Circle2D:
    def __init__(self, id, canvas, angle, radius=10, velocity=100):
        self.angle = angle
        self.radius = radius
        self.id = id
        self.canvas = canvas
        self.velocity = velocity
        self.vector = (self.velocity*math.cos(self.angle*(math.pi/180))),(self.velocity*math.sin(self.angle*(math.pi/180)))

    def update(self, elapsedTime):
        self.canvas.move(self.id, self.vector[0]*elapsedTime, self.vector[1]*elapsedTime)

    def setAngle(self, angle):
        self.angle = angle
        self.vector = (self.velocity*math.cos(self.angle*(math.pi/180))),(self.velocity*math.sin(self.angle*(math.pi/180)))

    def getX(self):
        return self.canvas.coords(self.id)[0] + self.radius

    def getY(self):
        return self.canvas.coords(self.id)[1] + self.radius
    
class Collision:
    def __init__(self, canvas, entity1, entity2, time):
        self.lineid = canvas.create_line(entity1.getX(), entity1.getY(), entity2.getX(), entity2.getY())
        self.textid = canvas.create_text(entity1.getX() - (entity1.getX() - entity2.getX())/2, entity1.getY() - (entity1.getY() - entity2.getY())/2, text=str(time))
        self.canvas = canvas
        self.entity1 = entity1
        self.entity2 = entity2
        self.time = time
        
    def update(self, elapsedtime):
        self.time = self.time - elapsedtime
        self.canvas.coords(self.lineid, (self.entity1.getX(), self.entity1.getY(), self.entity2.getX(), self.entity2.getY()))
        self.canvas.coords(self.textid, (self.entity1.getX() - (self.entity1.getX() - self.entity2.getX())/2, self.entity1.getY() - (self.entity1.getY() - self.entity2.getY())/2))
        self.canvas.itemconfigure(self.textid, text=str(self.time))

    def destroyMe(self):
        self.canvas.delete(self.lineid)
        self.canvas.delete(self.textid)

class World:
    def __init__(self, tk):
        self.running=True
        self.playing=False
        self.drawFPS=False
        self.tk = tk
        self.tk.protocol("WM_DELETE_WINDOW", self.endWorld)
        self.canvas = Canvas(tk, width=640, height=480, bg="white")
        self.canvas.pack()
        self.lastUpdateTime=0
        self.entities = []
        self.collisions = []
        self.initBindings()

    def initBindings(self):
        self.canvas.bind("<Button-1>", self.createLine)
        self.canvas.bind("<Button-3>", self.togglePlaying)
        self.canvas.bind("<B1-Motion>", self.moveLine)
        self.canvas.bind("<B1-ButtonRelease>", self.createCircle)
        self.tk.bind("r", lambda x: self.reset())

    def createLine(self, event):        
        self.currentLine = self.canvas.create_line(event.x, event.y, event.x, event.y)

    def moveLine(self, event):
        coords = self.canvas.coords(self.currentLine)
        self.canvas.coords(self.currentLine, coords[0], coords[1], event.x, event.y)

    def createCircle(self, event):
        coords = self.canvas.coords(self.currentLine)
        print(coords)
        x1 = coords[0]
        y1 = coords[1]
        x2 = event.x
        y2 = event.y
        if(x1==x2 and y1==y2):
            x1-=1
        distance = math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
        velocity = distance
        print("velocity = " + str(velocity))
        angleInRadians = math.acos((x2-x1)/distance)        
        angleInDegrees = math.degrees(angleInRadians)
        if(y1 > y2):
            angleInDegrees += (180-angleInDegrees)*2        
        radius = random.randint(10,30)
        circleId = self.canvas.create_oval(x1-radius,y1-radius,x1+radius,y1+radius, tags="circle", fill="#"+str(random.randint(100,999)))
        circle = Circle2D(circleId, self.canvas, angleInDegrees, radius,
                velocity)
        self.entities.append(circle)
        self.canvas.delete(self.currentLine)
        self.checkFutureCollisions(circle)
        #print(circleId, angleInDegrees)

    def loop(self):
        currentTime = time.time()
        elapsedTimeSinceLastUpdate = currentTime - self.lastUpdateTime
        if(currentTime - self.lastUpdateTime > 1/30):
            fps = 1/(currentTime - self.lastUpdateTime)
            self.lastUpdateTime = currentTime
            self.update(elapsedTimeSinceLastUpdate)
            if self.drawFPS:
                print("FPS : " + str(fps))
        self.canvas.update()

    def checkCollisions(self):
        current = 1
        for entity in self.entities:
            for other in self.entities[current:]:
                if self.checkCollision(entity, other):
                    self.handleCollision(entity, other)
            current += 1

    def checkCollision(self, first, second):
        distanceSquared = math.pow(first.getX() - second.getX(), 2) + math.pow(first.getY() - second.getY(), 2)
        collisionDistanceSquared = math.pow(first.radius + second.radius, 2)
        if (collisionDistanceSquared >= distanceSquared):
            return True
        return False

    def checkFutureCollisions(self, entity):
        for other in self.entities:
            if entity.id == other.id:
                continue
            self.checkFutureCollision(entity, other)            

    #   Uträkningar ! ( som är coola )
    #   a = Vx^2 + Vy^2
    #   b = 2(X*Vx + Y*Vy)
    #   c = X^2 + Y^2 - r^2
    #
    #   a*t^2 + b*t + c
    #   t^2 = -(b*t)/a - c/a
    #   t = -b/2 +- √( (-b/2*a)^2 - c/a)
    def checkFutureCollision(self, entity, other):
        deltaX, deltaY, deltaRadius, deltaVx, deltaVy = self.getDelta(entity, other)
        a = math.pow(deltaVx, 2) + math.pow(deltaVy, 2)
        b = (2*(deltaX*deltaVx)) + (2*(deltaY*deltaVy))
        c = math.pow(deltaX, 2) + math.pow(deltaY, 2) - math.pow(deltaRadius, 2)

        d = math.pow((-b)/(2*a), 2) - (c/a)
        
        #print("deltaX:", deltaX)
        #print("deltaY:", deltaY)
        #print("deltaRadius:", deltaRadius)
        #print("deltaVx:", deltaVx)
        #print("deltaVy:", deltaVy)
        #print("a:", a)
        #print("b:", b)
        #print("c:", c)
        #print("d:", d)
        
        if d >= 0:
            time = ((-b)/(2*a)) - math.sqrt(d)
            if(time >= 0):
                posX = entity.getX() + (entity.vector[0]*time)
                posY = entity.getY() + (entity.vector[1]*time)
                if not(posX < 0 or posX > 680 or posY < 0 or posY > 480):                    
                    self.createCollisionIfNotExisting(entity, other, time)
            
    def createCollisionIfNotExisting(self, entity1, entity2, time):
        for collision in self.collisions:
            if (collision.entity1.id == entity1.id and collision.entity2.id == entity2.id) or (collision.entity1.id == entity2.id and collision.entity2.id == entity1.id):
                return
        self.collisions.append(Collision(self.canvas, entity1, entity2, time))

    def getDelta(self, first, second):
        deltaX = second.getX() - first.getX()
        deltaY = second.getY() - first.getY()
        deltaRadius = second.radius + first.radius
        deltaVx = second.vector[0] - first.vector[0]
        deltaVy = second.vector[1] - first.vector[1]
        return (deltaX, deltaY, deltaRadius, deltaVx, deltaVy)
        
    def handleCollision(self, first, second):
        self.removeCollisionObject(first,second)
        firstAngle = first.angle
        secondAngle = second.angle
        first.setAngle(secondAngle)
        second.setAngle(firstAngle)
        self.checkFutureCollisions(first)
        self.checkFutureCollisions(second)

    def removeCollisionObject(self, first, second):
        for collision in self.collisions:
            if collision.entity1.id == first.id or collision.entity2.id == first.id or collision.entity1.id == second.id or collision.entity2.id == second.id:
                collision.destroyMe()
                self.collisions.remove(collision)

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
            self.checkFutureCollisions(entity)
        elif(y <= 0 or y+radius*2 >= h):
            angle = entity.angle
            entity.setAngle(angle+((180-angle)*2))
            self.checkFutureCollisions(entity)

    def reset(self):
        print("resetting")
        for i in self.entities:
            self.canvas.delete(i.id)
        self.entities = []
        for i in self.collisions:
            self.canvas.delete(i.lineid)
            self.canvas.delete(i.textid)
        collisions = []
        self.playing = False

    def togglePlaying(self, event):
        self.playing = not(self.playing)

    def update(self, elapsedTime):
        if self.playing:
            for entity in self.entities:
                entity.update(elapsedTime)
                self.checkBounds(entity)
            for collision in self.collisions:
                collision.update(elapsedTime)
            self.checkCollisions()

    def endWorld(self):
        self.running=False
        exit(0)

tk = Tk()
world = World(tk)
while(world.running):
    world.loop()    
