from cleo.io.io import IO

from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry


class PoetPlugin(Plugin):

    def activate(self, poetry: Poetry, io: IO):
        io.write_line("PoetPlugin activated")
        # poetry.package.readme = "README.md"
        # ...
