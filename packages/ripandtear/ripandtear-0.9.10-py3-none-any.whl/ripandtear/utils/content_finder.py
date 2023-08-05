import asyncio
import os
import logging

from ripandtear.utils.custom_types import UrlDictionary
from ripandtear.utils import conductor, rat_info
from ripandtear.utils.tracker import Tracker
from ripandtear.utils.progress import search_table, search_info, search_message, download_table
from rich.live import Live

log = logging.getLogger(__name__)


async def run(args):

    tracker = Tracker.getInstance()

    url_dictionary = await create_progress_info()

    if args.get_urls:

        await print_urls(args, url_dictionary)
        return

    log.debug("Staring search for content")
    table = await search_table()
    with Live(table, refresh_per_second=16):

        # if args.download:
        #
        #     await download_urls(args, url_dictionary.copy())
        #     return

        if args.download:

            await download_urls(args, url_dictionary.copy())

        if args.sync_all:
            await sync_all(url_dictionary.copy())

        if args.sync_errors:
            await sync_errors()

        if args.sync_reddit:
            await sync_reddit(url_dictionary.copy())

        if args.sync_redgifs:
            await sync_redgifs(url_dictionary.copy())

        if args.sync_tiktits:
            await sync_tiktits(url_dictionary.copy())

        if args.sync_coomer:
            await sync_coomer(url_dictionary.copy())

        if args.sync_urls_to_download:
            await sync_urls_to_download(url_dictionary.copy())

    if args.log_level is None:

        if os.name == 'nt':
            _ = os.system('cls')

        else:
            _ = os.system('clear')

    log.debug("Finished search for content")

    log.debug("Starting downloads")
    table = await download_table()
    with Live(table, refresh_per_second=16):
        await tracker.download_url_dictionaries()

    log.debug("Finished downloaded. Returning to __main__")
    return


async def create_progress_info() -> UrlDictionary:

    search_id = search_info.add_task("Searching", total=None)
    url_dictionary = {}
    url_dictionary['progress'] = {}
    url_dictionary['progress']['search_object'] = search_info
    url_dictionary['progress']['search_id'] = search_id
    url_dictionary['progress']['search_message'] = search_message

    return url_dictionary


def url_dictionary_constructor(url: str, url_dictionary: UrlDictionary, download: bool) -> UrlDictionary:

    url_dictionary['url'] = url

    url_dictionary['download'] = download

    return url_dictionary


async def download_urls(args, url_dictionary: UrlDictionary) -> None:

    tasks = []
    for entry in args.download:
        for url in entry.split('|'):

            url_dictionary: UrlDictionary = url_dictionary_constructor(
                url.strip(), url_dictionary.copy(), download=True)

            tasks.append(asyncio.create_task(
                conductor.validate_url(url_dictionary.copy())))

    await asyncio.gather(*tasks)


async def print_urls(args, url_dictionary: UrlDictionary) -> None:

    tracker = Tracker.getInstance()

    tasks = []

    for entry in args.get_urls:
        for url in entry.split('|'):

            new_url_dictionary: UrlDictionary = url_dictionary_constructor(
                url.strip(), url_dictionary.copy(), download=False)

            tasks.append(asyncio.create_task(
                conductor.validate_url(new_url_dictionary.copy())))

    await asyncio.gather(*tasks)
    await tracker.print_urls()


async def sync_reddit(url_dictionary: UrlDictionary) -> None:

    reddit_names: list[str] = rat_info.print_rat(
        'names', 'reddit', respond=True)

    if len(reddit_names) >= 1:

        tasks = []
        for name in reddit_names:
            url: str = f"https://www.reddit.com/user/{name}/submitted"
            new_url_dictionary: UrlDictionary = url_dictionary_constructor(
                url, url_dictionary.copy(),  download=True)
            tasks.append(asyncio.create_task(
                conductor.validate_url(new_url_dictionary.copy())))
        await asyncio.gather(*tasks)

    else:
        return


async def sync_redgifs(url_dictionary: UrlDictionary) -> None:

    redgifs_names: list[str] = rat_info.print_rat(
        'names', 'redgifs', respond=True)

    if len(redgifs_names) >= 1:

        tasks = []
        for name in redgifs_names:
            url: str = f"https://www.redgifs.com/users/{name}"
            new_url_dictionary: UrlDictionary = url_dictionary_constructor(
                url, url_dictionary.copy(), download=True)
            tasks.append(asyncio.create_task(
                conductor.validate_url(new_url_dictionary.copy())))
        await asyncio.gather(*tasks)

    else:
        return


async def sync_tiktits(url_dictionary: UrlDictionary) -> None:

    tiktits_names: list[str] = rat_info.print_rat(
        'names', 'tiktits', respond=True)

    try:
        if len(tiktits_names) >= 1:

            tasks = []
            for name in tiktits_names:
                url: str = f"https://tiktits.com/users/{name}"
                new_url_dictionary: UrlDictionary = url_dictionary_constructor(
                    url, url_dictionary.copy(), download=True)
                tasks.append(asyncio.create_task(
                    conductor.validate_url(new_url_dictionary.copy())))
            await asyncio.gather(*tasks)

        else:
            return

    except TypeError:
        pass


async def sync_coomer(url_dictionary: UrlDictionary) -> None:

    urls_to_download = rat_info.print_rat(
        category_1='links', category_2='coomer', respond=True)

    if len(urls_to_download) >= 1:

        tasks = []
        for url in urls_to_download:
            new_url_dictionary: UrlDictionary = url_dictionary_constructor(
                url, url_dictionary.copy(), download=True)
            tasks.append(asyncio.create_task(
                conductor.validate_url(new_url_dictionary.copy())))
        await asyncio.gather(*tasks)

    else:
        return


async def sync_urls_to_download(url_dictionary: UrlDictionary) -> None:

    urls_to_download = rat_info.get_urls_to_download()

    if len(urls_to_download) >= 1:

        tasks = []
        for url in urls_to_download:
            new_url_dictionary: UrlDictionary = url_dictionary_constructor(
                url, url_dictionary.copy(), download=True)
            tasks.append(asyncio.create_task(
                conductor.validate_url(new_url_dictionary.copy())))
        await asyncio.gather(*tasks)

    else:
        return


async def sync_errors() -> None:

    error_dictionaries = rat_info.get_error_dictionaries()

    if len(error_dictionaries) >= 1:

        tracker = Tracker.getInstance()

        tasks = []
        for url_dictionary in error_dictionaries:
            tasks.append(asyncio.create_task(
                tracker.add_url_dictionary(url_dictionary.copy())))

        await asyncio.gather(*tasks)

    else:
        return


async def sync_all(url_dictionary: UrlDictionary) -> None:

    await sync_reddit(url_dictionary)
    await sync_redgifs(url_dictionary)
    await sync_tiktits(url_dictionary)
    await sync_coomer(url_dictionary)
    await sync_urls_to_download(url_dictionary)
