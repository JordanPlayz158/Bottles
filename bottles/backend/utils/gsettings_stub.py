from bottles.backend.logger import Logger

logging = Logger()


class GSettingsStub:
    def __init__(self, is_cli=False):
        self.is_cli = is_cli

    def get_boolean(self, key: str) -> bool:
        if not self.is_cli:
          logging.warning(f"Stub GSettings key {key}=False")
        return False
