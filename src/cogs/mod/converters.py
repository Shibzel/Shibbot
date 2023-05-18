from datetime import datetime, timedelta
from discord.ext import commands
import re

from .lang import English

def secs_to_humain(lang: English, seconds: int | float):
    days, rem = divmod(int(seconds), 86400)
    if days:
        return f"{days} {lang.DAYS}"
    
    hours, rem = divmod(rem, 3600)
    if hours:
        return f"{hours} {lang.HOURS}"
    
    minutes, sec = divmod(rem, 60)
    if minutes:
        return f"{minutes} {lang.MINUTES}"
    
    return f"{sec or 1} {lang.SECONDS}"

class ArgToSeconds(commands.Converter):
    """Converter that returns a `_Duration` object."""
    
    @staticmethod
    async def convert(_, argument: str = None):
        if not argument:
            return
        
        try:
            duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
            seconds = sum(
                int(num) * duration[typ]
                for num, typ in re.findall(r'(\d+)([smhd])', argument)
            )
            return (datetime.utcnow() + timedelta(seconds=seconds)).timestamp()
        except (ValueError,) as exc:
            raise commands.BadArgument from exc

