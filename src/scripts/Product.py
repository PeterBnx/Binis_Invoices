class Product:
    def __init__(self, quantity, code, description, price, is_registered, brand_full, brand_short):
        self.quantity = quantity
        self.code = code
        self.description = description
        self.price = price
        self.is_registered = is_registered
        self.brand_full = brand_full
        self.brand_short = brand_short
    
    def to_dict(self):
        """Convert Product to dictionary with UTF-8 encoding"""
        return {
            "quantity": self.quantity,
            "code": str(self.code),
            "description": str(self.description),
            "price": str(self.price),
            "is_registered": self.is_registered,
            "brand_full": str(self.brand_full),
            "brand_short": str(self.brand_short)
        }