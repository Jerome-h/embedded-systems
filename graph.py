from matplotlib import pyplot as plt
# -*- coding: utf-8 -*-

def graph(temps,refresh):

    plt.plot(temps,'r',label='^C',marker='o')
    plt.legend()

    axes = plt.gca()
    

    plt.draw()
    plt.pause(refresh)
    plt.clf()