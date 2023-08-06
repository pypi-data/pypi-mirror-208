import requests


class HearthstoneRepositories:
    BASE = "https://omgvamp-hearthstone-v1.p.rapidapi.com"
    HEADERS = {
        "X-RapidAPI-Key": "fa1e60d34bmsha208a8c410fa0efp18f5bajsn3dfd102eb462",
        "X-RapidAPI-Host": "omgvamp-hearthstone-v1.p.rapidapi.com"
    }

    @staticmethod
    def get_info(locale: str = " "):
        params = {}
        if locale:
            params['locale'] = locale

        url = HearthstoneRepositories.BASE + "/info"
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def get_single_card(name: str,
                        collectible: int = 0,
                        locale: str = ""):
        params = {}
        if collectible:
            params['collectible'] = collectible
        if locale:
            params['locale'] = locale

        url = HearthstoneRepositories.BASE + "/cards/" + name
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def get_cards_by_class(hs_class: str,
                           health: int = 0,
                           durability: int = 0,
                           cost: int = 0,
                           attack: int = 0,
                           collectible: int = 0,
                           locale: str = ""):
        params = HearthstoneRepositories._create_dict(health, durability, cost, attack, collectible, locale)
        url = HearthstoneRepositories.BASE + "/cards/classes/" + hs_class
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def get_cards_by_race(race: str = "",
                          health: int = 0,
                          durability: int = 0,
                          cost: int = 0,
                          attack: int = 0,
                          collectible: int = 0,
                          locale: str = ""):
        params = HearthstoneRepositories._create_dict(health, durability, cost, attack, collectible, locale)
        url = HearthstoneRepositories.BASE + "/cards/races/" + race
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def get_cards_set(hs_set: str = "",
                      health: int = 0,
                      durability: int = 0,
                      cost: int = 0,
                      attack: int = 0,
                      collectible: int = 0,
                      locale: str = ""):
        params = HearthstoneRepositories._create_dict(health, durability, cost, attack, collectible, locale)
        url = HearthstoneRepositories.BASE + "/cards/sets/" + hs_set
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def get_cards_by_quality(quality: str = "",
                             health: int = 0,
                             durability: int = 0,
                             cost: int = 0,
                             attack: int = 0,
                             collectible: int = 0,
                             locale: str = ""):
        params = HearthstoneRepositories._create_dict(health, durability, cost, attack, collectible, locale)
        url = HearthstoneRepositories.BASE + "/cards/qualities/" + quality
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def get_cards_backs(locale: str = ""):
        params = {}
        if locale:
            params['locale'] = locale

        url = HearthstoneRepositories.BASE + "/cardbacks"
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def get_card_search(name: str,
                        collectible: int = 0,
                        locale: str = ""):
        params = {}
        if collectible:
            params['collectible'] = collectible
        if locale:
            params['locale'] = locale

        url = HearthstoneRepositories.BASE + "/cards/search/" + name
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def get_cards_by_faction(faction: str = "",
                             health: int = 0,
                             durability: int = 0,
                             cost: int = 0,
                             attack: int = 0,
                             collectible: int = 0,
                             locale: str = ""):
        params = HearthstoneRepositories._create_dict(health, durability, cost, attack, collectible, locale)
        url = HearthstoneRepositories.BASE + "/cards/factions/" + faction
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def get_cards_by_type(hs_type: str = "",
                          health: int = 0,
                          durability: int = 0,
                          cost: int = 0,
                          attack: int = 0,
                          collectible: int = 0,
                          locale: str = ""):
        params = HearthstoneRepositories._create_dict(health, durability, cost, attack, collectible, locale)
        url = HearthstoneRepositories.BASE + "/cards/types/" + hs_type
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def get_all_cards(health: int = 0,
                      durability: int = 0,
                      cost: int = 0,
                      attack: int = 0,
                      collectible: int = 0,
                      locale: str = ""):
        params = HearthstoneRepositories._create_dict(health, durability, cost, attack, collectible, locale)
        url = HearthstoneRepositories.BASE + "/cards"
        return HearthstoneRepositories._make_query(url, HearthstoneRepositories.HEADERS, params)

    @staticmethod
    def _make_query(url: str, headers: dict, params: dict = None):
        return requests.get(url, headers=headers, params=params).json()

    @staticmethod
    def _create_dict(health: int, durability: int, cost: int, attack: int, collectible: int, locale: str):
        my_dict = {}
        if health:
            my_dict['health'] = health
        if durability:
            my_dict['durability'] = durability
        if cost:
            my_dict['cost'] = cost
        if attack:
            my_dict['attack'] = attack
        if collectible:
            my_dict['collectible'] = collectible
        if locale:
            my_dict['locale'] = locale
        return my_dict
