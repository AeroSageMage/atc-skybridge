class RadioManager:
    """Manages radio frequencies and states"""
    
    def __init__(self):
        # Initialize COM1
        self.active_freq_1 = 118.700
        self.standby_freq_1 = 121.500
        self.com1_receive = True
        self.com1_transmit = True
        
        # Initialize COM2
        self.active_freq_2 = 118.000
        self.standby_freq_2 = 121.000
        self.com2_receive = True
        self.com2_transmit = False
    
    def adjust_frequency(self, radio_num: int, adjustment_type: str, direction: int):
        """Adjust the standby frequency for the specified radio"""
        if radio_num == 1:
            freq = self.standby_freq_1
        else:
            freq = self.standby_freq_2
            
        step = 1.0 if adjustment_type == 'coarse' else 0.005
        new_freq = freq + (direction * step)
        # Ensure frequency stays within valid range (118.000 - 136.975)
        new_freq = max(118.000, min(136.975, new_freq))
        
        if radio_num == 1:
            self.standby_freq_1 = new_freq
        else:
            self.standby_freq_2 = new_freq
            
        return new_freq
    
    def swap_frequencies(self, radio_num: int):
        """Swap active and standby frequencies for the specified radio"""
        if radio_num == 1:
            self.active_freq_1, self.standby_freq_1 = self.standby_freq_1, self.active_freq_1
            return self.active_freq_1, self.standby_freq_1
        else:
            self.active_freq_2, self.standby_freq_2 = self.standby_freq_2, self.active_freq_2
            return self.active_freq_2, self.standby_freq_2
    
    def set_active_frequency(self, radio_num: int, frequency: float):
        """Set the active frequency for the specified radio"""
        if radio_num == 1:
            self.active_freq_1 = frequency
        else:
            self.active_freq_2 = frequency
    
    def get_radio_state(self):
        """Get current radio state for SimAPI"""
        return {
            "COM ACTIVE FREQUENCY:1": self.active_freq_1,
            "COM ACTIVE FREQUENCY:2": self.active_freq_2,
            "COM RECEIVE:1": 1 if self.com1_receive else 0,
            "COM RECEIVE:2": 1 if self.com2_receive else 0,
            "COM TRANSMIT:1": 1 if self.com1_transmit else 0,
            "COM TRANSMIT:2": 1 if self.com2_transmit else 0
        } 