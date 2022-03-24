"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 0
NORTH = 1

NCARS = 5

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.inTunnel = Value('i',0)
        self.direction = Value('i',0)
        self.semaphore= Condition(self.mutex)
        self.carDir= None
        
    def car_dir(self, car_direction):
        self.carDir = car_direction

    def validTunnel(self):
        return self.carDir == self.direction.value or self.inTunnel.value == 0
    
    def wants_enter(self, car_direction):
        self.mutex.acquire()
        self.car_dir(car_direction)
        self.semaphore.wait_for(self.validTunnel)
        self.direction.value = car_direction
        self.inTunnel.value += 1
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        self.inTunnel.value -= 1
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
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")



def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s


if __name__ == "__main__":
 main()
