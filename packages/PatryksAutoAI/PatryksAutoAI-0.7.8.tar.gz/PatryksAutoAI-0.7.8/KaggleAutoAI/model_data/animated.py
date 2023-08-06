from matplotlib.animation import FuncAnimation
from itertools import count
import matplotlib.pyplot as plt

class Animated():
    def __init__(self):
        self.x_val = []
        self.y_val = []
        self.fig = None
        self.ax = None
        self.x_label = None
        self.y_label = None

    def create_animation(self, i):
        plt.cla()
        plt.plot(self.x_val, self.y_val)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)


    def start(self):
        anim = FuncAnimation(fig=self.fig, 
                            func=self.create_animation,
                            interval=1000)
        plt.plot()