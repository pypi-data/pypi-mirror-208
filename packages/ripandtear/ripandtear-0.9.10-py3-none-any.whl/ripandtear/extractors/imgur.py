import asyncio
import httpx
import logging
import re
import json

from ripandtear.extractors.common import Common
from ripandtear.utils.custom_types import UrlDictionary
from ripandtear.utils.tracker import Tracker

log = logging.getLogger(__name__)

# Errors
# 'https://i.imgur.com/LKvqXWE.gifv'

prefix = 'imgur'

imgur_re_direct_image = re.compile(
    r"(https?://)([im]\.|www\.)?(imgur\.(com|io))/(\w+)(\.jpg|jpeg|png|gifv|mp4|gif)?")
# 'https://i.imgur.com/I7i8u6b.gifv'
# 'https://i.imgur.com/hCOoORb.png'

imgur_re_album = re.compile(
    r"(https?://)?(([im]\.)|(www.))?(imgur\.(com|io))/((a))/(\w+)")
# 'https://imgur.com/a/1GXfC'
# 'https://imgur.com/a/1GXfC/all'

imgur_re_gallery = re.compile(
    r"(https?://)(imgur\.(com|io))/gallery/(\w+)")
# 'https://imgur.com/gallery/mPIxZnC'

headers = {
    "Authorization": "Client-ID 546c25a59c58ad7"
}


class Imgur(Common):

    def __init__(self):

        self.tracker = Tracker.getInstance()

    def imgur_direct_image_hash(self, url: str) -> str:
        log.debug("Looking for direct image hash")
        direct_image_hash = imgur_re_direct_image.search(url).group(5)
        return direct_image_hash

    def imgur_direct_album_hash(self, url: str) -> str:
        log.debug("Looking for album hash")
        direct_album_hash = imgur_re_album.search(url).group(9)
        return direct_album_hash

    def imgur_direct_gallery_hash(self, url: str) -> str:
        log.debug("Looking for gallery hash")
        direct_gallery_hash = imgur_re_gallery.search(url).group(4)
        return direct_gallery_hash

    async def run(self, url_dictionary: UrlDictionary) -> None:

        if imgur_re_gallery.match(url_dictionary['url']):

            log.debug("Gallery found. Sending to gallery download")
            await self.imgur_gallery_download(
                self.imgur_direct_gallery_hash(url_dictionary['url']), url_dictionary.copy())

        elif imgur_re_album.match(url_dictionary['url']):

            log.debug("Album found. Sending to album download")
            await self.imgur_album_download(
                self.imgur_direct_album_hash(url_dictionary['url']), url_dictionary.copy())

        elif imgur_re_direct_image.match(url_dictionary['url']):

            log.debug("Direct image found. Sending to single download")
            await self.imgur_single_download(self.imgur_direct_image_hash(
                url_dictionary['url']), url_dictionary.copy())

        else:
            log.info(f"No regex found for {url_dictionary['url']}")

    async def imgur_single_download(self, image_hash: str, url_dictionary: UrlDictionary) -> None:

        log.info(f"Single image found: {image_hash}")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.imgur.com/3/image/{image_hash}", headers=headers, timeout=None)

        try:

            data = response.json()

        except json.decoder.JSONDecodeError:

            log.warn(f"Image has been deleted: {image_hash}")

            await self.common_failed_attempt(url_dictionary)
            return

        # print(data)

        # if mp4 is a key in the data dictionary, then it means the image to download
        # ends with .mp4,.gif,.gifv. The mp4 link is grabbed along with its file size.
        # if mp4 does not exist, then the direct link to the file is grabbed along with
        # the file's size

        try:
            if 'mp4' in data['data']:

                url_to_download = data['data']['mp4']
                file_size = data['data']['mp4_size']
                url_dictionary['extension'] = 'mp4'

            else:

                url_to_download = data['data']['link']
                file_size = data['data']['size']
                url_dictionary['extension'] = data['data']['type']

        except KeyError:
            log.warn(f"Url missing keyword. Possibly deleted: {image_hash}")

            await self.common_failed_attempt(url_dictionary)
            return

        url_dictionary['prefix'] = prefix

        # Many times the titles from reddit are better description.
        # If description is true, that means the link was sent here
        # via the reddit ripper along with the better description.
        # use the better description by ignoring what imgur has set
        # other wise use what imgur gives, if availible

        if url_dictionary.get('description'):
            pass

        else:
            url_dictionary['description'] = data['data']['description']

        try:
            url_dictionary['name'] = data['data']['id']
            url_dictionary['date'] = data['data']['datetime']
            url_dictionary['url_to_download'] = url_to_download
            url_dictionary['file_size'] = file_size
            url_dictionary['filename'] = self.common_filename_creator(
                url_dictionary.copy())

            log.info("Url dictionary built. Sending to tracker")
            await self.tracker.add_url_dictionary(url_dictionary.copy())
            await self.common_advance_search_count(url_dictionary.copy())

        except KeyError:
            log.warn(f"Url missing keyword. Possibly deleted: {image_hash}")

            await self.common_failed_attempt(url_dictionary)
            return

    async def imgur_album_download(self, album_hash: str, url_dictionary: UrlDictionary) -> None:

        log.debug("Finding album hash")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.imgur.com/3/album/{album_hash}/images", headers=headers, timeout=None)

        try:
            data = response.json()

        except Exception:
            log.info(f"Album deleted: {album_hash}")

            await self.common_failed_attempt(url_dictionary)
            return

        # if the number of images in the album is greater then 1
        # it creates a count variable and passes it on so the pictures
        # will be numbered in the order they are in the album
        # otherwise no numbers are passed on.

        if len(data['data']) > 1:

            log.debug("Multiple images found. Sending them to single download")
            tasks = []
            count = 0
            for entry in data['data']:

                count += 1
                try:
                    image_hash = self.imgur_direct_image_hash(entry['link'])

                except TypeError:
                    continue

                url_dictionary['album_name'] = album_hash
                url_dictionary['count'] = count

                tasks.append(asyncio.create_task(
                    self.imgur_single_download(image_hash, url_dictionary.copy())))

            log.info("Tasks created. Gathering")
            await asyncio.gather(*tasks)

        else:

            for entry in data['data']:
                image_hash = self.imgur_direct_image_hash(entry['link'])
                await self.imgur_single_download(image_hash, url_dictionary.copy())

    async def imgur_gallery_download(self, gallery_hash: str, url_dictionary: UrlDictionary) -> None:

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.imgur.com/3/gallery/image/{gallery_hash}", headers=headers, timeout=None)

            data = response.json()

            image_hash = self.imgur_direct_image_hash(data['data']['link'])
            log.debug("Image found. Sending to single download")
            await self.imgur_single_download(image_hash, url_dictionary.copy())

        except Exception:

            try:
                log.debug(
                    "Problem loading imgur gallery. Attempting as imgur album instead")
                await self.imgur_album_download(gallery_hash, url_dictionary.copy())

            except Exception:
                log.exception("Problem Downloading a Gallery")

                await self.common_failed_attempt(url_dictionary)
                return
