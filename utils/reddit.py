import asyncio

import asyncpraw


class Reddit:
    """Simplified wrapper for Reddit based on asyncpraw."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        a2f: bool = False,
        *args, **kwargs
    ):
        self.loop = loop
        self.n_of_requests = 0  # current number of requests.
        self.max_requests = 60 if a2f else 30  # per min

        self.reddit = asyncpraw.Reddit(*args, **kwargs)

        self.running = True
        self.loop.create_task(self.requests_clear_loop())

    async def close(self):
        self.running = False
        await self.reddit.close()

    async def requests_clear_loop(self):
        while self.running is True:
            await asyncio.sleep(60.0)
            self.n_of_requests = 0

    async def get_subreddit(self, subreddit: str, limit: int = 1000):
        """Gets the latest hot submissions from a subreddit."""
        while self.n_of_requests >= self.max_requests:
            # Check every second if the number of requests is back to 0
            await asyncio.sleep(1.0)
        subreddit = await self.reddit.subreddit(subreddit)
        self.n_of_requests += 1
        return [sub async for sub in subreddit.hot(limit=limit)]

    async def get_subreddits(self, subreddits: list, limit_per_subred=1000):
        """Gets hot submissions from different submissions."""
        submissions = []

        async def append_submits(subreddit):
            for sub in await self.get_subreddit(subreddit, limit=limit_per_subred):
                submissions.append(sub)
        tasks = [append_submits(subreddit) for subreddit in subreddits]
        await asyncio.gather(*tasks)
        return submissions

    @staticmethod
    def sub_to_dict(submission, **kwargs: bool):
        """Returns a reddit submissions into a dictionnary.

        Existing attributes :
            "author": submission.author.name,
            "created_utc": submission.created_utc,
            "is_self": submission.is_self,
            "name": submission.name,
            "num_comments": submission.num_comments,
            "over_18": submission.over_18,
            "permalink": submission.permalink,
            "score": submission.score,
            "selftext": submission.selftext,
            "spoiler": submission.spoiler,
            "subreddit": submission.subreddit.name,
            "title": submission.title,
            "url": submission.url"""
        _dict = {}
        for key, value in kwargs.items():
            if value:
                _dict.update({key: submission.getattr(key, None)})
        return _dict
