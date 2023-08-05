"""
Copyright (c) 2023, Koen Martens <kmartens@sonologic.se>

Licensed under a hippocratic license. License terms can be found in
LICENSE.md or online:

https://firstdonoharm.dev/version/3/0/bds-cl-eco-extr-ffd-media-my-soc-sv-tal-xuar.md

"""
import os
from tempfile import TemporaryDirectory

import instagrapi
from PIL import Image
from instagrapi.exceptions import LoginRequired

from tootstagram.utils import download_file


class InstagramClient:
    def __init__(self, username: str, password: str, session_file_path: str) -> None:
        self._client = instagrapi.Client()
        self._client.delay_range = [1, 3]
        self._session_file_path = session_file_path
        self._username = username
        self._password = password
        self._authenticate()

    def _authenticate(self) -> None:
        if os.path.isfile(self._session_file_path):
            session = self._client.load_settings(self._session_file_path)
            self._client.set_settings(session)
            self._client.login(self._username, self._password)
            if not self._client_logged_in:
                print("Invalid session, logging in with username and password")
                old_session = self._client.get_timeline_feed()
                self._client.set_settings({})
                self._client.set_uuids(old_session['uuids'])
        else:
            self._client.login(self._username, self._password)
        if not self._client_logged_in:
            raise RuntimeError("Unable to authenticate with instagram")
        self._client.dump_settings(self._session_file_path)

    @property
    def _client_logged_in(self) -> bool:
        try:
            self._client.get_timeline_feed()
        except LoginRequired:
            return False
        return True

    def post_image(self, image_url: str, description: str, alt_text: str) -> None:
        extra_data = {}
        if alt_text:
            extra_data['custom_accessibility_caption'] = alt_text

        extension = os.path.splitext(os.path.basename(image_url))[1][1:]
        with TemporaryDirectory() as temp_dir:
            image_path = os.path.join(temp_dir, f'image.{extension}')
            download_file(image_url, image_path)
            image = Image.open(image_path)
            if image.format != 'JPEG':
                image_path = f"{image_path}.jpg"
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(image_path)
            self._client.photo_upload(
                image_path,
                description,
                extra_data=extra_data
            )

