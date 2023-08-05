import asyncio
import hashlib
from typing import Optional
import httpx
import logging
import re

from ripandtear.extractors.common import Common
from ripandtear.utils import rat_info
from ripandtear.utils.custom_types import UrlDictionary
from ripandtear.utils.tracker import Tracker

log = logging.getLogger(__name__)

re_folder_with_password = re.compile(
    r"(https?://)(gofile\.io)(/d/)(\w+|\w{8}-\w{4}-\w{4}-\w{4}-\w{12})~(\w+)")

re_folder = re.compile(
    r"(https?://)(gofile\.io)(/d/)(\w+|\w{8}-\w{4}-\w{4}-\w{4}-\w{12})")


class Gofile(Common):

    def __init__(self):
        log.debug("Getting api token")
        self.token = self.get_token()
        # print(self.token)
        self.website_token = '12345'

        self.tracker = Tracker.getInstance()

    async def run(self, url_dictionary: UrlDictionary) -> None:

        if re_folder_with_password.match(url_dictionary['url']):

            log.debug("url matches folder with password regex")

            temp = url_dictionary['url']
            temp = temp.split("~")

            url_dictionary['url'] = temp[0]
            content_id = re_folder.match(temp[0]).group(4)
            password = temp[1]
            await self.get_content(content_id, url_dictionary.copy(), password)

        elif re_folder.match(url_dictionary['url']):

            log.debug("url matches folder regex")
            content_id = re_folder.match(url_dictionary['url']).group(4)
            await self.get_content(content_id, url_dictionary.copy())

        else:
            log.info("Url does not match regex: {url_dictionary['url']}")

    async def call(self, endpoint: str, params: dict, url_dictionary: UrlDictionary) -> httpx.Response | None:

        log.debug("Calling api to get folder information")
        url = f"https://api.gofile.io/{endpoint}"

        async with httpx.AsyncClient() as client:

            response = await client.get(url, params=params, timeout=None)

        if response.status_code >= 300:
            url_dictionary['response'] = response
            await self.common_bad_status_code(url_dictionary.copy())
            return

        return response.json()

    async def get_content(self, contentId: str, url_dictionary: UrlDictionary, password: Optional[str] = None) -> None:

        already_downloaded_urls: list[str] = rat_info.get_downloaded_urls()

        if already_downloaded_urls:
            if url_dictionary['url'] in already_downloaded_urls:
                url_dictionary['completed'] = True
                log.info("Already found. Sending to tracker")
                await self.tracker.add_url_dictionary(url_dictionary.copy())
                await self.common_advance_search_count(url_dictionary.copy())
                return

        params = {"contentId": contentId,
                  "token": self.token,
                  "websiteToken": self.website_token}

        if password:
            log.debug("password found. Hashing")
            hash = hashlib.sha256()
            hash.update(password.encode('utf8'))
            hashed_password = hash.hexdigest()
            params['password'] = hashed_password

        log.debug("Calling api")
        data = await self.call("getContent", params, url_dictionary.copy())

        if data['status'] != 'ok':
            log.error(f"Error downloading content: {url_dictionary['url']}")
            return

        log.debug("Received folder information. Finding content...")
        data = data['data']
        # print(data)
        # return

        content = []
        try:
            for child in data['childs']:
                content.append(child)

        except KeyError:
            log.info(
                f"File deleted. Adding to completed urls to avoid reattempt: {url_dictionary['url']}")
            rat_info.add_entry(category_1='urls_downloaded',
                               entry=url_dictionary['url'])
            await self.common_failed_attempt(url_dictionary.copy())
            return

        for id in content:

            item = data['contents'][id]

            if item['type'] == 'file':
                url_dictionary['name'] = item['name'].split(".")[0]
                url_dictionary['url_to_download'] = item['link']
                url_dictionary['cookies'] = {'accountToken': str(self.token)}
                url_dictionary['file_size'] = item['size']
                url_dictionary['extension'] = item['mimetype']
                url_dictionary['filename'] = self.common_filename_creator(
                    url_dictionary.copy())

                log.info("Url dictionary built. Sending to tracker")
                await self.tracker.add_url_dictionary(url_dictionary.copy())
                await self.common_advance_search_count(url_dictionary.copy())

            elif item['type'] == 'folder':
                url = f"https://gofile.io/d/{id}"
                url_dictionary['url'] = url

                await self.run(url_dictionary.copy())

            else:
                log.warn("Entry is not a file or folder. Unrecognized type")
                await self.common_failed_attempt(url_dictionary.copy())

    def get_token(self) -> httpx.Response:

        url = "https://api.gofile.io/createAccount"

        response = httpx.get(url, timeout=None).json()
        # print(response['data']['token'])
        return response['data']['token']
