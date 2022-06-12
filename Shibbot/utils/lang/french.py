from .english import English


class French(English):
    def __init__(self):
        super().__init__()

        self.ping = {
            "embed": {
                "title": "🏓 Pong !",
                "description": "Latence de Shibbot : `{ping}ms`\nUtilisation machine : `CPU: {cpu}%` `RAM: {ram}%`"
            }
        }
