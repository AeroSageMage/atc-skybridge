from dataclasses import dataclass
from typing import Optional
import time
from datetime import datetime
import math

@dataclass
class AircraftState:
    """Class to hold aircraft state information"""
    # Basic aircraft info
    callsign: str = 'aabbcc'
    type: str = ''
    position: str = ''
    altitude: str = ''
    heading: str = ''
    latitude: float = 0.0
    longitude: float = 0.0
    ground_speed: float = 0.0
    bank: float = 0.0
    pitch: float = 0.0
    vertical_speed: int = 0
    on_ground: bool = True
    
    # Additional SimAPI variables
    engine_type: int = 1  # 0=Piston, 1=Jet, 2=None, 3=Helo, 4=Unsupported, 5=Turboprop
    total_weight: int = 150000  # in pounds
    sea_level_pressure: int = 2992  # in inHg (29.92)
    magvar: int = 0  # magnetic variation
    typical_descent_rate: int = 1000  # in feet per minute
    
    # Electrical and circuit states
    electrical_master_battery: bool = True
    circuit_com1: bool = True
    circuit_com2: bool = True
    
    # Environmental data
    ambient_wind_direction: int = 0  # in degrees true
    ambient_wind_velocity: int = 0  # in knots
    
    # Time data
    local_time: float = 0.0  # seconds since midnight
    zulu_time: float = 0.0  # seconds since midnight

class AircraftStateManager:
    """Manages aircraft state and provides methods to update it"""
    
    def __init__(self):
        self.state = AircraftState()
        self.last_altitude = 0
        self.last_time = 0
    
    def update_from_gps(self, gps_data, attitude_data=None):
        """Update aircraft state from GPS and attitude data"""
        if gps_data:
            # Update position and speed
            self.state.latitude = gps_data.latitude
            self.state.longitude = gps_data.longitude
            self.state.ground_speed = gps_data.ground_speed
            self.state.altitude = f"{gps_data.altitude} ft"
            self.state.position = f"{gps_data.latitude:.4f}, {gps_data.longitude:.4f}"
            
            # Use true_heading from attitude data if available, otherwise use track from GPS
            heading = attitude_data.true_heading if attitude_data else gps_data.track
            self.state.heading = f"{heading:.1f}°"
            
            # Update vertical speed
            self.state.vertical_speed = self._calculate_vertical_speed(gps_data.altitude)
            
            # Update on ground status
            self.state.on_ground = gps_data.ground_speed < 0.1
            
            if attitude_data:
                self.state.bank = attitude_data.roll  # Note: roll is used for bank angle
                self.state.pitch = attitude_data.pitch
            
            # Update time data
            self._update_time_data()
            
            # Update magnetic variation based on position
            self._update_magnetic_variation()
    
    def _calculate_vertical_speed(self, current_altitude):
        """Calculate vertical speed in feet per minute"""
        current_time = time.time()
        time_diff = current_time - self.last_time
        if time_diff > 0:
            altitude_diff = current_altitude - self.last_altitude
            vertical_speed = (altitude_diff / time_diff) * 60  # Convert to feet per minute
            self.last_altitude = current_altitude
            self.last_time = current_time
            return int(vertical_speed)
        return 0
    
    def _update_time_data(self):
        """Update local and Zulu time"""
        now = datetime.now()
        self.state.local_time = now.hour * 3600 + now.minute * 60 + now.second
        # Zulu time is local time + UTC offset (simplified)
        self.state.zulu_time = self.state.local_time + (4 * 3600)  # Assuming UTC+4 for example
    
    def _update_magnetic_variation(self):
        """Update magnetic variation based on position using a simplified model"""
        lat, lon = self.state.latitude, self.state.longitude
        
        # Convert to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        
        # Calculate magnetic variation using a simplified model
        # This is based on the World Magnetic Model (WMM) approximation
        # For more accuracy, we should use a proper WMM library
        year = datetime.now().year
        year_fraction = year + (datetime.now().timetuple().tm_yday / 365.0)
        
        # Base variation calculation
        base_var = 11.0 * math.sin(lat_rad) + 0.5 * math.sin(2 * lat_rad) * math.cos(lon_rad)
        
        # Add secular variation (change over time)
        secular_var = 0.1 * (year_fraction - 2020.0)
        
        # Calculate final variation
        variation = base_var + secular_var
        
        # Round to nearest integer
        self.state.magvar = int(round(variation))
    
    def get_magnetic_heading(self) -> int:
        """Calculate magnetic heading from true heading"""
        true_heading = float(self.state.heading.strip('°'))
        magnetic_heading = true_heading - self.state.magvar
        
        # Normalize to 0-360 range
        magnetic_heading = magnetic_heading % 360
        
        return int(round(magnetic_heading))
    
    def update_callsign(self, callsign: str):
        """Update aircraft callsign"""
        self.state.callsign = callsign if callsign else 'aabbcc'
    
    def update_type(self, aircraft_type: str):
        """Update aircraft type"""
        self.state.type = aircraft_type
    
    def set_engine_type(self, engine_type: int):
        """Set engine type (0=Piston, 1=Jet, 2=None, 3=Helo, 4=Unsupported, 5=Turboprop)"""
        if 0 <= engine_type <= 5:
            self.state.engine_type = engine_type
    
    def set_total_weight(self, weight: int):
        """Set total aircraft weight in pounds"""
        if weight > 0:
            self.state.total_weight = weight
    
    def set_sea_level_pressure(self, pressure: int):
        """Set sea level pressure in inHg (e.g., 2992 for 29.92)"""
        if 2800 <= pressure <= 3100:  # Reasonable range check
            self.state.sea_level_pressure = pressure
    
    def set_typical_descent_rate(self, rate: int):
        """Set typical descent rate in feet per minute"""
        if rate > 0:
            self.state.typical_descent_rate = rate
    
    def set_electrical_state(self, master: bool, com1: bool, com2: bool):
        """Set electrical and circuit states"""
        self.state.electrical_master_battery = master
        self.state.circuit_com1 = com1
        self.state.circuit_com2 = com2
    
    def set_wind_data(self, direction: int, velocity: int):
        """Set ambient wind data"""
        if 0 <= direction <= 360:
            self.state.ambient_wind_direction = direction
        if velocity >= 0:
            self.state.ambient_wind_velocity = velocity
    
    def get_state(self) -> AircraftState:
        """Get current aircraft state"""
        return self.state 