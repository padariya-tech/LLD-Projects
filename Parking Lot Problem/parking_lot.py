from abc import ABC , abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import IntEnum
from typing import Dict, List, Optional
from uuid import uuid4

class VehicleSize(IntEnum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class Vehicle(ABC):

    def __init__(self, license_plate:str) -> None:

        if not license_plate:
            raise ValueError("License plate cannot be empty")
        
        self.license_plate = license_plate


    @property
    @abstractmethod
    def size(self) -> VehicleSize:

        raise NotImplementedError
    
class Motorcycle(Vehicle):

    @property
    def size(self) -> VehicleSize:
        return VehicleSize.SMALL
    
class Car(Vehicle):

    @property
    def size(self) -> VehicleSize:
        return VehicleSize.MEDIUM
    
class Truck(Vehicle):

    @property
    def size(self) -> VehicleSize:
        return VehicleSize.LARGE
    
class ParkingSpot(ABC):

    def __init__(self, spot_number: int) -> None:
        self.spot_number = spot_number
        self.vehicle: Optional[Vehicle] = None

    def is_available(self) -> bool:
        return self.vehicle is None
    
    def occupy(self,vehicle:Vehicle) -> None:

        if not self.is_available():
            raise ValueError(f"Spot {self.spot_number} is already occupied")

        if vehicle.size > self.size:
            raise ValueError("Vehicle is too large for this parking spot")
        
        self.vehicle = vehicle

    def vacate(self) -> None:

        if self.is_available():
            raise ValueError(f"Spot {self.spot_number} is already empty")
        
        self.vehicle = None

    @property
    @abstractmethod
    def size(self) -> VehicleSize:
        raise NotImplementedError
    

class CompactSpot(ParkingSpot):

    @property
    def size(self) -> VehicleSize:
        return VehicleSize.MEDIUM

class RegularSpot(ParkingSpot):

    @property
    def size(self) -> VehicleSize:
        return VehicleSize.MEDIUM
    
class OversizedSpot(ParkingSpot):

    @property
    def size(self) -> VehicleSize:
        return VehicleSize.LARGE
    

class ParkingManager:
    def __init__(self, spots_by_size: Dict[VehicleSize, List[ParkingSpot]]) -> None:
        # These lists contain currently available spots only.
        self.available_spots = {
            size: list(spots_by_size.get(size, []))
            for size in VehicleSize
        }
        self.vehicle_to_spot: Dict[Vehicle, ParkingSpot] = {}

    def find_spot_for_vehicle(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        # Search from the smallest compatible spot size upward.
        for size in VehicleSize:
            if size >= vehicle.size:
                for spot in self.available_spots[size]:
                    if spot.is_available():
                        return spot
        return None

    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        if vehicle in self.vehicle_to_spot:
            raise ValueError("This vehicle is already parked")

        spot = self.find_spot_for_vehicle(vehicle)
        if spot is None:
            return None

        spot.occupy(vehicle)
        self.available_spots[spot.size].remove(spot)
        self.vehicle_to_spot[vehicle] = spot
        return spot

    def unpark_vehicle(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        spot = self.vehicle_to_spot.pop(vehicle, None)
        if spot is None:
            return None

        spot.vacate()
        self.available_spots[spot.size].append(spot)
        return spot


@dataclass
class Ticket:
    ticket_id: str
    vehicle: Vehicle
    parking_spot: ParkingSpot
    entry_time: datetime
    exit_time: Optional[datetime] = None


    def calculate_parking_duration(self, end_time: Optional[datetime] = None) -> Decimal:

        end = self.exit_time or end_time or datetime.now()
        if end < self.entry_time:
            raise ValueError("Exit time cannot be before entry time")
        
        minutes = (end - self.entry_time).total_seconds() / 60
        return Decimal(str(minutes))
    
class FareStrategy(ABC):

    @abstractmethod
    def calculate_fare(self,ticket:Ticket,input_fare: Decimal) -> Decimal:
        raise NotImplementedError
    
class BaseFareStrategy(FareStrategy):
    SMALL_VEHICLE_RATE = Decimal("1.0")
    MEDIUM_VEHICLE_RATE = Decimal("2.0")
    LARGE_VEHICLE_RATE = Decimal("3.0")

    def calculate_fare(self, ticket: Ticket, input_fare: Decimal) -> Decimal:
        rates = {
            VehicleSize.SMALL: self.SMALL_VEHICLE_RATE,
            VehicleSize.MEDIUM: self.MEDIUM_VEHICLE_RATE,
            VehicleSize.LARGE: self.LARGE_VEHICLE_RATE,
        }
        rate_per_minute = rates[ticket.vehicle.size]
        return input_fare + rate_per_minute * ticket.calculate_parking_duration()

class PeakHoursFareStrategy(FareStrategy):

    PEAK_HOURS_MULTIPLER = Decimal("1.5")

    @staticmethod
    def is_peak_hour(time: datetime) -> bool:

        hour = time.hour
        return (7 <= hour <= 10) or (16 <= hour <= 19)
    
    def calculate_fare(self, ticket, input_fare):
        
        if self.is_peak_hour(ticket.entry_time):
            return input_fare*self.PEAK_HOURS_MULTIPLER
        
        return input_fare
    

class FareCalculator:

    def __init__(self,fare_strategies: List[FareStrategy]) -> None:

        self.fare_strategies = list(fare_strategies)

    def calculate_fare(self, ticket:Ticket) -> Decimal:

        fare = Decimal("0")

        for strategy in self.fare_strategies:
            fare = strategy.calculate_fare(ticket,fare)

        return fare
    

class ParkingLot:

    def __init__(
            self,
            parking_manager: ParkingManager,
            fare_calculator: FareCalculator,
    )-> None:
        self.parking_manager = parking_manager
        self.fare_calculator = fare_calculator


    def enter_vehicle(self,vehicle:Vehicle) -> Optional[Ticket]:


        spot = self.parking_manager.park_vehicle(vehicle)
        if spot is None:
            return None
        
        return Ticket(
            ticket_id=str(uuid4()),
            vehicle=vehicle,
            parking_spot=spot,
            entry_time=datetime.now(),
        )
    
    def leave_vehicle(self,ticket:Ticket) -> Decimal:

        if ticket is None:
            raise ValueError("Ticket can not be None")
        
        if ticket.exit_time is not None:
            raise ValueError("Vehicle has already exited")
        
        ticket.exit_time = datetime.now()

        fare = self.fare_calculator.calculate_fare(ticket)

        spot = self.parking_manager.unpark_vehicle(ticket.vehicle)

        if spot is None:
            raise ValueError("Vehicle is not registered as parked")
        
        return fare
    

if __name__ == "__main__":

    spots = {
        VehicleSize.SMALL : [CompactSpot(1), CompactSpot(2)],
        VehicleSize.MEDIUM : [RegularSpot(3), RegularSpot(4)],
        VehicleSize.LARGE: [OversizedSpot(5)]
    }

    manager = ParkingManager(spots)

    calculator = FareCalculator([BaseFareStrategy(),PeakHoursFareStrategy()])

    parking_lot = ParkingLot(manager,calculator)

    car = Car("GJ03AB1234")

    ticket = parking_lot.enter_vehicle(car)

    if ticket is None:
        print("No parking spot available")

    else:
        print(f"Ticket ID: {ticket.ticket_id}")
        print(f"Vehicle: {ticket.vehicle.license_plate}")
        print(f"Spot: {ticket.parking_spot.spot_number}")

    fare = parking_lot.leave_vehicle(ticket)

    print(fare)