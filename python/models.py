class Merchant:
    def __init__(self, id, name, slug, user_rating, delivery_fee, distance):
        self.id = id
        self.name = name
        self.slug = slug
        self.user_rating = user_rating
        self.delivery_fee = delivery_fee
        self.distance = distance

class Item:
    def __init__(self, description, price, taxonomy, merchant_id,merchant_name, details):
        self.description = description
        self.details = details
        self.price = price
        self.taxonomy = taxonomy
        self.merchant_id = merchant_id
        self.merchant_name = merchant_name