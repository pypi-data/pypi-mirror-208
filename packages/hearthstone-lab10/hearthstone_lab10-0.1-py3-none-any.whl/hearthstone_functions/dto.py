from typing import Dict, Any


class Card:
    def __init__(self, card_id: str, dbf_id: int, name: str, card_set: str, card_type: str, rarity: str, cost: int = None,
                 attack: int = None, health: int = None, armor: int = None, elite: bool = False, player_class: str = None,
                 faction: str = None, race: str = None, text: str = None, flavor: str = None, artist: str = None,
                 img: str = None, img_gold: str = None, locale: str = None):
        self.card_id = card_id
        self.dbf_id = dbf_id
        self.name = name
        self.card_set = card_set
        self.card_type = card_type
        self.rarity = rarity
        self.cost = cost
        self.attack = attack
        self.health = health
        self.armor = armor
        self.elite = elite
        self.player_class = player_class
        self.faction = faction
        self.race = race
        self.text = text
        self.flavor = flavor
        self.artist = artist
        self.img = img
        self.img_gold = img_gold
        self.locale = locale

    @staticmethod
    def from_json(json_obj: Dict[str, Any]) -> 'Card':
        return Card(
            card_id=json_obj.get('cardId'),
            dbf_id=json_obj.get('dbfId'),
            name=json_obj.get('name'),
            card_set=json_obj.get('cardSet'),
            card_type=json_obj.get('type'),
            rarity=json_obj.get('rarity'),
            cost=json_obj.get('cost'),
            attack=json_obj.get('attack'),
            health=json_obj.get('health'),
            armor=json_obj.get('armor'),
            elite=json_obj.get('elite'),
            player_class=json_obj.get('playerClass'),
            faction=json_obj.get('faction'),
            race=json_obj.get('race'),
            text=json_obj.get('text'),
            flavor=json_obj.get('flavor'),
            artist=json_obj.get('artist'),
            img=json_obj.get('img'),
            img_gold=json_obj.get('imgGold'),
            locale=json_obj.get('locale'),
        )


# class Info:
#     def __init__(self, patch, hs_class, card_set, card_type, faction, quality, race, locale):
#         self.patch = patch
#         self.hs_class = hs_class
#         self.card_set = card_set
#         self.card_type = card_type
#         self.faction = faction
#         self.quality = quality
#         self.race = race
#         self.locale = locale
#
#     @staticmethod
#     def from_json(json_obj):
#         return Info(
#             json_obj["patch"],
#             json_obj["classes"],
#             json_obj["sets"],
#             json_obj["types"],
#             json_obj["factions"],
#             json_obj["qualities"],
#             json_obj["races"],
#             json_obj["locales"]
#         )
#
#
# class CardBack:
#     def __init__(self, card_back_id, name, description, source, enabled, img, img_animated, sort_category, sort_order, locale):
#         self.card_back_id = card_back_id
#         self.name = name
#         self.description = description
#         self.source = source
#         self.enabled = enabled
#         self.img = img
#         self.img_animated = img_animated
#         self.sort_category = sort_category
#         self.sort_order = sort_order
#         self.locale = locale
#
#     @staticmethod
#     def from_json(json_obj):
#         return CardBack(
#             json_obj["cardBackId"],
#             json_obj["name"],
#             json_obj["description"],
#             json_obj["source"],
#             json_obj["enabled"],
#             json_obj["img"],
#             json_obj["imgAnimated"],
#             json_obj["sortCategory"],
#             json_obj["sortOrder"],
#             json_obj["locale"]
#         )
