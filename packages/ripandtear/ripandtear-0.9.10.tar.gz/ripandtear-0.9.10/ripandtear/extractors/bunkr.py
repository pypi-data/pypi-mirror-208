from pathlib import Path
import asyncio
import httpx
import logging
import random
import re

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from ripandtear.extractors.common import Common
from ripandtear.utils.custom_types import UrlDictionary
from ripandtear.utils.tracker import Tracker

log = logging.getLogger(__name__)

# 'https://cdn.bunkr.ru/2316x3088_6f524042147f7b97c8c6e44ccab72374-jvBZFnON.jpg'
# 'https://i.bunkr.ru/2316x3088_6f524042147f7b97c8c6e44ccab72374-jvBZFnON.jpg'
re_bunkr_image_prefix = re.compile(
    r"(([i\w]+)|(i)|((cdn\w+)|(cdn)))")

# 'https://media-files10.bunkr.ru/2022-06-22-Natalie-Roush---Leggings-Haul-vJBce0DY.mp4'
re_bunkr_media_files = re.compile(
    r"((media-files[\w]+)|(media-files))")

# 'https://bunkr.su/v/0h1vsyrrw8558lb5agtx4_source-gigzea10.mp4'
re_bunkr_video_href = re.compile(
    r"(/|/[v|d]/)([\w\-_\(\)\.]+)\.(\w+)")

re_bunkr_file_extensions = re.compile(
    r"(zip|rar|7z|txt)")

re_bunkr_video_extensions = re.compile(
    r"(mkv|mp4|webm|mov)")


# 'https://bunkr.su/a/ouikRoFy'
# 'https://stream.bunkr.ru/v/2022-04-23_Fake-Tan-01-Av9w6Za4.mp4'
re_bunkr_album = re.compile(
    r"(https?://)(bunkr.ru|bunkr.su|bunkr.is|bunkr.la)/a/(\w+)")

# 'https://i.bunkr.ru/2316x3088_6f524042147f7b97c8c6e44ccab72374-jvBZFnON.jpg'
# re_bunkr_single = re.compile(
#     r"(https?://)([\w\-]+\.)?(bunkr\.(ru|la|su|is))(/|/[v|d]/)([\w\-_\(\)\.\%\’]+)\.(\w+)")
re_bunkr_single = re.compile(
    r"(https?://)([\w\-]+\.)?(bunkr\.(ru|la|su|is))(/|/[v|d]/)(.*)\.(\w+)")

sem = asyncio.Semaphore(4)
sem_picture = asyncio.Semaphore(6)


class Bunkr(Common):

    def __init__(self):
        self.tracker = Tracker.getInstance()

    async def run(self, url_dictionary: UrlDictionary) -> None:

        if re_bunkr_album.match(url_dictionary['url']):

            try:
                log.debug("Found album. Collecting dictionaries")
                await self.album(url_dictionary)

            except TypeError:
                log.exception("TypeError")

                await self.common_failed_attempt(url_dictionary)
                return

        elif re_bunkr_single.match(url_dictionary['url']):

            log.debug(f"Found single media. {url_dictionary}")
            await self.single(url_dictionary)
            return

        else:
            log.info(
                f"Url doesn't match regex patterns {url_dictionary['url']}")

    async def single(self, url_dictionary: UrlDictionary) -> None:

        try:

            if re_bunkr_media_files.search(url_dictionary['url']):

                log.debug(
                    f"Direct media-files found. {url_dictionary['url']}")
                await self.url_dictionary_builder(url_dictionary.copy())
                return

            elif re_bunkr_file_extensions.match(re_bunkr_single.match(url_dictionary['url']).group(7)):

                log.debug("Direct file found")
                await self.bunkr_file(url_dictionary.copy())
                return

            elif re_bunkr_single.match(url_dictionary['url']).group(2) == 'stream.':

                log.debug("Direct stream found")
                async with sem:

                    url = await self.bunkr_stream(url_dictionary)

                    if url is None:
                        return

                    url_dictionary['url'] = str(url)
                    await self.url_dictionary_builder(url_dictionary.copy())
                    return

            elif re_bunkr_video_extensions.match(re_bunkr_single.match(url_dictionary['url']).group(7).lower()):

                log.debug("Video page found. Finding url")
                async with sem:
                    await asyncio.sleep(random.randint(1, 4))

                    url = await self.bunkr_stream(url_dictionary)

                    if url is None:
                        return

                    url_dictionary['url'] = str(url)
                    await self.url_dictionary_builder(url_dictionary.copy())
                    return

            elif re_bunkr_image_prefix.match(re_bunkr_single.match(url_dictionary['url']).group(2)):

                if re_bunkr_video_extensions.match(re_bunkr_single.match(url_dictionary['url']).group(7)):

                    log.debug("Direct video found")
                    async with sem:

                        url = await self.bunkr_stream(url_dictionary)

                        if url is None:
                            return

                        url_dictionary['url'] = str(url)
                        await self.url_dictionary_builder(url_dictionary.copy())
                        return

                else:
                    async with sem_picture:
                        log.debug("Direct image found")
                        await self.url_dictionary_builder(url_dictionary.copy())
                        return

            else:
                log.info(
                    f"Given url doesn't match regex pattern {url_dictionary['url']}")
                return

        except AttributeError:
            log.exception(f"Unable to match {url_dictionary['url']}")
            await self.common_failed_attempt(url_dictionary)
            return

        except TypeError:
            log.exception(f"TypeError found for {url_dictionary['url']}")
            await self.common_failed_attempt(url_dictionary)
            return

    async def url_dictionary_builder(self, url_dictionary: UrlDictionary) -> None:

        try:

            log.debug("Sending request")
            async with httpx.AsyncClient() as client:
                response = await client.head(f"{url_dictionary['url']}", timeout=None, follow_redirects=True)

        except httpx.ReadError:
            log.error(
                f"Unable to confirm - {url_dictionary['url']}. Possible 404")

            await self.common_failed_attempt(url_dictionary)
            return

        # if a video is on a server that is under maintenance, the video is
        # redirected to this link. If this link is found then save the url_dictionary
        # to be downloaded later.

        if response.url == 'https://bnkr.b-cdn.net/maintenance.mp4':
            log.info(
                f"Server where content is hosted is under maintenance: {url_dictionary['url']}")

            await self.common_failed_attempt(url_dictionary)
            return

        url_dictionary['name'] = re_bunkr_single.match(
            url_dictionary['url']).group(6)

        url_dictionary['url_to_download'] = str(response.url)

        try:
            url_dictionary['file_size'] = response.headers['Content-Length']

        except KeyError:
            log.info(
                f"No 'Content-Length' found for {response.url}. Link is probably dead")
            return

        url_dictionary['extension'] = response.headers['Content-Type']
        url_dictionary['filename'] = self.common_filename_creator(
            url_dictionary.copy())

        log.debug("Url dictionary built. Sending to tracker")
        # print(url_dictionary)
        # return
        await self.tracker.add_url_dictionary(url_dictionary.copy())
        await self.common_advance_search_count(url_dictionary.copy())
        return

    async def album(self, url_dictionary: UrlDictionary) -> None:

        url = f"{url_dictionary['url']}"

        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(slow_mo=50)
                page = await browser.new_page()
                log.info(f"Navigating to url: {url_dictionary['url']}")
                await page.goto(url, wait_until='networkidle')

                log.info("Searching for content")

                if await page.query_selector("div.grid") is None:

                    if await page.query_selector("div.grid-images"):

                        small_layout = True
                        content = page.locator("div.grid-images > div")

                    else:
                        log.info(
                            f"Page Layout not recognized: {url_dictionary['url']}")
                        return

                else:
                    small_layout = False
                    content = page.locator("div.grid > div")

                for i in range(await content.count()):
                    if i % 50 == 0:
                        log.info(f"Number of content found: {i}")
                    await content.nth(i).hover()

                if small_layout is True:
                    html = await page.locator('div.grid-images').inner_html()

                else:
                    html = await page.locator('div.grid').inner_html()

                await page.close()
                await browser.close()

                soup = BeautifulSoup(html, features='html.parser')

                if len(soup.find_all('a')) > 0:
                    log.info(
                        f"Found {len(soup.find_all('a'))} pieces of content. Preparing for download...")

                    tasks = []
                    for links in soup.find_all('a'):
                        link = str(links.get('href'))
                        if re_bunkr_image_prefix.match(link):
                            url_dictionary['url'] = link
                            tasks.append(asyncio.create_task(
                                self.run(url_dictionary.copy())))
                            continue

                        elif re_bunkr_video_href.match(link):
                            url_dictionary['url'] = f"https://bunkr.su{link}"
                            tasks.append(asyncio.create_task(
                                self.run(url_dictionary.copy())))
                            continue
                        else:
                            log.info(f"Unable to match {link}")

                    await asyncio.gather(*tasks)
                    return

                else:
                    log.info("No content found")
                    return

        except Exception:
            log.exception(f"Problem Loading {url_dictionary['url']}")
            await self.common_failed_attempt(url_dictionary)
            return

    async def bunkr_stream(self, url_dictionary: UrlDictionary) -> None:

        async with async_playwright() as pw:
            try:

                browser = await pw.chromium.launch()
                context = await browser.new_context(accept_downloads=True)
                # await context.tracing.start(screenshots=True, snapshots=True, sources=True)

                page = await context.new_page()
                response = await page.goto(url_dictionary['url'], wait_until="networkidle")

                if response.status >= 300:
                    log.debug("Bad Status Code")
                    url_dictionary['status_code'] = int(response.status)
                    await self.common_bad_status_code(url_dictionary.copy())
                    await page.close()
                    await context.close()
                    await browser.close()
                    return

                log.info(f"Searching for video: {url_dictionary['url']}")

                await asyncio.sleep(random.randint(3, 8))

                await page.is_visible('source')

                html = await page.locator('video').inner_html()

                soup = BeautifulSoup(html, features='html.parser')

                url = soup.find('source')['src']
                log.debug(f"Found url: {url}")
                return url

            except Exception:
                log.exception("Problem finding url from video page")

                await self.common_failed_attempt(url_dictionary)

            finally:
                # await context.tracing.stop(path=f"{random.randint(1, 20)}.zip")
                await page.close()
                await context.close()
                await browser.close()

    async def bunkr_file(self, url_dictionary: UrlDictionary) -> None:

        async with async_playwright() as pw:
            try:
                browser = await pw.chromium.launch()
                context = await browser.new_context(accept_downloads=True)

                page = await context.new_page()
                await page.goto(url_dictionary['url'])

                log.info("Searching for files")
                await page.wait_for_timeout(3000)

                async with page.expect_download() as download_info:
                    await page.locator(
                        "xpath=/html/body/main/section[3]/div/div/div/div/div[2]/a").click()

                download = await download_info.value
                filename = download.suggested_filename
                destination_path = Path().cwd() / filename

                log.info(f"Downloading: {filename}")
                current_time = await self.common_get_time()
                url_dictionary['progress']['search_message'].add_task(
                    f"{current_time} Bunkr - Downloading {filename}")

                await download.save_as(destination_path)

                log.info(f"Downloaded: {filename}")
                current_time = await self.common_get_time()
                url_dictionary['progress']['search_message'].add_task(
                    f"{current_time} Bunkr - Downloaded {filename}")

            except Exception:
                log.exception("Error downloading file: {file_url}")

                await self.common_failed_attempt(url_dictionary)

            finally:

                await context.close()
                await page.close()
                await browser.close()
