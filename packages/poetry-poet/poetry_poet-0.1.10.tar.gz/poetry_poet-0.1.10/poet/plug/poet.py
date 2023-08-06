from cleo.commands.command import Command
from poetry.plugins.application_plugin import ApplicationPlugin


class CustomCommand(Command):

    name = "poet"

    def handle(self) -> int:
        self.line("PoetCommand handled")
        return 0


def factory():
    return CustomCommand()


class PoetApplicationPlugin(ApplicationPlugin):
    def activate(self, application):
        application.command_loader.register_factory("poet", factory)
