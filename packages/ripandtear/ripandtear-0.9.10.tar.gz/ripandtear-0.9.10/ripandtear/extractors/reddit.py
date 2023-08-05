import asyncio
import httpx
import json
import logging
import re

from ripandtear.extractors.common import Common
from ripandtear.utils.custom_types import UrlDictionary
from ripandtear.utils import conductor
from ripandtear.utils import rat_info
from ripandtear.utils.tracker import Tracker

log = logging.getLogger(__name__)

# 'https://i.redd.it/rnjp801xh0ia1.png'
# 'https://v.redd.it/v32qxuvfxxha1/'
# 'https://v.redd.it/xbmrqqxrqeda1/DASH_1080.mp4'
# 'https://v.redd.it/vvloy8w6i8ja1'
# 'https://v.reddit.com/vvloy8w6i8ja1'

re_reddit_media = re.compile(
    r"(https?://)([iv]\.)((reddit|redd)\.(com|it))/(\w+)(/?|\w+)?([\w\-_]+)?(\.\w+)?")


# 'https://www.reddit.com/r/ProgrammerHumor/comments/1115ze9/no_one_will_ever_know/'
# 'https://www.reddit.com/r/oddlyterrifying/comments/q2520f/419k_of_you_voted_and_we_listened_this_subreddit/'
re_reddit_post = re.compile(
    r"(https?://)([\w]+\.)(reddit\.com)/(r|user)/(\w+)/(\w+)/(\w+)/(.*)")

# 'https://www.reddit.com/gallery/pyuc2y'
re_reddit_gallery = re.compile(
    r"(https?://)([\w]+\.)?(reddit\.com|redd\.it)/(gallery)/(\w+)")

# 'https://preview.redd.it/ptwafbf4upq71.png?width=1080&crop=smart&auto=webp&v=enabled&s=c1bd0a78e48fcfe976956f14ad19074baea814f3'
re_reddit_gallery_link = re.compile(
    r"(https?://)(preview\.)(redd\.it)/(\w+)\.(\w+)\?(.*)")

# 'https://www.reddit.com/user/GallowBoob/'
re_reddit_user = re.compile(
    r"(https?://)(\w+\.)(reddit\.com)/(user|u)/([\w\-\_]+)(/.*)?")

sem = asyncio.Semaphore(4)


class Reddit(Common):

    def __init__(self):

        self.client_id = "qQ49J_mVAhnh6q4wAoJ8jQ"
        self.user_agent = "Python:ripandtear:0.1.4 (by /u/johnny_barracuda)"
        self.prefix = "reddit"
        self.headers = {}
        self.tracker = Tracker.getInstance()

    async def authorization(self) -> None:

        if self.headers.get("authorization"):
            log.debug("authorization token already found")
            return

        else:
            url = "https://www.reddit.com/api/v1/access_token"

            self.headers['user-agent'] = self.user_agent

            data = {"grant_type": "https://oauth.reddit.com/grants/installed_client",
                    "device_id": "DO_NOT_TRACK_THIS_DEVICE"}

            log.debug("Requesting authorization token")
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, data=data,
                                             auth=(self.client_id, ""), timeout=None)

            # print(response.headers)
            # print(response.content)

            try:
                data = response.json()

            except json.decoder.JSONDecodeError:
                log.error("Servers may be busy, try again later")
                return

            token = data["access_token"]
            # print(token)
            self.headers["authorization"] = f"bearer {token}"
            log.debug("authorization token set")

    async def call(self, endpoint: str, params: dict[str, int], url_dictionary: UrlDictionary) -> dict | None:

        url = f"https://oauth.reddit.com/{endpoint}"

        log.debug("getting authorization")
        await self.authorization()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=self.headers, timeout=None)

        except Exception as e:
            log.exception(f"{e}: {url}")
            await self.common_failed_attempt(url_dictionary.copy())
            return

        if response.status_code >= 300:
            url_dictionary['status_code'] = int(response.status_code)
            await self.common_bad_status_code(url_dictionary.copy())
            return

        remaining = response.headers.get("x-ratelimit-remaining")

        if remaining and float(remaining) < 2:
            wait_time = int(response.headers["x-ratelimit-reset"])
            current_time = await self.common_get_time()
            url_dictionary['progress']['search_message'].add_task(
                f'{current_time} Reddit - Sleeping to reset rateliming: {wait_time} seconds')
            await asyncio.sleep(wait_time)

        data = response.json()

        if "error" in data:

            if data["error"] == 403:
                log.error("Authorization Error")
                url_dictionary['status_code'] = 403
                await self.common_bad_status_code(url_dictionary.copy())
                return

            if data["error"] == 404:
                log.warn("404 Not Found")
                url_dictionary['status_code'] = 404
                await self.common_bad_status_code(url_dictionary.copy())
                return

        log.debug("Returning data from call")
        return data

    async def run(self, url_dictionary: UrlDictionary) -> None:

        if re_reddit_media.match(url_dictionary['url']):

            log.debug(
                f"Direct reddit media match: {url_dictionary['url']}")
            await self.reddit_media(url_dictionary.copy())

        elif re_reddit_gallery.match(url_dictionary['url']):

            url_dictionary['reddit_uniq_id'] = re_reddit_gallery.match(
                url_dictionary['url']).group(5)

            log.debug(f"reddit gallery match: {url_dictionary['url']}")
            await self.reddit_post(url_dictionary.copy())

        elif re_reddit_post.match(url_dictionary['url']):

            url_dictionary['reddit_uniq_id'] = re_reddit_post.match(
                url_dictionary['url']).group(7)
            log.debug(f"reddit post match: {url_dictionary['url']}")
            await self.reddit_post(url_dictionary.copy())

        elif re_reddit_user.match(url_dictionary['url']):

            url_dictionary['reddit_username'] = re_reddit_user.match(
                url_dictionary['url']).group(5)
            log.debug(f"reddit user match: {url_dictionary['url']}")
            await self.reddit_user(url_dictionary.copy())

        else:
            log.info(
                f"No matching regex found for {url_dictionary['url']}")
            await self.common_failed_attempt(url_dictionary.copy())

    async def reddit_media(self, url_dictionary: UrlDictionary) -> None:

        log.debug("Inside reddit media download")
        if re_reddit_media.match(url_dictionary['url']).group(2) == 'i.':
            log.debug("reddit image found")

            user_agent = {'user-agent': self.user_agent}

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.head(
                        url_dictionary['url'], headers=user_agent, timeout=None)

                if response.status_code >= 300:
                    await self.common_bad_status_code(url_dictionary.copy())
                    return

                temp = json.dumps(dict(response.headers))
                data = json.loads(temp)
                # print(data)

                url_dictionary['prefix'] = self.prefix

                url_dictionary['date'] = await self.common_get_epoch_time(
                    str(response.headers.get('last-modified')))

                url_dictionary['name'] = re_reddit_media.match(
                    url_dictionary['url']).group(6)

                url_dictionary['url_to_download'] = str(response.url)

                if data.get('Content-Length'):
                    url_dictionary['file_size'] = int(
                        data['Content-Length'])

                url_dictionary['extension'] = data['content-type']
                url_dictionary['filename'] = self.common_filename_creator(
                    url_dictionary)

                # await self.common_file_downloader(url_dictionary.copy())
                log.info("Url dictionary built. Sending to tracker")
                await self.tracker.add_url_dictionary(url_dictionary.copy())
                await self.common_advance_search_count(url_dictionary.copy())

            except Exception:
                log.exception(
                    f"Problem downloading file. Saving for later: {url_dictionary['url_to_download']}")
                await self.common_failed_attempt(url_dictionary.copy())

        if re_reddit_media.match(url_dictionary['url']).group(2) == 'v.':

            log.debug("Reddit video found")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url_dictionary['url'], headers=self.headers, follow_redirects=True, timeout=None)

            # print(response.url)
            url_dictionary['url'] = str(response.url)

            try:
                url_dictionary['reddit_uniq_id'] = re_reddit_post.match(
                    url_dictionary['url']).group(7)

            except AttributeError:
                # print(url_dictionary['url'])
                url_dictionary['ytdlp_required'] = True
                url_dictionary['url_to_download'] = url_dictionary['url']

                url_dictionary['name'] = re_reddit_media.match(
                    url_dictionary['url']).group(6)

                url_dictionary['extension'] = 'mp4'

                url_dictionary['filename'] = self.common_filename_creator(
                    url_dictionary.copy())

                # print(url_dictionary)
                # await self.common_file_downloader(url_dictionary.copy())
                log.info("Url dictionary built. Sending to tracker")
                await self.tracker.add_url_dictionary(url_dictionary.copy())
                await self.common_advance_search_count(url_dictionary.copy())
                return

            await self.reddit_post(url_dictionary.copy())

    async def reddit_post(self, url_dictionary: UrlDictionary) -> None:

        endpoint = f"comments/{url_dictionary['reddit_uniq_id']}/.json"
        params = {}
        params["raw_json"] = "1"

        async with sem:
            log.debug("Calling reddit api for a post")
            data = await self.call(endpoint, params, url_dictionary.copy())

            try:

                post = data[0]['data']['children'][0]['data']

                url_dictionary['url_to_download'] = str(post['url'])

                log.info(
                    f"Reddit post found: {url_dictionary['url_to_download']}")

            except TypeError:
                log.warn(
                    f"Servers are down or most likely user profile has been deleted. Reddit username: {url_dictionary['reddit_username']}")
                await self.common_failed_attempt(url_dictionary.copy())

            try:
                if conductor.imgur_re.search(url_dictionary['url_to_download']):

                    url_dictionary['url'] = url_dictionary['url_to_download']
                    url_dictionary['url_to_record'] = url_dictionary['url_to_download']
                    url_dictionary['description'] = str(post['title'])
                    log.debug("imgur link found, sending to conductor")
                    await conductor.imgur(url_dictionary.copy())

                elif conductor.redgifs_re.search(url_dictionary['url_to_download']):

                    url_dictionary['url'] = url_dictionary['url_to_download']
                    url_dictionary['description'] = str(post['title'])
                    log.debug("redgifs link found, sending to conductor")
                    await conductor.redgifs(url_dictionary.copy())

                elif conductor.gfycat_re.search(url_dictionary['url_to_download']):

                    url_dictionary['url'] = url_dictionary['url_to_download']
                    url_dictionary['description'] = str(post['title'])
                    log.debug("gfycat link found, sending to conductor")
                    await conductor.gfycat(url_dictionary.copy())

                elif post.get('is_gallery'):

                    if post.get('gallery_data'):
                        await self.reddit_gallery_download(post, url_dictionary)

                    else:
                        log.info(
                            f"Post Deleted: {url_dictionary['reddit_uniq_id']}")
                        await self.common_failed_attempt(url_dictionary.copy())
                        return

                elif re_reddit_media.match(post['url']).group(2) == "i.":

                    url_dictionary['url'] = str(post['url'])
                    url_dictionary['description'] = str(post['title'])
                    url_dictionary['album_name'] = url_dictionary['reddit_uniq_id']

                    await self.reddit_media(url_dictionary.copy())

                elif re_reddit_media.match(post['url']).group(2) == "v.":
                    await self.reddit_video_download(post, url_dictionary.copy())

                else:
                    log.warn(
                        f"No regex match found for: {url_dictionary['url_to_download']}. \
                        Seeing if url matches a pattern in conductor")
                    await conductor.validate_url(url_dictionary.copy())
                    return

            except AttributeError:

                log.error(
                    f"Not a downloadable link: {url_dictionary['url_to_download']}")
                await self.common_failed_attempt(url_dictionary.copy())

            except KeyError:
                log.error("Problem downloading. Reddit servers might be down")
                await self.common_failed_attempt(url_dictionary.copy())
                return

    async def reddit_user(self, url_dictionary: UrlDictionary) -> None:

        log.info(f"Reddit user found: {url_dictionary['reddit_username']}")
        endpoint = f"user/{url_dictionary['reddit_username']}/submitted/.json"
        params = {}

        tasks = []
        already_downloaded_urls = rat_info.get_downloaded_urls()
        end = False
        while end is False:

            log.debug("Calling Reddit api to get user info")

            params["limit"] = 100
            data = await self.call(endpoint, params, url_dictionary.copy())
            log.debug("Received Reddit user data")
            # log.debug(data['data']['children'])

            try:
                for post in data['data']['children']:

                    # if attempting to download the files, skip what has already been downloaded
                    # otherwise if downloading isn't being attempted continue to find the actual urls so they
                    # can be printed (-g flag)

                    if post['data']['url'] in already_downloaded_urls and url_dictionary['download'] is True:
                        continue

                    elif post['data']['url'] not in already_downloaded_urls and url_dictionary['download'] is True:
                        url_dictionary['reddit_uniq_id'] = post['data']['id']
                        tasks.append(asyncio.create_task(
                            self.reddit_post(url_dictionary.copy())))

                    elif url_dictionary['download'] is False:
                        url_dictionary['url_to_download'] = post['data']['url']

                        log.info("Url dictionary built. Sending to tracker")
                        await self.tracker.add_url_dictionary(url_dictionary.copy())
                        continue

                if data['data']['after']:
                    params['after'] = data['data']['after']

                else:
                    end = True

            except TypeError:
                log.warn(
                    f"Servers could be down, but most likely user profile has been deleted. Reddit username: {url_dictionary['reddit_username']}")
                end = True

        await asyncio.gather(*tasks)

    async def reddit_gallery_download(self, post, url_dictionary):

        log.debug("gallery found")
        image_order = []
        for entry in post['gallery_data']['items']:
            id = entry['media_id']
            image_order.append(id)

        count = 0
        try:
            for id in image_order:

                count += 1

                image_link = post['media_metadata'][id]['p'][0]['u']

                url_dictionary['name'] = re_reddit_gallery_link.match(
                    image_link).group(4)

                url_dictionary['extension'] = re_reddit_gallery_link.match(
                    image_link).group(5)

                image_url = f"https://i.redd.it/{url_dictionary['name']}.{url_dictionary['extension']}"

                async with httpx.AsyncClient() as client:
                    response = await client.head(
                        image_url, headers=self.headers, timeout=None)

                temp = json.dumps(dict(response.headers))
                data = json.loads(temp)

                url_dictionary['prefix'] = self.prefix
                url_dictionary['date'] = post['created_utc']

                url_dictionary['album_name'] = url_dictionary['reddit_uniq_id']
                url_dictionary['count'] = count
                url_dictionary['description'] = str(post['title'])

                if data.get('content-length'):
                    url_dictionary['file_size'] = int(data['content-length'])

                url_dictionary['url_to_download'] = image_url
                url_dictionary['filename'] = self.common_filename_creator(
                    url_dictionary.copy())

                log.info("Url dictionary built. Sending to tracker")
                await self.tracker.add_url_dictionary(url_dictionary.copy())
                await self.common_advance_search_count(url_dictionary.copy())

        except IndexError:
            pass

    async def reddit_video_download(self, post, url_dictionary):

        log.info(f"Reddit video found: {post['url']}")

        url_dictionary['ytdlp_required'] = True
        url_dictionary['prefix'] = self.prefix
        url_dictionary['date'] = post['created_utc']
        url_dictionary['name'] = url_dictionary['reddit_uniq_id']
        url_dictionary['description'] = post['title']
        url_dictionary['url_to_download'] = str(post['url'])
        url_dictionary['extension'] = "mp4"
        url_dictionary['filename'] = self.common_filename_creator(
            url_dictionary.copy())

        # await self.common_file_downloader(url_dictionary.copy())
        log.info("Url dictionary built. Sending to tracker")
        await self.tracker.add_url_dictionary(url_dictionary.copy())
        await self.common_advance_search_count(url_dictionary.copy())
