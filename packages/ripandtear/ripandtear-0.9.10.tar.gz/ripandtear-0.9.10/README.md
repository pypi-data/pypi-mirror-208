# Ripandtear 

### An asynchronous file archival program

The intention of Ripandtear is to make it easy to save/update content uploaded by content creators online. 
What makes Ripandtear unique is that it stores all information on a user in a .rat file to help condense all the information about a content creator into one location
(don't worry, a .rat is just a .json file with a different extension name). 
From what usernames they use across different websites, to tracking already downloaded URLs and even file names with their MD5 hash to remove duplicates, it's all stored in the .rat for easy convenience when adding new information from the command line. 
You can store all the information about a content creator, archive their content, remove duplicates and sort the files all with one command!

By using the .rat file you eliminate the need for re-downloading the same content and creating duplicate files.
All the previously downloaded Url's are tracked in the .rat file.
If the file has already been downloaded, it is skipped to save you time/data/bandwidth and make fewer requests to servers.
This also makes it convenient if you share a folder that has a .rat file with someone else.
They can pick up where you left off without having to download the same content all over again!


# Installation 

### Requires Python 3.10

(Linux/Mac)

`pip install ripandtear`

(Windows)

`py -m pip install ripandtear`

### Additional Downloads
After downloading ripandtear from your command line run

`playwright install`

Playwright is a webdevelopment tool that opens up a browser in the background. Ripandtear uses this for certain websites to interact with javascript in order to find and download links

### Updating

If you already have ripandtear downloaded you can update it with the following command

(Linux/Mac)

`pip install --upgrade ripandtear`

(Windows)

`py -m pip install --upgrade ripandtear`


## Current Supported Sites

**Bunkr.su**

**Coomer.party**

**Cyberdrop.me**

**Gfycat.com** (only direct links and image pages. Not profiles)

**Gofile.io** (can take passwords if seperated by a `~`. `https://gofile.io/d/Qjakte~yiAjdwl`)

**Imgur.com**

**Jpg.fish**

**Pixl.li**

**Reddit.com**

**Redgifs.com**

**Tiktits.com**

### Store Names

Tell Ripandtear to save names to the below categories with the specific flags. 
If you want to print the names to the screen put a 'p' in front of the flag. 
If syncing is availible add a 's' in front of the flag to download all new content from the site (you cannot print and sync in the same flag: -psr)

chaturbate - `-cb`, `-pcb` (to print)

fansly - `-f`, `-pf` (to print)

instagram - `-i`, `-pi` (to print)

myfreecams - `-mfc`, `-pmfc` (to print)

onlyfans - `-o`, `-po` (to print)

patreon - `-P`, `-pP` (to print)

pornhub - `-p`, `-pp` (to print)

reddit - `-r`, `-pr` (to print), `-sr` (to sync)

redgifs - `-R`, `-pR` (to print), `-sR` (to sync)

tiktits - `-tt`, `-ptt` (to print), `-stt` (to sync)

tiktok - `-T`, `-pT` (to print)

tumblr - `-tum`, `-ptum` (to print)

twitch - `-twitch`, `-ptwitch` (to print)

twitter - `-t`, `-pt` (to print)

youtube - `-y`, `-py` (to print)

### Store Links

Store links to the websites below with the following flags

coomer.party - `-c`, `-pc` (to print), `-sc` (to sync)

simpcity - `-s`, `-ps` (to print)

### Save Urls

Save urls to download and already downloaded urls with the following flags

add url to download - `-u`, `-pu` (to print)

add already downloaded url - `-U`, `-pU` (to print)

## Examples

### Download a link

Ripandtear has extractors to download content from many different content providers (see ***Supported Sites***). The simplest use case is to download content from a supported url


`ripandtear -d 'https://www.supportedsite.com/<content-id>|https://www.differentsite.io/<content-id>.jpg'`

`ripandtear` - the name of the program

`-d` - `-d` stands for download. If Ripandtear recognizes the url it will download all the content it can find into the current directory. You can download multiple links at once by seperating them with commas (,) or even adding multiple `-d` flags in the same command

### Creating a new user

Run Ripandtear with the following flags:

`ripandtear -mk 'Username' -r 'random_reddit_username' -R 'redgifs_username' -sr -sR -H -S`

With this one command you have created a new directory, recorded a reddit and redgifs username in a .rat file, downloaded all the content from each website, found the hashes of the files to remove duplicates and sorted the files into distinct directories based on their type.

Here is what the result of the command:


    Username (<- the directory)
    ├── Username.rat
    ├── pics
    │   └── reddit-2022-01-01-example_pic.png
    └── vids
        └── redgifs-2023-04-12-example_vid.mp4


Inside the directory you created you now have a .rat file with the same name as the directory (the .rat must match have the same name as the directory. Don't worry it is created automatically).
The .rat now contains the usernames you set for reddit and redgifs.
Ripandtear has also downloaded all the content off of reddit and redgifs, hashed the files to remove duplicates, sorted the files into folders respective of their content type and recorded all information into the .rat

Lets walk through the previous command to explain what each flag does:

`ripandtear` - the name of the program

`-mk Username` - Creates a directory with the name of 'Username', then moves into that directory before executing the following commands. 
There is no problem if the directory already exists

`-r 'random_reddit_username'` - the `-r` flag adds the reddit username to the .rat file.

`-R 'redgifs_username'` - the `-R` flag adds the redgifs username to the .rat file.

`-sr` - `-sr` stands for "Sync Reddit". Running this command will look up all the Reddit names saved in the .rat file, then download all content that has not been downloaded yet from the users Reddit profile

`-sR` - `-sR` stands for "Sync Redgifs". Running this command will look up all the Redgifs names saved in the .rat file, then download all content that has not been downloaded yet from the users Redgifs profile

`-H` - `-H` stands for "Hash files". This command hashes all the files in the current directory and removes duplicates. 
If it is run in the same directory with a .rat file it looks in the .rat file to see if newly downloaded content matches older downloaded content. 
If there is a match Ripandtear deletes the file with the shorter filename and keeps the file with the longer username

`-S` - `-S` stand for "Sort files". It sorts the files in the current directory into either pics, vids, audio and text directories depending on the file type. 
If a file does not fit in any of those folders it is kept in the current directory

### Adding another username

You find out that the same content creator uses multiple different reddit names. 
You want to add the new name you found.
Doing that is extreamly easy. 
All you have to do is run the following command:

`ripandtear -r 'new_example_reddit_username|plus_another_username' -r 'even_another_name'`

Ripandtear looks in the current directory for a .rat file. If a .rat doesn't exist is creates one (naming itself after the current directory) and adds the names. 
If it finds a .rat it adds the new username(s) to the already existing .rat file. 
You can even add multiple names at once by separting them with commas (,) and/or multiple identical flags. 
Don't worry about accidentally adding the same name multiple times. 
Ripandtear makes sure that each name stored in the .rat is unique and that there are no duplicates. 
This approach applies for all username categories. See ***stored names*** to see which usernames you can store and the flags to use to set them.

### Adding a website url to download later

Ripandtear has the ability to download content from many different hosting sites. 
See the ***Supported Sites*** section for compatible websites. 
If you want to add a url to the .rat file to be downloaded later you can do it with the following command.

`ripandtear -u 'https://www.examplesite.com/<content-id>.jpg'`

`-u` - `-u` adds a url to be downloaded later. 
It stores raw url's so any url can be stored. 
Saved urls can be downloaded with Ripandtear (if Ripandtear supports the link) with `-su` (sync urls). 
Ripandtear looks at all the stored urls in the .rat, If the url matches an extractor Ripandtear has, it will attempt to download all content.
If the url doesn't match, it will be kept in the .rat for later, either to help you archive links you want to manually download later, or for when Ripandtear adds an extractor to download the content. 
Feel free to add whatever url's you want!


### Syncing errors

Sometimes when downloading, things go wrong.
A server could be down, you could be making so many requests that you were blocked, maybe the content is temporarily unavailible.
Ripandtear keeps track of all urls and information relating to the url if an error occures when attempting a download and saves it for later.
If you want to reattempt failed downloads you can run the command:

`ripandtear -se`

`-se` - `-se` stands for "Sync Errors". Ripandtear will look for any saved errors and attempt them again. If the url works, the error will be removed.
If there is another error Ripandtear will continue to save the url to attempt later.
After 5 attempts Ripandtear assumes getting the content will not be possible to download and move the bad url into the downloaded urls category within the .rat to prevent more attempts in the future.
The errors saved in the .rat can be cleared with the `-ee` (erase errors) and printed with `-pe` (print errors)

### Sync All

If you want to update a user and get all of their new content you can run the following command

`ripandtear -sa -HS` 

`-sa` - `-sa` stand for "Sync All". It syncs all supported sites (see ***supported names***) and stored urls (`-su`). It does not sync errors though (`-se`)

`-SH` - This is a combination of `-S` and `-H`. The order of `-S` and `-H` does not matter when combining them

### Print Urls

Maybe you want to see all availible url's Ripandtear can find. 
Maybe you want to take those url's and save them to a file to be used with a different downloader.
Whatever you want to do, if you want to print all files Ripandtear can find to the screen from a supported site without downloading them, you can run the following command

`ripandtear -g 'https://www.url.com/'`

`-g` - `-g` stands for "Get urls". It prints all the found urls to the screen instead of downloading them. 
On a OS like Linux you can then pipe the output into another command or file

### Add Already Downloaded Urls

If you are coming from another downloader, or have a list of already downloaded urls, you can add them to the .rat with the following command so Ripandtear will skip downloading the url again

`ripandtear -U 'https://url.com/content.jpg'`

`-U` - `-U` adds the url to the already downloaded urls section of the .rat file. This is the information Ripandtear checks before preceding with a download.
If a url to be downloaded is found within this category, it is skipped.
If you are a more advanced Linux user you could run a command like this to move all the urls from a text file into the .rat

`cat location/to/urls.txt | xargs -i ripandtear -U {}`

Just remember that Ripandtear works off the current directory it is in.
Make sure you are located where you want the .rat file to be saved/updated

### Logging to the screen

`ripandtear -l 2 -SH`

By default Ripandtear trys to show as little information as possible to keep the downloading experience very minimal.
Sometimes you might want more information to make sure the program is working, or incase you need to post information online to help with trouble shooting.
You can do this by adding the `-l 2` flag to the command you are executing. 
There are five levels (1-5).
2 is the recommended level for just tracking that Ripandtear is working and see what is happening.
1 is for debugging and will print a LOT of information that won't be useful if you are doing multiple downloads at once, but exists for extreme situations where you need help trouble shooting a single url

# FAQ

> Ripandtear seems to be hanging/has long pauses while downloading. Has it frozen?

Ripandtear tries to keep the information printed to the screen as minimal as possible.
While Ripandtear is trying to find all the downloadable links, it won't print anything to the screen.
If Ripandtear is finding a lot of content this is probably the reason for it to "hang" or seem frozen.
In most cases it is just doing a lot of work in the background so just let it run and it should be fine.
If you are really worried that something might be wrong, run it with the `-l 2` flag.
This will print logging information to the screen and you can get more information about what is going on behind the screen.
Some websites have specific quirks so if you notice it having more problems more often on specific sites check out the ***Website Quirks*** section for more potential causes from that site

> WTF?! I ran Ripandtear, it paused and then just shut down without downloading or printing anything

If you are syncing a users profile Ripandtear only downloads content that has not been downloaded yet.
If the user has not uploaded anything new between the last time you did a sync, then Ripandtear won't download anything.
It not printing anything to the screen just means it didn't find any new content

# Website Quirks

Every website is a unique and beautiful website. Because of this they might have their own little oddities and special behavior.
Here are some potential symptoms you might notice and what is going on behind the scene

### Bunkr
Bunkr file format:

`<content_name>.<extension>`

To be kinder on Bunkr's servers, Ripandtear's Bunkr extractor incorporates random delays.
Finding links will be slower compared to other sites and Ripandtear limits itself to download only 2 videos at once.
All of this is done to prevent 429 errors (Too Many Requests).

### Coomer
Coomer file format:

`coomer-<year>-<month>-<day>-<post-id>-<count>-<content-title>.<extension>`

Currently limited to 4 simultaneous downloads to prevent 429 errors (Too Many Requests)

### Cyberdrop
Cyberdrop file format:

`<content_name>.<extension>`

### Gfycat
Only downloads direct video links and video pages. Not user profiles

Gfycat file format:

`gfycat-<year>-<month>-<day>-<gfycat-id>-<reddit post tile: if sent from reddit>.<extension>`

### Gofile
Gofile file format:

`<content_name>.<extension>`

You can add gofile urls with passwords via the `-d` or `-u` flags if you separte the url and password with a `~`

Example: `https://gofile.io/d/Qjakte~yiAjdwl`

### Imgur
Imgur file format:

`imgur-<year>-<month>-<day>-<album hash: if applicable>-<order: if applicable>-<image hash>-<reddit post title: if sent from reddit>.<extension>`

### Jpg.fish|church
Jpg file format:

`<content_id>.<extension>`

### Pixl
Pixl file format:

`<content_id>.<extension>`

### Reddit

Reddit file format: 

`reddit-<year>-<month>-<day>-<gallery name: if applicable>-<order: if applicable>-<reddit post id>-<post title>.<extension>`

Reddit asks that anybody using their API to download content follows certain rules they have. 
One of the rules is limiting the amount of downloads a user makes in a five minute period (they limit it to 300 requests).
Because Ripandtear is an asynchronous downloader it can easily hit that 300 requests limit in just a minute or two.
To be a respectful downloader (and prevent your IP address and Ripandtear the program from being banned) Ripandtear follows their API rules and times itself out if it hits that requests limit in the 5 minute window.
This means there might be times when downloading a Reddit users profile where Ripandtear will pause until it hits the next 5 minute increment.
For example at 12:02 PM Ripandtear pauses while downloading and "stops working". 
It should start back up again at 12:05 PM when it hits the next 5 minute window.
In some extreme cases it might need to wait 10 minutes.
If Ripandtear has paused for more than 10 minutes then something might be wrong. 
The only time this will really be a problem is if you are doing an initial download of a users profile and they have a lot of content.
After the first download Ripandtear compares all availible links with what has been already downloaded in the .rat and only downloads the new content.
If you are syncing reddit profiles on a regular basis then you shouldn't hit the API limit often (unless the user posts a LOT)

The Reddit extractor also uses yt-dlp to download Reddit videos

### Redgifs
Redgifs file format:

`redgifs-<year>-<month>-<day>-<redgifs_id>-<reddit post title: if passed from reddit>.<extension>`

### Tiktits
Tiktits file format:

`tiktits-<upload_date>-<url/file_name>.<extension>`
