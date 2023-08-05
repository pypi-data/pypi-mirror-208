from ripandtear.utils import rat_info
from ripandtear.__main__ import args


async def run(args):
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
            for name in entry.split(','):
                rat_info.update_rat('names', 'reddit', name)

    if args.redgifs:
        for entry in args.redgifs:
            for name in entry.split(','):
                rat_info.update_rat('names', 'redgifs', name)

    if args.onlyfans:
        for entry in args.onlyfans:
            for name in entry.split(','):
                rat_info.update_rat('names', 'onlyfans', name)

    if args.fansly:
        for entry in args.fansly:
            for name in entry.split(','):
                rat_info.update_rat('names', 'fansly', name)

    if args.pornhub:
        for entry in args.pornhub:
            for name in entry.split(','):
                rat_info.update_rat('names', 'pornhub', name)

    if args.twitter:
        for entry in args.twitter:
            for name in entry.split(','):
                rat_info.update_rat('names', 'twitter', name)

    if args.tiktits:
        for entry in args.tiktits:
            for name in entry.split(','):
                rat_info.update_rat('names', 'tiktits', name)

    if args.instagram:
        for entry in args.instagram:
            for name in entry.split(','):
                rat_info.update_rat('names', 'instagram', name)

    if args.youtube:
        for entry in args.youtube:
            for name in entry.split(','):
                rat_info.update_rat('names', 'youtube', name)

    if args.tiktok:
        for entry in args.tiktok:
            for name in entry.split(','):
                rat_info.update_rat('names', 'tiktok', name)

    if args.twitch:
        for entry in args.twitch:
            for name in entry.split(','):
                rat_info.update_rat('names', 'twitch', name)

    if args.patreon:
        for entry in args.patreon:
            for name in entry.split(','):
                rat_info.update_rat('names', 'patreon', name)

    if args.tumblr:
        for entry in args.tumblr:
            for name in entry.split(','):
                rat_info.update_rat('names', 'tumblr', name)

    if args.myfreecams:
        for entry in args.myfreecams:
            for name in entry.split(','):
                rat_info.update_rat('names', 'myfreecams', name)

    if args.chaturbate:
        for entry in args.chaturbate:
            for name in entry.split(','):
                rat_info.update_rat('names', 'chaturbate', name)

    if args.simp:
        for entry in args.simp:
            for url in entry.split(','):
                rat_info.update_rat('links', 'simpcity', url)

    if args.coomer:
        for entry in args.coomer:
            for url in entry.split(','):
                rat_info.update_rat('links', 'coomer', url)

    if args.url_add:
        for entry in args.url_add:
            for url in entry.split(','):
                rat_info.update_rat('urls_to_download', None, url)

    if args.urls_downloaded:
        for entry in args.urls_downloaded:
            for url in entry.split(','):
                rat_info.update_rat('urls_downloaded', None, url)

    if args.erase_errors:
        rat_info.erase_error_dictionaries()

    return
