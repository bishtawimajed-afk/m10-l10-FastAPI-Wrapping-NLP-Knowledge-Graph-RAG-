
def load(*args, **kwargs):
    class MockLanguage:
        def __call__(self, text):
            class MockDoc:
                def __init__(self):
                    self.ents = []
            return MockDoc()
    return MockLanguage()