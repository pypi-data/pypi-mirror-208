"""
Copyright (c) 2023, Koen Martens <kmartens@sonologic.se>

Licensed under a hippocratic license. License terms can be found in
LICENSE.md or online:

https://firstdonoharm.dev/version/3/0/bds-cl-eco-extr-ffd-media-my-soc-sv-tal-xuar.md

"""
import html
import re
from dataclasses import dataclass
from typing import List

import feedparser

from tootstagram.database import Database


@dataclass
class Media:
    url: str
    alt_text: str


@dataclass
class Toot:
    id: str
    description: str
    media: List[Media]


class MastodonClient:
    def __init__(self, account_url: str, database: Database) -> None:
        self.account_url = account_url
        self._database = database

    def get_images(self) -> List[feedparser.util.FeedParserDict]:
        toots = []
        feed = feedparser.parse(f"{self.account_url}.rss")
        for entry in feed.entries:
            if self._should_post(entry):
                toots += [self._extract_media(entry)]
        return toots

    def _should_post(self, entry: feedparser.util.FeedParserDict) -> bool:
        if 'media_content' not in entry:  # only post images
            return False

        if not any(x['medium'] == 'image' for x in entry['media_content']):
            return False

        if not any(not self._database.have_processed(entry['id'], x['url']) for x in entry['media_content']):
            return False

        return True

    def _extract_media(self, entry: feedparser.util.FeedParserDict) -> Toot:
        toot = Toot(
            id=entry['id'],
            description=html.unescape(re.sub('<[^>]*>', '', entry['summary'])),
            media=[]
        )

        for index in range(0, len(entry['media_content'])):
            media_content = entry['media_content'][index]
            if 'content' in entry and len(entry['media_content']) == len(entry['content']):
                alt_text = html.unescape(re.sub('<[^>]*>', '', entry['content'][index]['value']))
            else:
                alt_text = None

            if media_content['medium'] == 'image':
                toot.media += [Media(
                    url=media_content['url'],
                    alt_text=alt_text,
                )]
        return toot
