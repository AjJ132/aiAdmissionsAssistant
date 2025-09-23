

class ScrapingControllerFactory:
    @staticmethod
    def create():
        return ScrapingController()


class ScrapingController:
    def __init__(self):
        self.name = "ScrapingController"

    def test(self):
        return "test"