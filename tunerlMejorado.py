#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 11:07:14 2022

@author: mat
"""

"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process, Manager
from multiprocessing import Value

SOUTH = 0
NORTH = 1

NCARS = 5

class Monitor():
    def __init__(self):
        self.manager = Manager()
        self.mutex = Lock()
        self.inTunnel = Value('i',0)
        self.direction = Value('i',0)
        self.waiting = self.manager.list([0,0])
        self.permission = Value('i',1)
        self.semaphore= Condition(self.mutex)
        #self.empty= Condition(self.mutex)
        self.carDir= None
                
    def car_dir(self, car_direction):
        self.carDir = car_direction


    def validTunnel(self):
        return self.direction.value == self.carDir and self.permission != 0
    
    def emptyTunnel(self):
        return self.inTunnel == 0
    
    def wants_enter(self, car_direction):
        self.mutex.acquire()
        self.waiting[car_direction] += 1
        print('aumenta el waiting' + str(self.waiting))
        
        self.car_dir(car_direction)
        self.semaphore.wait_for(self.validTunnel)
        print('ha entrado con este permiso: ' + str(self.permission.value))
        self.permission.value -=1
        self.inTunnel.value += 1
        
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        self.inTunnel.value -= 1
        self.waiting[direction] -=1
        if self.permission.value == 0:
            print('el permiso deberia ser 0 :' + str(self.permission.value))
            #self.empty.wait_for(self.emptyTunnel)
            self.direction.value = (self.direction.value +1 )%2
            print('cambio de dirección a: ' + str(self.direction.value))
            self.permission.value = self.waiting[self.direction.value]
            #self.empty.notify()
       
        self.semaphore.notify()
        self.mutex.release()

def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel", flush=True)
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")



def main():
    monitor = Monitor()
    cid = 0
    cars = []
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        cars.append(p)
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s
    
    for c in cars:
        c.join()

if __name__ == "__main__":
 main()

