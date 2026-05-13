class Order:
    def __init__(self, id, client, date, price):
        self.id = id
        self.client = client
        self.date = date
        self.price = price

    def to_dict(self):
        return {
            "id": self.id,
            "client": self.client,
            "date": self.date,
            "price": self.price
        }