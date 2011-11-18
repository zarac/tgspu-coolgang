from tkinter import *
import random
import math

class Oval():
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.velocity = random.random()/20
        self.angle = random.randint(0,360)

    def printValues(self):
        print(self.id,self.x,self.y,self.velocity,self.angle)

    def update(self, canvas):
        newX = self.velocity * math.cos(self.angle*(math.pi/180))
        newY = self.velocity * math.sin(self.angle*(math.pi/180))
        canvas.move(self.id, newX, newY)

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.createWidgets()
        self.pack()
        master.bind("<Button-1>", self.leftMouseDown)
        master.bind("<B1-Motion>", self.leftMouseDownMove)
        master.bind("<3>", self.rightMouseDown)
        master.bind("<Key>", self.keyPressed)
        self.counter=0
        self.ovals = list()
        self.running=False

    def createWidgets(self):
        self.canvas = Canvas(self,width=600,height=400)
        self.canvas.pack()
        self.label = Label(self, text="Stopped")
        self.label.pack(side="right")
        
    def rightMouseDown(self,event):
        if(self.currentOval>0):
            self.canvas.itemconfigure(self.currentOval,fill="yellow")
            self.currentOval=0

    def leftMouseDown(self, event):
        selectedOval = self.canvas.find_overlapping(event.x, event.y,event.x,event.y)
        if(len(selectedOval)==0):
            if(self.counter > 0):
                self.canvas.itemconfigure(self.counter, fill="yellow")
            x = event.x
            y = event.y
            self.currentOval=self.canvas.create_oval(x-10,y-10,x+10,y+10,tags=self.counter,fill="green")
            self.ovals.append(Oval(x, y, self.currentOval))
            self.ovals[self.currentOval-1].printValues()
            self.counter+=1
        else:
            self.canvas.itemconfigure(self.currentOval, fill="yellow")
            self.canvas.itemconfigure(selectedOval, fill="green")
            self.currentOval=selectedOval[0]
        

    def leftMouseDownMove(self, event):
        self.canvas.coords(self.currentOval, event.x-10, event.y-10, event.x+10,event.y+10)

    def keyPressed(self, event):
        self.running=not(self.running)
        if(self.running):
            self.label["text"] = "Running"
        else:
            self.label["text"] = "Stopped"

    def updater(self):
        while True:
            self.update()
            if(self.running):
                for oval in self.ovals:
                    oval.update(self.canvas)

root = Tk()
app = Application(master=root)
app.updater()
