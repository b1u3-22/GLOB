# GLOB

## General Literally Obligatory Bot

* Bot with all the general functions that you could ever need!
* Managed with *Cog* system, so you can add other modules
* You can also unload modules that you don't want

## [Join the test server](https://discord.gg/d4Fwf5Gu9b) or [Invite GLOB to yours](https://discord.com/api/oauth2/authorize?client_id=781629601105444946&permissions=502791286&scope=bot)!

[<img src="resources/server_icon.png" width = "100" height = "100">](https://discord.gg/d4Fwf5Gu9b) [<img src="resources/glob_icon.png" width = "100" height = "100">](https://discord.com/api/oauth2/authorize?client_id=781629601105444946&permissions=502791286&scope=bot)

## *Cog* management
* All modules are stored in `GLOB/cogs`
* If you don't want to use certain modules you can just delete them from there
* Same applies for adding your own modules
### Reloading, loading and unloading *cogs*
* GLOB has these functions programmed as commands
* To **reload** *cog*
  * `.reload {cog_name}`
* To **load** *cog*
  * `.load {cog_name}`
* To **unload** *cog*
  * `.unload {cog_name}`

## Short feature list
### Music
* Play, Pause and Stop songs
* Create Playlist that can be loaded anytime from database
* Queue songs, change their position in queue or skip them
* Tell GLOB to send you the currently playing song to DMs
### Fun
* Hangman game
* Images from Reddit
  * Predefined commands to get images from `r/cats`, `r/Birbs` and some others
  * You can get random image from any subreddit using `.subreddit {subreddit name}`
* Write down things that somebody has said with `citation` *cog*
### Management
* Votekick and voteban
* Change roles and nicknames
* Make announcements
  * GLOB let's you create messages formated in *embeds* and sends them to channel that's configured as **Announcement channel**

## How to selfhost GLOB
### With venv or on its own
1) Clone this repository
  * `git clone https://github.com/Simpleton-Yogy/GLOB.git`
2) Create `.env` file
  * `cd GLOB`
  * `nano .env`
  * Things needed in .env:
    * `DISCORD_TOKEN`
  * If you are using the `reddit` *cog*:
    * `REDDIT_USERNAME`
      * Username of your Reddit Account
    * `REDDIT_ID`
      * ID of application created in [Reddit settings](https://www.reddit.com/prefs/apps/)
    * `REDDIT_PASSWORD`
      * Password to your Reddit Account
    * `REDDIT_SECRET`
      * Secret that can be found in your app created in the Reddit Settings
    * `REDDIT_USERAGENT`
      * Description of service that would be making requests
      * For example: `Discord_Bot_GLOBv1_(by u/RedditUser)`
3) Install requirements
  * `pip install -r requirements.txt`
4) Start GLOB
  * `python bot.py`

### Using Docker
* Thanks to [satcom886](https://github.com/satcom886) GLOB has a Dockerfile and so can be served in Docker  

Images are available on [Docker Hub](https://hub.docker.com/r/satcom886/glob). The table below explains the tags.

|  Tag   |   Update   |                                 Description                                                 |
|:------:|:----------:|:-------------------------------------------------------------------------------------------:|
| latest |   on push  | Built automatically using a GitHub Action                                                   |
| stable | irregularly | Built by [satcom886](https://github.com/satcom886) whenever a version is mostly working    |

In both instances, you need to set the `DISCORD_TOKEN` variable. Optionally you can choose a place to store GLOB's database using a mount point. GLOB stores its data in `/GLOB/data`, so you can bind-mount that wherever you want. If you don't set a mount point for GLOB's data, GLOB won't remember your settings and data.

#### Pure Docker

```
docker run \
 -e DISCORD_TOKEN="your_discord_token" \
 -e REDDIT_USERNAME="meeeeee" \
 -e REDDIT_ID="smt" \
 -e REDDIT_PASSWORD="VerySecret" \
 -e REDDIT_SECRET="MoreSecret" \
 -e REDDIT_USERAGENT="NetScape-Navigator" \
 --mount type=bind,source=/your/datadir,target=/GLOB/data \
 satcom886/glob
```

#### Using `docker-compose`

```yaml
version: "3.5"
services:
  glob:
    image: satcom886/glob
    ## Uncomment to auto-start
    # restart: unless-stopped
    volumes:
      - /your/datadir:/GLOB/data
    environment:
      DISCORD_TOKEN: "your_discord_token"
      REDDIT_USERNAME: "meeeeee"
      REDDIT_ID: "smt"
      REDDIT_PASSWORD: "VerySecret"
      REDDIT_SECRET: "MoreSecret"
      REDDIT_USERAGENT: "Netscape-Navigator"
```
