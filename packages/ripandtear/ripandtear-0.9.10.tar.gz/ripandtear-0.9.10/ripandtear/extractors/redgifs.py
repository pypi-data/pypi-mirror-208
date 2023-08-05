import asyncio
import httpx
import logging
import re

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from ripandtear.extractors.common import Common
from ripandtear.utils.custom_types import UrlDictionary
from ripandtear.utils import rat_info
from ripandtear.utils.tracker import Tracker

log = logging.getLogger(__name__)


prefix = "redgifs"
url_root = "https://www.redgifs.com/"
url_root_v3 = "https://v3.redgifs.com/"

# https://api.redgifs.com/v2/gifs/firstscientificloon
single_uid_api = "https://api.redgifs.com/v2/gifs/"

re_tag_url = re.compile(r"(https?://)(\w+\.)(redgifs\.com/)gifs\/(.*)")

re_extension = re.compile(
    r"(https?://)(\w+\.)(redgifs.com/)(\w+)(-\w+)?\.(\w+)")

re_watch_uid = re.compile(
    r"(/watch/)(\w+)#")

# 'https://i.redgifs.com/i/kosherpurehairstreak.jpg'
# https://v3.redgifs.com/watch/heavyimperfectkookaburra#rel=user%3Alamsinka89
# https://www.redgifs.com/watch/firstscientificloon (album with multiple images)
re_single_uid = re.compile(
    r"(https?://)(\w+\.)?(redgifs.com/)(watch|i)/(\w+)")

re_url_to_record = re.compile(
    r"((https?://)(\w+\.)?(redgifs.com/)(watch|i)/(\w+))")

# https://v3.redgifs.com/users/lamsinka89
re_user = re.compile(
    r"((https?://)(\w+\.)?(redgifs\.com)/(users)/([\w\-]+))")

sem = asyncio.Semaphore(6)


class Redgifs(Common):

    def __init__(self):
        self.tracker = Tracker.getInstance()

    async def get_token(self) -> None:

        log.debug("Requesting auth token")
        headers = {'token': ''}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.redgifs.com/v2/auth/temporary", headers=headers, timeout=None)

        data = response.json()

        self.headers = {'authorization': f"Bearer {data['token']}"}
        # print(self.headers)

        log.debug("Auth token set")

    async def run(self, url_dictionary: UrlDictionary) -> None:

        await self.get_token()

        if re_single_uid.match(url_dictionary['url']):

            log.debug("Single image found. Sending to single single_download")
            await self.single_download(re_single_uid.match(
                url_dictionary['url']).group(5), url_dictionary.copy())

        elif re_user.match(url_dictionary['url']):

            log.debug("User found. Sending to user_download_v3")
            await self.user_download_v3(re_user.match(
                url_dictionary['url']).group(6), url_dictionary.copy())

        elif re_tag_url.match(url_dictionary['url']):

            log.debug("Tags url found. Preparing download")
            await self.tag_download(url_dictionary.copy())

    async def tag_download(self, url_dictionary: UrlDictionary) -> None:

        log.info("Found Tag. Preparing download")

        async with async_playwright() as pw:

            try:
                browser = await pw.chromium.launch()
                page = await browser.new_page()
                await page.goto(url_dictionary['url'])

                log.info("Searching for videos")
                content = await page.query_selector_all('a.tile')

                while True:

                    for x in range(5):
                        await page.keyboard.down('PageDown')
                        await page.wait_for_timeout(200)

                    new_content = await page.query_selector_all('a.tile')

                    if len(new_content) > len(content):

                        content = new_content
                        log.info(f"Gifs found: {len(new_content)}")

                    else:
                        content = new_content
                        break

                if page.locator('div.gifList'):
                    html = await page.locator('div.gifList').inner_html()

                elif page.locator('div.tileFeed'):
                    html = await page.locator('div.tileFeed').inner_html()

                soup = BeautifulSoup(html, features='html.parser')

                already_downloaded_urls = rat_info.get_downloaded_urls()

                tasks = []
                for link in soup.find_all('a'):

                    href = link.get('href').split('#')[0]

                    url = f"https://v3.redgifs.com{href}"

                    if url in already_downloaded_urls and url_dictionary['download'] is True:
                        log.info(f"Already downloaded: {url}")
                        continue

                    elif url not in already_downloaded_urls and url_dictionary['download'] is True:
                        log.info(f"Creating task out of {url}")

                        url_dictionary['url'] = url
                        tasks.append(asyncio.create_task(
                            self.run(url_dictionary.copy())))

                    elif url_dictionary['download'] is False:
                        url_dictionary['url_to_download'] = url
                        continue

                log.info("Executing tasks")
                await asyncio.gather(*tasks)

            except Exception:
                log.exception("Problem getting gifs from tag url")
                await self.common_failed_attempt(url_dictionary.copy())

            finally:
                await page.close()
                await browser.close()

    async def single_download(self, uid: str, url_dictionary: UrlDictionary, download_gallery=True) -> None:
        # some urls can contain albums that need to use playwright to get all image uid's because albums
        # are not supported by the API. If the API returns the first image and in the data it says that
        # the image is part of a gallery, playwright opens the webpage to find all the individual images
        # within the album. It then recursivly sends it back to teh single_download to download all images
        # because each of those images say that they are apart of a gallery it can cause a forever loop.
        # the download_gallery variable is used to preven a forever loop. When album links are found
        # with playwright the variable is set to False to skip the playwright download a second time and
        # download the individual image

        async with sem:

            log.debug("Single image given. Attempting download")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{single_uid_api}{uid}", headers=self.headers, timeout=None)

            data = response.json()
            # print(data)

            if 'error' in data:

                log.info(f"File Deleted: {url_dictionary['url']}")
                return

            elif data['gif']['gallery'] is not None and download_gallery is True:
                async with async_playwright() as pw:

                    try:
                        browser = await pw.chromium.launch()
                        page = await browser.new_page()
                        await page.goto(f"https://www.redgifs.com/watch/{uid}")

                        log.info("Searching for album")
                        content = await page.locator("div.GallerySlider").inner_html()
                        # print(content)

                        log.info("Album found. Finding individual images")
                        soup = BeautifulSoup(content, features='html.parser')
                        # print(soup)

                        already_downloaded_urls = rat_info.get_downloaded_urls()

                        tasks = []
                        for link in soup.find_all('img'):

                            href = link.get('src')

                            uid = re_extension.match(href).group(4).lower()
                            url = f"https://v3.redgifs.com/watch/{uid}"

                            if url in already_downloaded_urls and url_dictionary['download'] is True:
                                log.info(f"Already downloaded: {url}")
                                continue

                            elif url not in already_downloaded_urls and url_dictionary['download'] is True:
                                log.info(f"Creating task out of {uid}")

                                url_dictionary['url'] = url
                                tasks.append(asyncio.create_task(
                                    self.single_download(uid, url_dictionary.copy(), download_gallery=False)))

                            elif url_dictionary['download'] is False:
                                url_dictionary['url_to_download'] = url
                                continue

                        log.info("All images in album found. Executing tasks")
                        await asyncio.gather(*tasks)

                    except Exception:
                        log.exception("Problem getting gifs from album")
                        await self.common_failed_attempt(url_dictionary.copy())

                    finally:
                        await page.close()
                        await browser.close()

            else:

                url_dictionary['prefix'] = prefix
                url_dictionary['name'] = data['gif']['id']
                url_dictionary['date'] = data['gif']['createDate']
                url_dictionary['url_to_download'] = data['gif']['urls']['hd']
                url_dictionary['url_to_record'] = re_url_to_record.match(
                    url_dictionary['url']).group(1)

                url_dictionary['extension'] = re_extension.match(
                    url_dictionary['url_to_download']).group(6)

                url_dictionary['filename'] = self.common_filename_creator(
                    url_dictionary)

                log.info("Sending dictionary to tracker")
                await self.tracker.add_url_dictionary(url_dictionary.copy())
                await self.common_advance_search_count(url_dictionary.copy())

    async def user_download_v3(self, username: str, url_dictionary: UrlDictionary) -> None:

        log.info(f"Redgifs user Found: {username}")

        user_url = f"https://v3.redgifs.com/users/{username}"

        async with async_playwright() as pw:

            try:
                browser = await pw.chromium.launch()
                page = await browser.new_page()
                await page.goto(user_url)

                log.info("Searching for videos")
                content = await page.query_selector_all('a.tile')

                while True:

                    for x in range(5):
                        await page.keyboard.down('PageDown')
                        await page.wait_for_timeout(200)

                    new_content = await page.query_selector_all('a.tile')

                    if len(new_content) > len(content):

                        content = new_content
                        log.info(f"Gifs found: {len(new_content)}")

                    else:
                        content = new_content
                        break

                if page.locator('div.gifList'):
                    html = await page.locator('div.gifList').inner_html()

                elif page.locator('div.tileFeed'):
                    html = await page.locator('div.tileFeed').inner_html()

                soup = BeautifulSoup(html, features='html.parser')

                already_downloaded_urls = rat_info.get_downloaded_urls()

                tasks = []
                for link in soup.find_all('a'):

                    href = link.get('href')

                    uid = re_watch_uid.match(href).group(2)
                    url = f"https://v3.redgifs.com/watch/{uid}"

                    if url in already_downloaded_urls and url_dictionary['download'] is True:
                        log.info(f"Already downloaded: {url}")
                        continue

                    elif url not in already_downloaded_urls and url_dictionary['download'] is True:
                        log.info(f"Creating task out of {uid}")

                        url_dictionary['url'] = url
                        tasks.append(asyncio.create_task(
                            self.single_download(uid, url_dictionary.copy())))

                    elif url_dictionary['download'] is False:
                        url_dictionary['url_to_download'] = url
                        continue

                log.info("Executing tasks")
                await asyncio.gather(*tasks)

            except Exception:
                log.exception("Problem getting gifs from user profile")
                await self.common_failed_attempt(url_dictionary.copy())

            finally:
                await page.close()
                await browser.close()
