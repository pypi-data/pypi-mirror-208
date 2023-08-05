import asyncio
import logging
import sys
from pathlib import Path
import os

from ripandtear.__init__ import __version__
from ripandtear.utils import cli_arguments, content_finder, file_hasher, file_sorter, logger, rat_info


async def main():

    try:

        parser = cli_arguments.make_args()
        args = parser.parse_args()

        if args.version:
            print(f"version: {__version__}")

        if args.make_dir:
            Path(args.make_dir).mkdir(exist_ok=True)
            os.chdir(Path(args.make_dir).resolve())

        if args.log_level:

            if args.log_level == '1' or args.log_level.lower() == 'debug':
                level = logging.DEBUG
                logger.create_logger(level)
                log = logging.getLogger(__name__)
                log.debug("logging working")

            elif args.log_level == '2' or args.log_level.lower() == 'info':
                level = logging.INFO
                logger.create_logger(level)
                log = logging.getLogger(__name__)
                log.info("logging working")

            elif args.log_level == '3' or args.log_level.lower() == 'warning':
                level = logging.WARNING
                logger.create_logger(level)
                log = logging.getLogger(__name__)
                log.warning("logging working")

            elif args.log_level == '4' or args.log_level.lower() == 'error':
                level = logging.ERROR
                logger.create_logger(level)
                log = logging.getLogger(__name__)
                log.error("logging working")

            elif args.log_level == '5' or args.log_level.lower() == 'critical':
                level = logging.CRITICAL
                logger.create_logger(level)
                log = logging.getLogger(__name__)
                log.critical("logging working")

            else:
                print("Incorrect input to get logging")
        else:
            level = logging.CRITICAL
            logger.create_logger(level)

        if args.print_chaturbate:
            rat_info.print_rat('names', 'chaturbate')

        if args.print_coomer:
            rat_info.print_rat('links', 'coomer')

        if args.print_errors:
            rat_info.print_rat('errors')

        if args.print_fansly:
            rat_info.print_rat('names', 'fansly')

        if args.print_instagram:
            rat_info.print_rat('names', 'instagram')

        if args.print_myfreecams:
            rat_info.print_rat('names', 'myfreecams')

        if args.print_reddit:
            rat_info.print_rat('names', 'reddit')

        if args.print_redgifs:
            rat_info.print_rat('names', 'redgifs')

        if args.print_onlyfans:
            rat_info.print_rat('names', 'onlyfans')

        if args.print_patreon:
            rat_info.print_rat('names', 'patreon')

        if args.print_pornhub:
            rat_info.print_rat('names', 'pornhub')

        if args.print_simpcity:
            rat_info.print_rat('links', 'simpcity')

        if args.print_tiktok:
            rat_info.print_rat('names', 'tiktok')

        if args.print_tiktits:
            rat_info.print_rat('names', 'tiktits')

        if args.print_tumblr:
            rat_info.print_rat('names', 'tumblr')

        if args.print_twitter:
            rat_info.print_rat('names', 'twitter')

        if args.print_twitch:
            rat_info.print_rat('names', 'twitch')

        if args.print_urls_downloaded:
            rat_info.print_rat('urls_downloaded')

        if args.print_urls_to_download:
            rat_info.print_rat('urls_to_download')

        if args.print_youtube:
            rat_info.print_rat('names', 'youtube')

        if args.reddit:
            for entry in args.reddit:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'reddit', name)

        if args.redgifs:
            for entry in args.redgifs:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'redgifs', name)

        if args.onlyfans:
            for entry in args.onlyfans:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'onlyfans', name)

        if args.fansly:
            for entry in args.fansly:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'fansly', name)

        if args.pornhub:
            for entry in args.pornhub:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'pornhub', name)

        if args.twitter:
            for entry in args.twitter:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'twitter', name)

        if args.tiktits:
            for entry in args.tiktits:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'tiktits', name)

        if args.instagram:
            for entry in args.instagram:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'instagram', name)

        if args.youtube:
            for entry in args.youtube:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'youtube', name)

        if args.tiktok:
            for entry in args.tiktok:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'tiktok', name)

        if args.twitch:
            for entry in args.twitch:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'twitch', name)

        if args.patreon:
            for entry in args.patreon:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'patreon', name)

        if args.tumblr:
            for entry in args.tumblr:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'tumblr', name)

        if args.myfreecams:
            for entry in args.myfreecams:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'myfreecams', name)

        if args.chaturbate:
            for entry in args.chaturbate:
                for name in entry.split('|'):
                    rat_info.update_rat('names', 'chaturbate', name)

        if args.simp:
            for entry in args.simp:
                for url in entry.split('|'):
                    rat_info.update_rat('links', 'simpcity', url)

        if args.coomer:
            for entry in args.coomer:
                for url in entry.split('|'):
                    rat_info.update_rat('links', 'coomer', url)

        if args.url_add:
            for entry in args.url_add:
                for url in entry.split('|'):
                    rat_info.update_rat('urls_to_download', None, url)

        if args.urls_downloaded:
            for entry in args.urls_downloaded:
                for url in entry.split('|'):
                    rat_info.update_rat('urls_downloaded', None, url)

        if args.erase_errors:
            rat_info.erase_error_dictionaries()

        if args.get_urls or \
                args.download or \
                args.generic_download or \
                args.sync_all or \
                args.sync_errors or \
                args.sync_reddit or \
                args.sync_redgifs or \
                args.sync_tiktits or \
                args.sync_coomer or \
                args.sync_urls_to_download:

            await content_finder.run(args)

        if args.hash_files:
            await file_hasher.file_hasher()

        if args.sort_files:

            await file_sorter.sort()

    except KeyboardInterrupt:
        print()
        print("Cancelled via keyboard")


def launch():

    try:
        sys.exit(asyncio.run(main()))

    except KeyboardInterrupt:
        sys.exit("\nCancelled via keyboard")

    except RuntimeError:
        pass


if __name__ == "__main__":
    launch()
