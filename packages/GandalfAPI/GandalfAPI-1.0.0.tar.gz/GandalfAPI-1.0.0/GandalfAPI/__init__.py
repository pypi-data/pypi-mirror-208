from .main import MovieAPI, QuoteAPI


class GandalfAPI:
    def __init__(self, api_key):
        self.movie = MovieAPI(api_key)
        self.quote = QuoteAPI(api_key)
