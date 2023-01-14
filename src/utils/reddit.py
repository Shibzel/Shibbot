from asyncio import sleep, AbstractEventLoop, gather
from asyncpraw import Reddit as BaseReddit

from src.logging import Logger


logger = Logger(__name__)

class Reddit(BaseReddit):
    """This dumbass dev forgot to add a documentation."""

    def __init__(self, loop: AbstractEventLoop, two_af: bool=False, *args, **kwargs):
        self.loop = loop
        self.two_af = two_af
        self.running = True
        self.n_requests = 0  # Current number of requests.
        self.max_requests = 60 if self.two_af else 30  # per min

        super().__init__(user_agent=(f"Shibbot v1 (by /u/JeanLeShiba", "https://github.com/Shibzel/Shibbot/"), *args, **kwargs)
        
        self.loop.create_task(self.clear_requests_loop())
        
    async def close(self):
        logger.debug(f"Closing Reddit client.")
        self.running = False
        await super().close()

    async def clear_requests_loop(self):
        while self.running:
            await sleep(60.0)
            self.n_requests = 0

    async def get_sub(self, subreddit: str, limit: int=500):
        """Gets the latest hot submissions from a subreddit."""
        while self.n_requests >= self.max_requests:
            # Check every second if the number of requests is back to 0
            await sleep(1.0)
        self.n_requests += 1
        subreddit = await self.subreddit(subreddit)
        return [sub async for sub in subreddit.hot(limit=limit)]

    async def get_subs(self, subreddits: list, limit_per_subred: int=500):
        """Gets hot submissions from different subreddits."""
        submissions = []
        async def append_submits(subreddit):
            try:
                for sub in await self.get_sub(subreddit, limit=limit_per_subred):
                    submissions.append(sub)
            except Exception as e:
                logger.error(f"Failed fetching submissions from r/'{subreddit}' on Reddit.", e)
        tasks = [append_submits(subreddit) for subreddit in subreddits]
        await gather(*tasks)
        return submissions

    @staticmethod
    def sub_to_dict(submission, **kwargs: bool):
        """Returns a reddit submissions into a dictionnary.

        Existing attributes :
            "author": submission.author.name
            "created_utc": submission.created_utc
            "is_self": submission.is_self
            "name": submission.name
            "num_comments": submission.num_comments
            "over_18": submission.over_18
            "permalink": submission.permalink
            "score": submission.score
            "selftext": submission.selftext
            "spoiler": submission.spoiler
            "subreddit": submission.subreddit.name
            "title": submission.title
            "url": submission.url"""
        _dict = {}
        for key, value in kwargs.items():
            if value:
                _dict.update({key: getattr(submission, key, None)})
        return _dict