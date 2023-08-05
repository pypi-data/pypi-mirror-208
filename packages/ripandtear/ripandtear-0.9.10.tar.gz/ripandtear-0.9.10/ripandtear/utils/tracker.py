import asyncio
import logging


from ripandtear.utils.progress import file_category_progress
from ripandtear.utils import rat_info

from ripandtear.utils import downloader

log = logging.getLogger(__name__)


class Tracker:

    __instance = None

    @staticmethod
    def getInstance():
        if Tracker.__instance is None:
            Tracker()
        return Tracker.__instance

    def __init__(self):
        Tracker.__instance = self
        self.url_dictionaries = []
        self.fast_dictionaries = []
        self.medium_dictionaries = []
        self.slow_dictionaries = []

    async def add_url_dictionary(self, url_dictionary):
        log.debug("Adding url_dictionary")
        self.url_dictionaries.append(url_dictionary)

    def total_url_dictionaries(self):
        return len(self.url_dictionaries)

    async def print_urls(self):
        for url_dictionary in self.url_dictionaries:
            if url_dictionary.get('fail') is None:
                print(url_dictionary['url_to_download'])

    def clean_duplicates(self):
        log.info("Cleaning Duplicate Dictionaries")
        log.info(f"Before cleaning: {len(self.url_dictionaries)}")

        temp_dictionary = {}

        for url_dictionary in self.url_dictionaries:
            url_to_download = url_dictionary["url_to_download"]

            if url_to_download not in temp_dictionary:
                temp_dictionary[url_to_download] = url_dictionary
            else:
                saved_filename = temp_dictionary[url_to_download]["filename"]
                new_filename = url_dictionary["filename"]

                if len(new_filename) > len(saved_filename):
                    temp_dictionary[url_to_download] = url_dictionary

        deduplicated_dictionaries = []

        for k, v in temp_dictionary.items():
            deduplicated_dictionaries.append(v)

        self.url_dictionaries = deduplicated_dictionaries

        log.info(f"After cleaning: {len(self.url_dictionaries)}")

    async def download_url_dictionaries(self):
        self.clean_duplicates()
        log.info("Preparing downloads")

        failed_id = file_category_progress.add_task(
            "Failed", total=self.total_url_dictionaries())

        completed_id = file_category_progress.add_task(
            "Completed", total=self.total_url_dictionaries())

        downloaded_id = file_category_progress.add_task(
            "Downloaded", total=self.total_url_dictionaries())

        fast_semaphore = asyncio.Semaphore(6)
        medium_semaphore = asyncio.Semaphore(4)
        slow_semaphore = asyncio.Semaphore(2)

        already_downloaded_urls = rat_info.get_downloaded_urls()

        for url_dictionary in self.url_dictionaries:

            url_dictionary['progress'] = {}
            url_dictionary['progress']['failed_id'] = failed_id
            url_dictionary['progress']['completed_id'] = completed_id
            url_dictionary['progress']['downloaded_id'] = downloaded_id

            # This is to handle cases where an error dictionary might not
            # have set the url_to_download before encountering an error,
            # but set the correct url to ['url']

            if url_dictionary.get('url_to_download') is None:
                url_dictionary['url_to_download'] = url_dictionary['url']
                continue

            if url_dictionary.get('fail'):
                rat_info.add_error_dictionary(url_dictionary.copy())
                file_category_progress.advance(
                    url_dictionary['progress']['failed_id'], 1)
                continue

            if url_dictionary.get('completed'):
                file_category_progress.advance(
                    url_dictionary['progress']['completed_id'], 1)
                continue

            log.debug("Checking if url has already been downloaded")
            if url_dictionary.get('url_to_record'):
                if url_dictionary['url_to_record'] in already_downloaded_urls:
                    log.info(
                        f"Url already recorded: {url_dictionary['url_to_record']}")
                    file_category_progress.advance(
                        url_dictionary['progress']['completed_id'], 1)
                    continue

            if url_dictionary['url_to_download'] in already_downloaded_urls:
                log.info(
                    f"Url already recorded: {url_dictionary['url_to_download']}")
                file_category_progress.advance(
                    url_dictionary['progress']['completed_id'], 1)
                continue

            log.debug("url has not been downloaded yet")

            if 'media-files' in url_dictionary['url_to_download']:
                self.slow_dictionaries.append(asyncio.create_task(
                    downloader.download_file(url_dictionary.copy(), slow_semaphore)))
                continue

            if 'coomer' in url_dictionary['url_to_download']:
                self.slow_dictionaries.append(asyncio.create_task(
                    downloader.download_file(url_dictionary.copy(), slow_semaphore)))
                continue

            if 'cyberdrop' in url_dictionary['url_to_download']:
                self.medium_dictionaries.append(asyncio.create_task(
                    downloader.download_file(url_dictionary.copy(), medium_semaphore)))
                continue

            self.fast_dictionaries.append(asyncio.create_task(
                downloader.download_file(url_dictionary.copy(), fast_semaphore)))

        if len(self.fast_dictionaries) >= 1:
            log.info("Starting Fast Downloads")
            await asyncio.gather(*self.fast_dictionaries)

        if len(self.medium_dictionaries) >= 1:
            log.info("Starting Medium Downloads")
            await asyncio.gather(*self.medium_dictionaries)

        if len(self.slow_dictionaries) >= 1:
            log.info("Starting Slow Downloads")
            await asyncio.gather(*self.slow_dictionaries)
