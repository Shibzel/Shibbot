import datetime

from discord.ext import commands
from .functions import remove_chars


class _Duration:
    def __init__(self, _datetime, raw_time, _type):
        self.datetime = _datetime
        self.raw_time = raw_time
        self.type = _type

    def __str__(self) -> str:
        return f"{self.raw_time} {self.type}"


class ArgToDuration(commands.Converter):
    """Converter that returns a `_Duration` object."""

    async def convert(self, ctx: commands.Context, argument: str = None):

        if not argument:
            return None  # Not sure that if I remove this condition the converter would return None
        try:
            if argument.endswith(("s", "sec", "second", "seconds")):
                raw_time, duration_type = int(remove_chars(
                    argument, "seconds ", "")), "second(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=raw_time)
            elif argument.endswith(("m", "min", "minute ", "minutes")):
                raw_time, duration_type = int(remove_chars(
                    argument, "minutes ", "")), "minute(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(minutes=raw_time)
            elif argument.endswith(("h", "hour", "hours")):
                raw_time, duration_type = int(
                    remove_chars(argument, "hours ", "")), "hour(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=raw_time)
            elif argument.endswith(("d", "day", "days")):
                raw_time, duration_type = int(
                    remove_chars(argument, "days ", "")), "day(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(days=raw_time)
            elif argument.endswith(("w", "week", "weeks")):
                raw_time, duration_type = int(
                    remove_chars(argument, "weeks ", "")), "week(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(weeks=raw_time)
            elif argument.endswith(("month", "months")):
                raw_time, duration_type = int(remove_chars(
                    argument, "months ", "")), "month(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=raw_time *
                                                                            2629800)  # Doesn't support "month" parameter
            # Who bans for a year ? Seriously
            elif argument.endswith(("y", "year", "years")):
                raw_time, duration_type = int(
                    remove_chars(argument, "years ", "")), "year(s)"
                _datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=raw_time*31557600)
            # This was tricky, I'm sure there's a better way to do this. If it's the case don't hesitate to tell me 😏
            return _Duration(
                _datetime,
                raw_time,
                duration_type
            )
        except (ValueError, NameError):
            raise commands.BadArgument
