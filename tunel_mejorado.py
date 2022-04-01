#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 11:05:48 2022

@author: mat
"""

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

NCARS = 10

class Monitor():
    def __init__(self):
        self.manager = Manager()
        self.mutex = Lock()
        self.direction = Value('i',-1)
        self.waiting = self.manager.list([0,0])
        self.permission = Value('i',1)
        self.semaphore= Condition(self.mutex)
        self.carDir= None
                
    def car_dir(self, car_direction):
        self.carDir = car_direction


    def validTunnel(self):
        return (self.direction.value == self.carDir and self.permission.value > 0)
    
    def wants_enter(self, car_direction):
        self.mutex.acquire()
        self.waiting[car_direction] += 1
        print('coches esperando' + str(self.waiting))
        
        self.car_dir(car_direction)
        if self.direction.value == -1:
            self.direction.value = car_direction 
        
        #if (self.waiting[(car_direction+1)%2]==0) and self.inTunnel == 0:
            #self.direction.value = car_direction 
        
        self.semaphore.wait_for(self.validTunnel)
        self.waiting[car_direction] -=1
        print('ha entrado con este permiso: ' + str(self.permission.value))
        self.permission.value -=1    
        self.mutex.release()

    def leaves_tunnel(self, car_direction):
        self.mutex.acquire()
        if self.permission.value == 0:
            print('self.permission.value = ' + str(self.permission.value))
            #self.empty.wait_for(self.emptyTunnel)
            if self.waiting[(car_direction+1)%2]!=0: #hay coches en el otro lado esperando 
                print('habia coches esperando en el otro lado, cambiamos direccíon') 
                self.direction.value = (car_direction +1 )%2
                print('cambio de dirección a: ' + str(self.direction.value)) 
                self.permission.value = self.waiting[self.direction.value]
                print('el permiso ahora es:' + str(self.permission.value))
            elif self.waiting[self.direction.value] == 0 and self.waiting[(self.direction.value+1)%2] == 0:
                self.permission.value = 1
                self.direction.value = -1
                print('no queda ningún coche esperando')
                print('el permiso ahora es:' + str(self.permission.value))
            else: 
                self.permission.value = self.waiting[self.direction.value]
                print('no hay coches esperando en dirección contraria, no cambiamos dirección')
                print('el permiso ahora es:' + str(self.permission.value))
        self.semaphore.notify_all()
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
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    #print(f"car {cid} heading {direction} out of the tunnel")



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