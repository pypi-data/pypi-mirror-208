import argparse


def make_args():
    parser = argparse.ArgumentParser(
        prog='ripandtear', description='A file downloader/archive manager')

    general = parser.add_argument_group('general', 'General Options')
    general.add_argument(
        '-v', '--version', help='prints out the current version', action='store_true')
    general.add_argument('-gd', '--generic-download',
                         help="Generic downloader that doesn't store url", metavar='', action='append')
    general.add_argument(
        '-g', '--get-urls', help='Print URLs instead of downloading', metavar='', action='append')
    general.add_argument('-l', '--log-level',
                         help='Set log level to print to the screen. 1 = debug, 2 = info, 3 = warning, 4 = error, 5 = critical. Ex: -l 1, -l 2', metavar='', action='store')
    general.add_argument('-mk', '--make-dir',
                         help='Make a directory with the given name, moves into it the new dir to exectute commands, then return to original dir when done', metavar='', action='store')
    general.add_argument('-S', '--sort-files',
                         help='Sort files into pics/vids/audio/text directories', action='store_true')
    general.add_argument('-H', '--hash-files',
                         help='Finds the hashes of files and deletes duplicates. If no .rat exists then it will hash the local files. If a .rat exists \
                                 it will compare the file hash with the stored hashes in the .rat and remove the matching file \
                                 with the shorter file name', action='store_true')
    general.add_argument('-ee', '--erase-errors',
                         help='Erase the error directories that are stored in the current .rat file', action='store_true')

    adding = parser.add_argument_group('adding', 'Adds Information to .rat')
    adding.add_argument(
        '-c', '--coomer', help='adds a coomer.party url to the .rat file', metavar='', action='append')
    adding.add_argument('-cb', '--chaturbate',
                        help='adds chaturbate username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1', metavar='', action='append')
    adding.add_argument('-d', '--download',
                        help='give a url to download content from a supported website', metavar='', action='append')
    adding.add_argument('-f', '--fansly', help='adds fansly username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-i', '--instagram', help='adds instagram username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-mfc', '--myfreecams', help='adds myfreecams username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-o', '--onlyfans', help='adds onlyfans username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-O', '--output', help='give a desired name for a downloaded file when combined with -d',
                        metavar='', type=str, action='append')
    adding.add_argument('-p', '--pornhub', help='adds pornhub username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-P', '--patreon', help='adds patreon username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-r', '--reddit', help='adds reddit username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-R', '--redgifs', help='adds redgifs username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument(
        '-s', '--simp', help='adds a simpcity url to the .rat file', metavar='', action='append')
    adding.add_argument('-t', '--twitter', help='adds twitter username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-tt', '--tiktits', help='adds tiktits username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-T', '--tiktok', help='adds tiktok username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-tum', '--tumblr', help='adds tumblr username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-twitch', '--twitch', help='adds twitch username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')
    adding.add_argument('-u', '--url-add', help='saves a url to be downloaded later',
                        metavar='', type=str, action='append')
    adding.add_argument('-U', '--urls-downloaded',
                        help='add a url that has already been downloaded', metavar='', type=str, action='append')
    adding.add_argument('-y', '--youtube', help='adds youtube username to .rat file. Can add multiple names if seperated by a comma (,). Ex: name,name1',
                        metavar='', type=str, action='append')

    printing = parser.add_argument_group(
        'print', 'Prints out information from .rat file')
    printing.add_argument('-pc', '--print-coomer',
                          help='Prints out coomer.party urls', action='store_true')
    printing.add_argument('-pcb', '--print-chaturbate',
                          help='Prints out chaturbate names', action='store_true')
    printing.add_argument('-pe', '--print-errors',
                          help='Prints out stored errors', action='store_true')
    printing.add_argument('-pf', '--print-fansly',
                          help='Prints out fansly names', action='store_true')
    printing.add_argument('-pi', '--print-instagram',
                          help='Prints out instagram names', action='store_true')
    printing.add_argument('-pmfc', '--print-myfreecams',
                          help='Prints out myfreecam names', action='store_true')
    printing.add_argument('-po', '--print-onlyfans',
                          help='Prints out onlyfan names', action='store_true')
    printing.add_argument('-pp', '--print-pornhub',
                          help='Prints out pornhub names', action='store_true')
    printing.add_argument('-pP', '--print-patreon',
                          help='Prints out patreon names', action='store_true')
    printing.add_argument('-pr', '--print-reddit',
                          help='Prints out reddit names', action='store_true')
    printing.add_argument('-pR', '--print-redgifs',
                          help='Prints out redgifs names', action='store_true')
    printing.add_argument('-ps', '--print-simpcity',
                          help='Prints out simpcity urls', action='store_true')
    printing.add_argument('-pt', '--print-twitter',
                          help='Prints out twitter names', action='store_true')
    printing.add_argument('-ptt', '--print-tiktits',
                          help='Prints out tiktits names', action='store_true')
    printing.add_argument('-pT', '--print-tiktok',
                          help='Prints out tiktok names', action='store_true')
    printing.add_argument('-ptum', '--print-tumblr',
                          help='Prints out tumblr names', action='store_true')
    printing.add_argument('-ptwitch', '--print-twitch',
                          help='Prints out twitch names', action='store_true')
    printing.add_argument('-pu', '--print-urls_to_download',
                          help='Prints out urls to download', action='store_true')
    printing.add_argument('-pU', '--print-urls_downloaded',
                          help='Prints out urls already downloaded', action='store_true')
    printing.add_argument('-py', '--print-youtube',
                          help='Prints out youtube names', action='store_true')

    syncing = parser.add_argument_group(
        'sync', 'Downloads the media from the appropriate user pages. Uses the stored usernames from each category to do so')
    syncing.add_argument('-sa', '--sync-all',
                         help='Syncs all availible user profiles', action='store_true')
    syncing.add_argument('-sc', '--sync-coomer',
                         help='Syncs all links stored under coomer.party', action='store_true')
    syncing.add_argument('-se', '--sync-errors',
                         help='Syncs the stored error directories in the .rat file', action='store_true')
    syncing.add_argument('-sr', '--sync-reddit',
                         help='Syncs Reddit users profile', action='store_true')
    syncing.add_argument('-sR', '--sync-redgifs',
                         help='Syncs Redgifs user profile', action='store_true')
    syncing.add_argument('-stt', '--sync-tiktits',
                         help='Syncs Tiktits user profile', action='store_true')
    syncing.add_argument('-su', '--sync-urls-to-download',
                         help='Downloads urls in the urls to download category within a .rat (urls can be added here with -u)', action='store_true')

    return parser
