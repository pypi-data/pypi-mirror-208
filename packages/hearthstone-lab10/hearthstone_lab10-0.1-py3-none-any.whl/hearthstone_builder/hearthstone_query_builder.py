from hearthstone_builder import Query
from hearthstone_builder import Endpoint


class QueryBuilder:

    def __init__(self):
        self.query = None

    @staticmethod
    def builder():
        query_builder = QueryBuilder()
        query_builder.query = Query()
        query_builder.query.url = "https://omgvamp-hearthstone-v1.p.rapidapi.com"
        query_builder.query.headers = {
            "X-RapidAPI-Key": "fa1e60d34bmsha208a8c410fa0efp18f5bajsn3dfd102eb462",
            "X-RapidAPI-Host": "omgvamp-hearthstone-v1.p.rapidapi.com"
        }
        return query_builder

    def set_segment(self, segment: Endpoint):
        self.query.url = self.query.url + "/" + segment.value
        return self

    def set_segment_str(self, segment: str):
        self.query.url = self.query.url + "/" + segment
        return self

    def add_parameter(self, parameter: str, value: str):
        self.query.params[parameter] = value
        return self

    def build(self):
        return self.query
