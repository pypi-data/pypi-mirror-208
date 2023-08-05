import json
import httpx
import logging
import os

import yt_dlp
from pathlib import Path

from ripandtear.utils import rat_info
from ripandtear.utils.custom_types import UrlDictionary
from ripandtear.utils.progress import file_progress, file_category_progress

log = logging.getLogger(__name__)


async def download_file(url_dictionary: UrlDictionary, asyncio_semphore) -> None:

    async with asyncio_semphore:
        log.debug("Inside downloader")

        if url_dictionary.get("file_size"):
            file_size = int(url_dictionary['file_size'])

        else:
            file_size = 0

        if url_dictionary.get('ytdlp_required'):
            ytdlp_download(url_dictionary)
            return

        # is_file_local returns a tuple that says if the file exists in the
        # first position and many bytes have been downloaded in the second
        # Ex: (True, 8473)

        log.debug("Checking if file exists locally")

        if url_dictionary.get('filename'):
            filename = url_dictionary['filename']

        else:
            filename = url_dictionary['url_to_download'].split('/')[-1]

        is_file_local = local_file_exists(filename, file_size)

        try:
            if is_file_local[0] == "True":

                if is_file_local[1] == "done":

                    file_category_progress.advance(
                        url_dictionary['progress']['completed_id'], 1)
                    return

                else:

                    mode = 'ab'
                    initial_position = is_file_local[1]
            else:

                mode = 'wb'
                initial_position = 0

        except TypeError:
            log.error("Filename too long. Skipping")

            rat_info.add_entry(category_1='urls_downloaded',
                               entry=str(url_dictionary['url']))

            file_category_progress.advance(
                url_dictionary['progress']['failed_id'], 1)

            return

        headers = {'Range': f'bytes={initial_position}-'}

        if url_dictionary.get('headers'):

            for key, value in url_dictionary['headers'].items():
                headers[key] = value

        if len(filename) > 60:
            name = filename[:57] + "..."

        else:
            name = filename

        file_progress_id = file_progress.add_task(
            f"{name}", completed=initial_position, total=file_size)

        try:
            cookies = None
            if url_dictionary.get('cookies'):
                cookies = url_dictionary['cookies']

            async with httpx.AsyncClient() as client:
                async with client.stream('GET',
                                         url_dictionary['url_to_download'],
                                         headers=headers,
                                         timeout=None,
                                         cookies=cookies,
                                         follow_redirects=True) as response:

                    if response.status_code >= 300:

                        url_dictionary['status_code'] = int(
                            response.status_code)

                        await errors(url_dictionary.copy(), file_progress_id)
                        return

                    temp = json.dumps(dict(response.headers))
                    data = json.loads(temp)

                    if file_size == 0:
                        try:
                            if isinstance(int(data.get('content-length')), int):
                                file_size = int(data.get('content-length'))
                                file_progress.update(
                                    file_progress_id, total=file_size)

                        except TypeError:
                            pass

                        except KeyError:
                            pass

                    file = open(filename, mode)
                    async for chunk in response.aiter_bytes(8192):
                        size = file.write(chunk)
                        file_progress.update(file_progress_id, advance=size)

                    file_progress.update(file_progress_id, visible=False)
                    file_category_progress.advance(
                        url_dictionary['progress']['downloaded_id'], 1)

        except FileNotFoundError:

            file_progress.update(file_progress_id, visible=False)
            file_category_progress.advance(
                url_dictionary['progress']['failed_id'], 1)
            return

        except Exception:
            log.exception(
                f"Unable to download: {url_dictionary['url_to_download']}")
            rat_info.add_error_dictionary(url_dictionary.copy())
            file_progress.update(file_progress_id, visible=False)
            file_category_progress.advance(
                url_dictionary['progress']['failed_id'], 1)
            return

        try:
            if url_dictionary.get('url_to_record'):

                rat_info.add_entry(category_1='urls_downloaded',
                                   entry=url_dictionary['url_to_record'])

            else:
                rat_info.add_entry(category_1='urls_downloaded',
                                   entry=url_dictionary['url_to_download'])

        except ValueError as identifier:
            log.info(identifier)


def local_file_exists(filename, online_file_size):

    try:
        if Path(filename).exists():

            temp = open(filename)
            temp.seek(0, os.SEEK_END)
            local_file_size = temp.tell()

            if online_file_size > 0:

                if local_file_size != online_file_size:
                    return ("True", local_file_size)

                else:
                    return ("True", "done")

            else:
                return ("False")
        else:
            return ("False")

    except OSError:
        return


async def errors(url_dictionary, file_progress_id):

    log.error("Finding bad status code")

    if url_dictionary['status_code'] == 403:

        log.error(f"Authorization Error - {url_dictionary['url']}")

        rat_info.add_error_dictionary(url_dictionary.copy())
        file_progress.update(file_progress_id, visible=False)
        file_category_progress.advance(
            url_dictionary['progress']['failed_id'], 1)

    elif url_dictionary['status_code'] == 404:

        log.error(
            f"Content was deleted or did not exist: {url_dictionary['status_code']} - {url_dictionary['url']}")

        rat_info.add_error_dictionary(url_dictionary.copy())
        file_progress.update(file_progress_id, visible=False)
        file_category_progress.advance(
            url_dictionary['progress']['failed_id'], 1)

    elif url_dictionary['status_code'] == 429:

        log.error(f"{url_dictionary['status_code']}: Too Many Requests")

        rat_info.add_error_dictionary(url_dictionary.copy())
        file_progress.update(file_progress_id, visible=False)
        file_category_progress.advance(
            url_dictionary['progress']['failed_id'], 1)

    elif 500 <= url_dictionary['status_code'] < 600:

        log.error(
            f"500 error. Saving the url to be attempted later: {url_dictionary['status_code']} - {url_dictionary['url_to_download']}")

        rat_info.add_error_dictionary(url_dictionary.copy())
        file_progress.update(file_progress_id, visible=False)
        file_category_progress.advance(
            url_dictionary['progress']['failed_id'], 1)

    else:
        log.error(
            f"Unable to download {url_dictionary['status_code']}: {url_dictionary['url']}")


def ytdlp_download(url_dictionary):

    try:
        log.info("Attempting yt_dlp download")

        ytdlp_options = {"outtmpl": url_dictionary['filename']}

        with yt_dlp.YoutubeDL(ytdlp_options) as ytdlp:
            ytdlp.download(url_dictionary['url_to_download'])

        rat_info.add_entry(category_1='urls_downloaded',
                           entry=url_dictionary['url_to_download'])

        file_category_progress.advance(
            url_dictionary['progress']['downloaded_id'], 1)
        return

    except yt_dlp.utils.DownloadError:
        log.info(
            f"Problem downloading url. Saving for later: {url_dictionary['url_to_download']}")
        rat_info.add_error_dictionary(url_dictionary)
        file_category_progress.advance(
            url_dictionary['progress']['failed_id'], 1)
        return
