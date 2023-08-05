import httpx
import logging
import re

from ripandtear.extractors.common import Common
from ripandtear.utils.custom_types import UrlDictionary
from ripandtear.utils.tracker import Tracker

log = logging.getLogger(__name__)

re_content_link = re.compile(r"(https?://)(gfycat\.(com)/)(\w+)")

gfycat_api_url = 'https://api.gfycat.com'

prefix = 'gfycat'


class Gfycat(Common):

    def __init__(self):
        self.tracker = Tracker.getInstance()

    async def run(self, url_dictionary):

        if re_content_link.match(url_dictionary['url']):
            content_id = re_content_link.match(url_dictionary['url']).group(4)
            await self.download_individual_gfy(content_id, url_dictionary.copy())

    async def call(self, endpoint: str, url_dictionary: UrlDictionary) -> dict | None:

        api_url = gfycat_api_url + endpoint

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, timeout=None)

        except Exception:
            log.error("Error calling api")
            await self.common_failed_attempt(url_dictionary)
            return

        if response.status_code >= 300:

            url_dictionary['status_code'] = int(response.status_code)
            await self.common_bad_status_code(url_dictionary.copy())
            return

        data = response.json()

        return data

    async def download_individual_gfy(self, content_id, url_dictionary):
        endpoint = f"/v1/gfycats/{content_id}"
        data = await self.call(endpoint, url_dictionary.copy())

        try:
            url_dictionary['url_to_download'] = data['gfyItem']['mp4Url']

        except TypeError:
            log.info(f"Video deleted: {url_dictionary['url']}")
            await self.common_failed_attempt(url_dictionary)
            return

        url_dictionary['prefix'] = prefix
        url_dictionary['name'] = content_id
        url_dictionary['date'] = data['gfyItem']['createDate']
        url_dictionary['file_size'] = data['gfyItem']['mp4Size']
        url_dictionary['extension'] = 'mp4'
        url_dictionary['filename'] = self.common_filename_creator(
            url_dictionary.copy())

        # await self.common_file_downloader(url_dictionary.copy())
        log.info("Url dictionary built. Sending to tracker")
        await self.tracker.add_url_dictionary(url_dictionary.copy())
        await self.common_advance_search_count(url_dictionary.copy())
