from abc import ABC, abstractmethod

class Vehicle(ABC):
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year
        self._mileage = 0
    
    @abstractmethod
    def start_engine(self):
        pass
    
    def get_info(self):
        return f"{self.year} {self.brand} {self.model}"

class Engine:
    def __init__(self, horsepower, fuel_type):
        self.horsepower = horsepower
        self.fuel_type = fuel_type
        self.is_running = False
    
    def start(self):
        self.is_running = True
        return "Engine started"
    
    def stop(self):
        self.is_running = False
        return "Engine stopped"

class Car(Vehicle):
    def __init__(self, brand, model, year, doors, engine):
        super().__init__(brand, model, year)
        self.doors = doors
        self.engine = engine
    
    def start_engine(self):
        return self.engine.start()
    
    def honk(self):
        return "Beep beep!"
    
    def drive(self, miles):
        self._mileage += miles
        return f"Driving {miles} miles"

class ElectricCar(Car):
    def __init__(self, brand, model, year, doors, battery_capacity):
        engine = Engine(0, "electric")
        super().__init__(brand, model, year, doors, engine)
        self.battery_capacity = battery_capacity
    
    def charge(self):
        return f"Charging {self.battery_capacity}kWh battery"
    
    def get_range(self):
        return f"Estimated range: {self.battery_capacity * 4} miles"

class Motorcycle(Vehicle):
    def __init__(self, brand, model, year, has_sidecar):
        super().__init__(brand, model, year)
        self.has_sidecar = has_sidecar
        self.engine = Engine(100, "gasoline")
    
    def start_engine(self):
        return self.engine.start()
    
    def wheelie(self):
        return "Performing a wheelie!"
    
    def ride(self, miles):
        self._mileage += miles
        return f"Riding {miles} miles" 