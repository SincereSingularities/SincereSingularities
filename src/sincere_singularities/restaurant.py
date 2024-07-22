from typing import Any

import disnake

class Restaurant:
    def __init__(self, restaurant_json: Any):
        self.restaurant_json = restaurant_json

        self.name = restaurant_json['name']
        

    def enter_menu(self, inter: disnake.MessageInteraction):
        print(f"Restaurant {self.name} is entering menu")
