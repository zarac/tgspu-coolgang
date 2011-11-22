from tkinter import Tk, Canvas, Button, Entry
import math
import random
import time

#Traceback (most recent call last):
#  File "Coolacoolgangetsapp.py", line 251, in <module>
#    world.loop()
#  File "Coolacoolgangetsapp.py", line 111, in loop
#    self.update(elapsedTimeSinceLastUpdate)
#  File "Coolacoolgangetsapp.py", line 241, in update
#    collision.update(elapsedTime)
#  File "Coolacoolgangetsapp.py", line 42, in update
#    self.canvas.coords(self.lineid, (self.entity1.getX(),
#  File "Coolacoolgangetsapp.py", line 23, in getX
#    return self.canvas.coords(self.id)[0] + self.radius
#IndexError: list index out of range

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

class Sphere:
    def __init__(self, x, y, angle, canvas, radius=20, velocity=200):
        self.x = x
        self.y = y
        self.z = random.randint(20, 80)
        self.angle = angle
        self.canvas = canvas
        self.radius = radius
        self.velocity = velocity
        #self.vector = [self.velocity*math.cos(self.angle*(math.pi/180)), (self.velocity*math.sin(self.angle*(math.pi/180))), random.random()]
        self.vector = [self.velocity*math.cos(self.angle*(math.pi/180)), (self.velocity*math.sin(self.angle*(math.pi/180))), random.randint(-15, 15)]
        print(self.vector)
        print(self.radius)
        drawSize = self.radius*(self.z/world.depth) + 5
        self.id = self.canvas.create_oval(x-drawSize, y-drawSize, x+drawSize, y+drawSize, fill="#"+str(random.randint(100,999)))
    
    def update(self, elapsedTime):
        self.x += self.vector[0] * elapsedTime
        self.y += self.vector[1] * elapsedTime
        self.z += self.vector[2] * elapsedTime
        #drawSize = (self.radius*0.75*2/100)*self.z + self.radius*0.25*2
        drawSize = self.radius*(self.z/world.depth) + 5
        self.canvas.coords(self.id, self.x-drawSize, self.y-drawSize, self.x+drawSize, self.y+drawSize)

    def bounceZ(self):
        self.vector[2] = -self.vector[2]

    def bounceY(self):
        self.vector[1] = -self.vector[1]

    def bounceX(self):
        self.vector[0] = -self.vector[0]

    def getX(self):
        return self.x

    def getY(self):
        return self.y
    
class Collision:
    def __init__(self, canvas, entity1, entity2, time):
        self.lineid = canvas.create_line(entity1.getX(), entity1.getY(),
                entity2.getX(), entity2.getY())
        self.textid = canvas.create_text(entity1.getX() - (entity1.getX() -
            entity2.getX())/2, entity1.getY() - (entity1.getY() -
                entity2.getY())/2, text=str(time))
        self.canvas = canvas
        self.entity1 = entity1
        self.entity2 = entity2
        self.time = time
        
    def update(self, elapsedtime):
        self.time = self.time - elapsedtime
        self.canvas.coords(self.lineid, (self.entity1.getX(),
            self.entity1.getY(), self.entity2.getX(), self.entity2.getY()))
        self.canvas.coords(self.textid, (self.entity1.getX() -
            (self.entity1.getX() - self.entity2.getX())/2, self.entity1.getY()
            - (self.entity1.getY() - self.entity2.getY())/2))
        self.canvas.itemconfigure(self.textid, text=str(self.time))

    def destroyMe(self):
        self.canvas.delete(self.lineid)
        self.canvas.delete(self.textid)

class World:
    def __init__(self, tk):
        self._debug=False
        self.running=True
        self.playing=False
        self.drawFPS=False
        self.tk = tk
        self.tk.protocol("WM_DELETE_WINDOW", self.endWorld)
        self.canvas = Canvas(tk, width=640, height=480, bg="white")
        self.canvas.pack()
        self.depth = 100
        self.lastUpdateTime=0
        self.entities = []
        self.collisions = []
        #self.initBindings2D()
        self.initBindings3D()

    def initBindings3D(self):
        self.canvas.bind("<Button-1>", self.createLine)
        self.canvas.bind("<Button-3>", self.togglePlaying)
        self.canvas.bind("<B1-Motion>", self.moveLine)
        self.canvas.bind("<B1-ButtonRelease>", self.createSphere)

    def initBindings2D(self):
        self.canvas.bind("<Button-1>", self.createLine)
        self.canvas.bind("<B1-Motion>", self.moveLine)
        self.canvas.bind("<B1-ButtonRelease>", self.createCircle)
        self.canvas.bind("<Button-3>", lambda x: self.togglePlaying())
        self.tk.bind("<space>", lambda x: self.togglePlaying())
        self.tk.bind("<BackSpace>", lambda x: self.reverse())
        self.tk.bind("r", lambda x: self.reset())
        self.tk.bind("c", lambda x: self.recalculateFutureCollisions())
        self.tk.bind("d", lambda x: self.toggleDebug())

    def createLine(self, event):        
        self.currentLine = self.canvas.create_line(event.x, event.y, event.x, event.y)

    def moveLine(self, event):
        coords = self.canvas.coords(self.currentLine)
        self.canvas.coords(self.currentLine, coords[0], coords[1], event.x, event.y)

    def createSphere(self, event):
        coords = self.canvas.coords(self.currentLine)
        x1 = coords[0]
        y1 = coords[1]
        x2 = event.x
        y2 = event.y
        if x1==x2 and y1==y2:
            x1-=1
        distance = math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
        angleInRadians = math.acos((x2-x1)/distance)        
        angleInDegrees = math.degrees(angleInRadians)
        if(y1 > y2):
            angleInDegrees += (180-angleInDegrees)*2        
        #radius = random.randint(10,30)
        sphere = Sphere(x1, y1, angleInDegrees, self.canvas)
        self.entities.append(sphere)
        self.canvas.delete(self.currentLine)
        self.checkFutureCollisions3D(sphere)
        
    def createCircle(self, event):
        coords = self.canvas.coords(self.currentLine)
        x1 = coords[0]
        y1 = coords[1]
        x2 = event.x
        y2 = event.y
        if(x1==x2 and y1==y2):
            x1-=1
        distance = math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))
        velocity = distance
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
        self.checkFutureCollisions2D(circle)
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

    def checkCollisions3D(self):
        current = 1
        for entity in self.entities:
            for other in self.entities[current:]:
                if(self.checkCollision3D(entity, other)):
                   self.handleCollision3D(entity, other)
            current += 1

    def checkCollisions2D(self):
        current = 1
        for entity in self.entities:
            for other in self.entities[current:]:
                if self.checkCollision2D(entity, other):
                    self.handleCollision2D(entity, other)
            current += 1

    def checkCollision3D(self, first, second):
        distanceSquared = math.pow(first.x - second.x, 2) + math.pow(first.y - second.y,2) + math.pow(first.z - second.z, 2)
        collisionDistanceSquared = math.pow(first.radius + second.radius, 2)
        if(collisionDistanceSquared >= distanceSquared):
            return True
        return False

    def checkCollision2D(self, first, second):
        distanceSquared = math.pow(first.getX() - second.getX(), 2) + math.pow(first.getY() - second.getY(), 2)
        collisionDistanceSquared = math.pow(first.radius + second.radius, 2)
        if (collisionDistanceSquared >= distanceSquared):
            return True
        return False

    def checkFutureCollisions3D(self, entity):
        for other in self.entities:
            if entity.id == other.id:
                continue
            self.checkFutureCollision3D(entity, other)

    def checkFutureCollisions2D(self, entity):
        for other in self.entities:
            if entity.id == other.id:
                continue
            self.checkFutureCollision2D(entity, other)            

    #   a = Vx^2 + Vy^2 + Vz^2
    #   b = 2(X*Vx + Y*Vy + Z*Vz)
    #   c = X^2 + Y^2 + Z^2 - r^2
    def checkFutureCollision3D(self, entity, other):
        deltaX, deltaY, deltaZ, deltaRadius, deltaVx, deltaVy, deltaVz = self.getDelta3D(entity, other)
        a = math.pow(deltaVx, 2) + math.pow(deltaVy, 2) + math.pow(deltaVz, 2)
        b = (2*(deltaX*deltaVx)) + (2*(deltaY*deltaVy)) + (2*(deltaZ*deltaVz))
        c = math.pow(deltaX, 2) + math.pow(deltaY, 2) + math.pow(deltaZ, 2) - math.pow(deltaRadius, 2)

        d = math.pow((-b)/(2*a), 2) - (c/a)

        if d >= 0:
            time = ((-b)/(2*a)) - math.sqrt(d)
            if(time >= 0):
                posX = entity.x + (entity.vector[0]*time)
                posY = entity.y + (entity.vector[1]*time)
                posZ = entity.z + (entity.vector[2]*time)
                if not(posX < 0 or posX > 680 or posY < 0 or posY > 480 or posZ < 0 or posZ > self.depth):
                    self.createCollisionIfNotExisting(entity, other, time)
            
    #   Uträkningar ! ( som är coola )
    #   a = Vx^2 + Vy^2
    #   b = 2(X*Vx + Y*Vy)
    #   c = X^2 + Y^2 - r^2
    #
    #   a*t^2 + b*t + c
    #   t^2 = -(b*t)/a - c/a
    #   t = -b/2 +- √( (-b/2*a)^2 - c/a)
    def checkFutureCollision2D(self, entity, other):
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
            if (collision.entity1.id == entity1.id and collision.entity2.id ==
                    entity2.id) or (collision.entity1.id == entity2.id and
                            collision.entity2.id == entity1.id):
                return
        if self._debug:
            print("collision created: " + str(entity1.id) + " <> " +
                    str(entity2.id) + " in " + str(time))
        self.collisions.append(Collision(self.canvas, entity1, entity2, time))

    def getDelta3D(self, first, second):
        deltaX = second.x - first.x
        deltaY = second.y - first.y
        deltaZ = second.z - first.z
        deltaRadius = second.radius + first.radius
        deltaVx = second.vector[0] - first.vector[0]
        deltaVy = second.vector[1] - first.vector[1]
        deltaVz = second.vector[2] - first.vector[2]
        return (deltaX, deltaY, deltaZ, deltaRadius, deltaVx, deltaVy, deltaZ)

    def getDelta2D(self, first, second):
        deltaX = second.getX() - first.getX()
        deltaY = second.getY() - first.getY()
        deltaRadius = second.radius + first.radius
        deltaVx = second.vector[0] - first.vector[0]
        deltaVy = second.vector[1] - first.vector[1]
        return (deltaX, deltaY, deltaRadius, deltaVx, deltaVy)

    def handleCollision3D(self, first, second):
        self.removeCollisionObject(first, second)
        firstVector = first.vector
        secondVector = second.vector
        first.vector = secondVector
        second.vector = firstVector
        self.checkFutureCollisions3D(first)
        self.checkFutureCollisions3D(second)
        
    def handleCollision2D(self, first, second):
        self.removeCollisionObject(first,second)
        # TODO : find extra distance and reverse it (add it to out angle)
        #distance = math.sqrt(math.pow(first.getX() - second.getX(), 2) +
                #math.pow(first.getY() - second.getY(), 2))
        firstAngle = first.angle
        secondAngle = second.angle
        first.setAngle(secondAngle)
        second.setAngle(firstAngle)
        self.checkFutureCollisions2D(first)
        self.checkFutureCollisions2D(second)

    def recalculateFutureCollisions(self):
        if self._debug:
            print("recalculateFutureCollisions():")
        for collision in self.collisions:
            self.canvas.delete(collision.lineid)
            self.canvas.delete(collision.textid)
        self.collisions = []
        current = 1
        for left in self.entities:
            if self._debug:
                print("left", left.id)
            for right in self.entities[current:]:
                if self._debug:
                    print("right", right.id)
                if left.id == right.id:
                    continue
                self.checkFutureCollision(left, right)            
            current += 1

    def removeCollisionObject(self, first, second):
        for collision in self.collisions:
            if collision.entity1.id == first.id or collision.entity2.id == first.id or collision.entity1.id == second.id or collision.entity2.id == second.id:
                collision.destroyMe()
                self.collisions.remove(collision)

    def checkBounds3D(self, entity):
        x = entity.x
        y = entity.y
        z = entity.z
        r = entity.radius
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])
        d = self.depth
        if(x-r <= 0 or x+r >= w):
            entity.bounceX()
            self.checkFutureCollisions3D(entity)
        if(y-r <= 0 or y+r >= h):
            entity.bounceY()
            self.checkFutureCollisions3D(entity)
        if(z <= 0 or z >= d):
            entity.bounceZ()
            self.checkFutureCollisions3D(entity)

    def checkBounds2D(self, entity):
        coords = self.canvas.coords(entity.id)
        x = coords[0]
        y = coords[1]     
        radius = entity.radius
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])
        # TODO : only reverse if direction is wrong (to allow outside balls to
        # travel inside)
        if(x < 0 or x+radius*2 >= w):
            angle = entity.angle
            entity.setAngle(angle+180-((angle-180)*2))
            self.checkFutureCollisions2D(entity)
            # TODO : find extra distance and reverse it (add it to out angle)
        elif(y < 0 or y+radius*2 >= h):
            angle = entity.angle
            entity.setAngle(angle+((180-angle)*2))
            self.checkFutureCollisions2D(entity)
            # TODO : find extra distance and reverse it (add it to out angle)

    def reverse(self):
        for entity in self.entities:
            entity.setAngle(entity.angle+180)
        self.recalculateFutureCollisions()

    def reset(self):
        for entity in self.entities:
            self.canvas.delete(entity.id)
        self.entities = []
        for collision in self.collisions:
            self.canvas.delete(collision.lineid)
            self.canvas.delete(collision.textid)
        collisions = []
        self.playing = False

    def toggleDebug(self, event):
        self._debug = not(self._debug)
        if self._debug:
            print("debug on")

    def togglePlaying(self, event):
        self.playing = not(self.playing)

    def update(self, elapsedTime):
        if self.playing:
            for entity in self.entities:
                entity.update(elapsedTime)
                #self.checkBounds2D(entity)
                self.checkBounds3D(entity)
            for collision in self.collisions:
                collision.update(elapsedTime)
                if collision.time < 0:
                    collision.destroyMe()
                    self.collisions.remove(collision)
            #self.checkCollisions2D()
            self.checkCollisions3D()

    def endWorld(self):
        self.running=False
        exit(0)

tk = Tk()
world = World(tk)
while(world.running):
    world.loop()    
