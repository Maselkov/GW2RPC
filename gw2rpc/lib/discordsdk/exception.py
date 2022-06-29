from .enum import Result


class DiscordException(Exception):
    pass


exceptions = {}

# we dynamically create the exceptions
for res in Result:
    exception = type(res.name, (DiscordException,), {})

    globals()[res.name] = exception
    exceptions[res] = exception


def get_exception(result):
    return exceptions.get(result, DiscordException)("result " + str(result.value))
