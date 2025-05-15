from src.types import OperatingSystem


def router_login_rules(self: OperatingSystem) -> list:
    rules = []

    if self.trigger_sequence is not None:
        rules += [(self.trigger_sequence, '\n')]

    if self.login is not None:
        rules += [('ogin:', self.login)]
    if self.password is not None:
        rules += [('assword:', self.password)]

    return rules
