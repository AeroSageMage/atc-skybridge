class TransponderManager:
    """Manages transponder state and operations"""
    
    def __init__(self):
        self.code = 1200  # Default VFR squawk
        self.mode = 3     # 0=Off, 1=Standby, 2=Test, 3=On, 4=Alt, 5=Ground
        self.ident = False
    
    def adjust_code(self, direction: int) -> int:
        """Adjust the transponder code"""
        new_code = self.code + direction
        if 0 <= new_code <= 7777:  # Valid range for transponder codes
            self.code = new_code
        return self.code
    
    def set_mode(self, mode: int):
        """Set the transponder mode"""
        if 0 <= mode <= 5:
            self.mode = mode
            # Reset IDENT when changing modes
            self.ident = False
    
    def toggle_ident(self) -> bool:
        """Toggle the IDENT state"""
        self.ident = not self.ident
        return self.ident
    
    def get_transponder_state(self):
        """Get current transponder state for SimAPI"""
        return {
            "TRANSPONDER CODE:1": self.code,
            "TRANSPONDER STATE:1": self.mode,
            "TRANSPONDER IDENT": 1 if self.ident else 0
        } 