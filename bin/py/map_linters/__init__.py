from collections.abc import Generator
import glob
import os


class Result():
    def __init__(self, filename, message, **kwargs):
        self.filename = filename
        self.message = message
        self.level = kwargs.get("level", "INFO")
        self.line = kwargs.get("line", 0)
        self.col = kwargs.get("col", 0)
        self.rule = kwargs.get("rule", "")


class Linter():
    def __init__(self, default_config: dict = {}, external_config: dict = {}):
        super(Linter, self).__init__()
        self.config = default_config
        self._update_config(external_config)

    def _update_config(self, config: dict = {}):
        """Update the linter configuration from an external source"""
        if not hasattr(self, "config"):
            print("Linter is missing config; setting empty")
            self.config = {}
        if self.__class__.__name__ in config.keys():
            self.config.update(config[self.__class__.__name__])

    def lint(self, target_file: str) -> Generator[Result]:
        """Stub function to perform the actual linting."""
        yield Result(filename="", message="")


def linters() -> Generator:
    """Generate a list of all known linters."""
    from importlib import import_module
    import inspect
    for module in glob.glob(os.path.join(os.path.dirname(__file__), "linter_*.py")):
        mod_name = os.path.basename(module).replace('.py', '')
        for name, cls in inspect.getmembers(import_module(f".{mod_name}", package="map_linters"), inspect.isclass):
            if issubclass(cls, Linter) and cls is not Linter:
                yield cls


class BaseFormatter():
    """Default result formatter to print results in PEP8 format"""
    def __init__(self):
        super(BaseFormatter, self).__init__()

    def format_result(self, result: Result):
        print(f"{result.filename}:{result.line}:{result.col}: "
              f"[{result.rule}] {result.level} {result.message}")
