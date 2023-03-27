"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

#nombres de los turnos y las direcciones
SOUTH = 1
NORTH = 0
PED = 2
NULL=-1

#faltan los notify

NCARS = 4
NPED = 4
TIME_CARS_NORTH = 0.5  # a new car enters each 0.5s
TIME_CARS_SOUTH = 0.5  # a new car enters each 0.5s
TIME_PED = 5 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (30, 10) # normal 1s, 0.5s

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.turn=Value('i', -1)
        self.nCN = Value('i', 0)
        self.nCS = Value('i', 0)
        self.nP = Value('i', 0)
        self.wCS = Value('i', 0)
        self.wCN = Value('i', 0)
        self.wP = Value('i', 0)
        
        self.esTurnoN = Condition(self.mutex)
        self.esTurnoS = Condition(self.mutex)
        self.esTurnoP = Condition(self.mutex)
        self.puedePasarCN = Condition(self.mutex)
        self.puedePasarCS = Condition(self.mutex)
        self.puedePasarP = Condition(self.mutex)

    def noHayNadieSur(self):
        return self.nCN.value == 0 and self.nP.value == 0 

    def surTurno(self):
        return self.turn.value == SOUTH or self.turn.value == NULL
    
    def noHayNadieNorte(self):
        return self.nCS.value == 0 and self.nP.value == 0 

    def norteTurno(self):
        return self.turn.value == NORTH or self.turn.value == NULL

    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        if direction==SOUTH :
            self.wCS.value += 1
            self.esTurnoS.wait_for(self.surTurno)
            if self.turn.value == NULL :
                    self.turn.value = SOUTH       
            self.puedePasarCS.wait_for(self.noHayNadieSur)
            self.wCS.value -= 1
            self.nCS.value=self.nCS.value + 1
            
        elif direction==NORTH :
            self.wCN.value += 1
            self.esTurnoN.wait_for(self.norteTurno)
            if self.turn.value == NULL :
                    self.turn.value = NORTH
            self.puedePasarCN.wait_for(self.noHayNadieNorte)
            self.wCN.value -= 1
            self.nCN.value=self.nCN.value + 1
            
            
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire() 
        if direction==SOUTH :
             #igual habria que pone run error si ncs=0
            self.nCS.value -= 1
            
            if self.turn.value == SOUTH:
                
                if self.wCN.value > 0:
                    self.turn.value = NORTH #si hay cola al norte le damos el turno
                    self.esTurnoN.notify()
                    
                elif self.wP.value > 0:
                    self.turn.value = PED
                    self.esTurnoP.notify()
                    
                elif self.wCS.value == 0: #si no hay cola en ningun lao ponemos otra vez e turno nulo
                    self.turn.value = NULL
                      
                else :
                    pass #si solo hay cola en el sur no hacemos nada, seguimos pasando
                    
            else:
                pass #si el turno no es el que toca, llegamos y ya
             
            if self.turn.value == PED:
                self.puedePasarP.notify()
            
            elif self.turn.value == NORTH:
                self.puedePasarCN.notify()
            
            
            
            
        elif direction==NORTH:
            self.nCN.value -= 1
            
            if self.turn.value == NORTH:
                
                if self.wP.value > 0:
                    self.turn.value = PED #si hay cola al norte le damos el turno
                    self.esTurnoP.notify()
                    
                elif self.wCS.value > 0:
                    self.turn.value = SOUTH
                    self.esTurnoS.notify()
                    
                elif self.wCN.value == 0: #si no hay cola en ningun lao ponemos otra vez e turno nulo
                    self.turn.value = NULL
                    
                else: 
                    pass
                
            else:
                pass #si el turno no es north no hacemos nada, solo llegar
            
            if self.turn.value == PED:
                self.puedePasarP.notify()
            
            elif self.turn.value == SOUTH:
                self.puedePasarCS.notify()
            
            
        self.mutex.release()
        
        

    def noHayNadieAndar(self):
        return self.nCN.value == 0 and self.nCS.value == 0 

    def andarTurno(self):
        return self.turn.value == PED or self.turn.value == NULL


    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.wP.value += 1
        self.esTurnoP.wait_for(self.andarTurno)
        if self.turn.value == NULL :
                self.turn.value = PED
        self.puedePasarP.wait_for(self.noHayNadieAndar)
        self.wP.value -= 1
        self.nP.value=self.nP.value + 1
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        
        self.nP.value -= 1
        
        if self.turn.value == PED:
            
            if self.wCS.value > 0:
                self.turn.value = SOUTH #si hay cola al norte le damos el turno
                self.esTurnoS.notify()
                
            elif self.wCN.value > 0:
                self.turn.value = NORTH
                self.esTurnoN.notify()
                
            elif self.wP.value == 0: #si no hay cola en ningun lao ponemos otra vez e turno nulo
                self.turn.value = NULL
                
            else: 
                pass
        
        else:
            pass
        
        if self.turn.value == SOUTH:
            self.puedePasarCS.notify()
            
        elif self.turn.value == NORTH:
            self.puedePasarCN.notify()
            
        self.mutex.release()

    def __repr__(self) -> str:
        return f'TURNO= {self.turn.value}  nCN:\
{self.nCN.value} ,wCN: {self.wCN.value} \
nCS:  {self.nCS.value} ,wCS:\
{self.wCN.value} , NP . \
{self.nP.value} ,wP: {self.wP.value}            '

def delay_car_north() -> None:
    time.sleep(1)
    pass

def delay_car_south() -> None:
    time.sleep(1)
    pass

def delay_pedestrian() -> None:
    time.sleep(0.5)
    pass

def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction==NORTH :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")



def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))

    for p in plst:
        p.join()

def gen_cars(direction: int, time_cars, monitor: Monitor) -> None:
    cid = 0
    plst = []
    for _ in range(NCARS):
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/time_cars))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars_north = Process(target=gen_cars, args=(NORTH, TIME_CARS_NORTH, monitor))
    gcars_south = Process(target=gen_cars, args=(SOUTH, TIME_CARS_SOUTH, monitor))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars_north.start()
    gcars_south.start()
    gped.start()
    gcars_north.join()
    gcars_south.join()
    gped.join()


if __name__ == '__main__':
    main()
