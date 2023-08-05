import json
import logging

from pathlib import Path


log = logging.getLogger(__name__)

rat_template = '''
{
  "names": {
    "reddit": [],
    "redgifs": [],
    "onlyfans": [],
    "fansly": [],
    "pornhub": [],
    "twitter": [],
    "instagram": [],
    "tiktits": [],
    "youtube": [],
    "tiktok": [],
    "twitch": [],
    "patreon": [],
    "tumblr": [],
    "myfreecams": [],
    "chaturbate": []
  },
  "links": {
    "coomer": [],
    "simpcity": []
  },
  "urls_to_download": [],
  "urls_downloaded": [],
  "file_hashes": {},
  "error_dictionaries": []
}
'''


def get_rat_name():
    log.debug("Returning .rat name")
    return Path.cwd().stem + '.rat'


def get_rat_template():
    log.debug("Returning copy of rat template")
    return json.loads(rat_template)


def write_rat_file(template):
    log.debug("Writing rat file")
    rat_name = get_rat_name()
    with open(f"{rat_name}", 'w') as f:
        json.dump(template, f, indent=2)


def rat_file_exists():
    log.debug("Checking if .rat file exists")
    dir_name = Path.cwd().stem
    file = list(Path.cwd().glob(f"{dir_name}.rat"))

    if len(file) > 1:
        log.info("Too many .rat files")
        return False

    elif len(file) == 0:
        # rat_name = get_rat_name()
        # template = json.loads(rat_template)
        log.info("Missing .rat file")
        return False

    elif len(file) == 1:
        return True


def get_rat_info():
    log.debug("Returning stored information from the .rat")

    if rat_file_exists():
        rat_name = get_rat_name()
        with open(f'{rat_name}', 'r') as f:
            rat_contents = json.load(f)
        return rat_contents
    else:
        return 'missing'


def check_existence(category_1, entry):

    rat_contents = get_rat_info()
    if rat_contents == 'too_many' or rat_contents == 'missing':
        pass

    else:

        if category_1 == 'urls_downloaded':
            if entry in rat_contents['urls_downloaded']:
                return True
            else:
                return False


def add_entry(**kwargs):
    if kwargs:
        if kwargs['category_1']:
            category_1 = kwargs['category_1']

        if kwargs['entry']:
            entry = str(kwargs['entry'])

    rat_contents = get_rat_info()
    if rat_contents == 'too_many' or rat_contents == 'missing':
        pass

    else:

        if category_1 == 'urls_downloaded':
            stored_urls = rat_contents['urls_downloaded']
            stored_urls.append(entry)
            rat_contents['urls_downloaded'] = sorted(list(set(stored_urls)))

        rat_name = get_rat_name()
        with open(f"{rat_name}", 'w') as f:
            json.dump(rat_contents, f, indent=2)


def print_rat(category_1, category_2=None, respond=False):

    rat_contents = get_rat_info()

    if rat_contents == 'too_many':
        print("Too many .rat files found")

    elif rat_contents == 'missing':
        print("No .rat file found")

    else:
        try:
            entries: list[str] = []

            if category_1 == 'names':

                for x in rat_contents['names'][category_2]:
                    entries.append(x)

            if category_1 == 'links':
                for x in rat_contents['links'][category_2]:
                    entries.append(x)

            elif category_1 == 'urls_to_download':
                for x in rat_contents['urls_to_download']:
                    entries.append(x)

            elif category_1 == 'urls_downloaded':
                for x in rat_contents['urls_downloaded']:
                    entries.append(x)

            elif category_1 == 'errors':
                for x in rat_contents['error_dictionaries']:
                    entries.append(x)

            if respond is True:
                return entries

            else:
                print(*entries, sep='\n')

        except KeyError:
            log.debug("No Entry Found")


def synced_rat_template():

    log.debug("Syncing the current .rat info with the current template")
    rat_contents = get_rat_info()

    if rat_contents == 'too_many':
        log.warn("Too many .rat files found")
        return

    elif rat_contents == 'missing':

        template = get_rat_template()
        return template

    else:

        template = get_rat_template()

        for name in rat_contents['names']:
            if name == 'reddit':
                template['names']['reddit'] = rat_contents['names']['reddit']

            if name == 'redgifs':
                template['names']['redgifs'] = rat_contents['names']['redgifs']

            if name == 'onlyfans':
                template['names']['onlyfans'] = rat_contents['names']['onlyfans']

            if name == 'fansly':
                template['names']['fansly'] = rat_contents['names']['fansly']

            if name == 'pornhub':
                template['names']['pornhub'] = rat_contents['names']['pornhub']

            if name == 'twitter':
                template['names']['twitter'] = rat_contents['names']['twitter']

            if name == 'instagram':
                template['names']['instagram'] = rat_contents['names']['instagram']

            if name == 'youtube':
                template['names']['youtube'] = rat_contents['names']['youtube']

            if name == 'tiktok':
                template['names']['tiktok'] = rat_contents['names']['tiktok']

            if name == 'tiktits':
                template['names']['tiktits'] = rat_contents['names']['tiktits']

            if name == 'twitch':
                template['names']['twitch'] = rat_contents['names']['twitch']

            if name == 'patreon':
                template['names']['patreon'] = rat_contents['names']['patreon']

            if name == 'tumblr':
                template['names']['tumblr'] = rat_contents['names']['tumblr']

            if name == 'myfreecams':
                template['names']['myfreecams'] = rat_contents['names']['myfreecams']

            if name == 'chaturbate':
                template['names']['chaturbate'] = rat_contents['names']['chaturbate']

        for link in rat_contents['links']:

            if link == 'coomer':
                template['links']['coomer'] = rat_contents['links']['coomer']

            if link == 'simpcity':
                template['links']['simpcity'] = rat_contents['links']['simpcity']

        for url in rat_contents['urls_to_download']:
            template['urls_to_download'].append(url)

        for url in rat_contents['urls_downloaded']:
            template['urls_downloaded'].append(url)

        if rat_contents.get('file_hashes'):
            template['file_hashes'] = rat_contents['file_hashes']

        else:
            template['file_hashes'] = {}

        if rat_contents.get('error_dictionaries'):
            template['error_dictionaries'] = rat_contents['error_dictionaries']

        else:
            template['error_dictionaries'] = []

        return template


def update_rat(category_1, category_2=None, category_3=None):

    log.debug("Updating the .rat with new info")
    template = synced_rat_template()

    if category_1 == 'names':
        x = template['names'][category_2]
        x.append(category_3.strip())
        template['names'][category_2] = sorted(list(set(x)))

    if category_1 == 'links':
        x = template['links'][category_2]
        x.append(category_3.strip())
        template['links'][category_2] = sorted(list(set(x)))

    if category_1 == 'urls_to_download':
        template['urls_to_download'].append(category_3.strip())

    if category_1 == 'urls_downloaded':
        template['urls_downloaded'].append(category_3.strip())

    if category_1 == 'file_hashes':
        template['file_hashes'] = category_2

    write_rat_file(template)


def get_file_hashes() -> dict[str, str]:

    if rat_file_exists():
        template = synced_rat_template()
        return template['file_hashes']

    else:
        return


def get_urls_to_download() -> list[str] | list:

    if rat_file_exists():
        template = synced_rat_template()
        return template['urls_to_download']

    else:
        return []


def get_downloaded_urls() -> list[str] | list:

    if rat_file_exists():
        template = synced_rat_template()
        return template['urls_downloaded']

    else:
        return []


def add_error_dictionary(url_dictionary):

    if rat_file_exists() is False:
        return

    template = synced_rat_template()

    # Clean up keys that will create problems
    # when storing and during the next attempted sync

    if url_dictionary.get('response'):
        del url_dictionary['response']

    if url_dictionary.get('progress'):
        del url_dictionary['progress']

    if url_dictionary.get('fail'):
        del url_dictionary['fail']

    error_dictionaries = template['error_dictionaries']
    if len(error_dictionaries) == 0:
        url_dictionary['retries'] = 1
        template['error_dictionaries'] = []
        template['error_dictionaries'].append(url_dictionary)
        write_rat_file(template)

    else:
        already_stored = False
        try:
            for index, error_dictionary in enumerate(template['error_dictionaries']):
                for key, value in error_dictionary.items():
                    if key == 'url' and value == url_dictionary['url']:
                        already_stored = True
                        count = error_dictionary['retries']
                        count += 1
                        log.debug(
                            f"url_dictionary has already been stored. Increasing error attempt count to {count}")
                        if count > 5:
                            log.warn(
                                f"Already attempted 5 times. Removing from being attempted again. {url_dictionary['url_to_download']}")
                            del template['error_dictionaries'][index]
                        else:
                            template['error_dictionaries'][index]['retries'] = count
        except KeyError:
            pass

        if already_stored is False:
            log.debug(
                f"url_dictionary has not had an error yet. Storing it for later")
            url_dictionary['retries'] = 1
            template['error_dictionaries'].append(url_dictionary)

        write_rat_file(template)


def remove_error_dictionary(url_dictionary):

    template = synced_rat_template()

    for index, error_url_dictionary in enumerate(template['error_dictionaries']):
        for key, value in error_url_dictionary:
            if key == 'urls_to_download' and value == url_dictionary['urls_to_download']:
                del template['error_dictionaries'][index]

    write_rat_file(template)


def get_error_dictionaries():

    template = synced_rat_template()

    return template['error_dictionaries']


def erase_error_dictionaries():

    log.debug("Erasing error dictionaries")

    template = synced_rat_template()

    template['error_dictionaries'] = []

    write_rat_file(template)
