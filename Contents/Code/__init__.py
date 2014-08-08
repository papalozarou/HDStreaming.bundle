################################################################################
# Python Imports
################################################################################
# This is only needed for picking a randomised IP address from CHANNEL_IPS array
import random

################################################################################
# Global variables for channel
################################################################################
TITLE                           = "HD Streaming"
PREFIX                          = "/video/hdstreaming"

ART                             = "art-default.png"
ICON                            = "icon-default.png"

# Below values lifted from FilmOn plugin
USER_AGENT                      = 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
REFERER                         = "http://news-source.tv/"
CUSTOM_HEADERS                  = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                                    'Accept-Encoding': 'gzip,deflate,sdch',
                                    'Accept-Language': 'en-US,en;q=0.8,es;q=0.6',
                                    'Cache-Control': 'max-age=0',
                                    'Connection': 'keep-alive'}

URL_BASE                        = "http://hd-streaming.tv/"
URL_LOGIN                       = "api/?request=login"
URL_LIVE                        = "watch/livehds"
URL_UPCOMING                    = "watch/upcoming-matches"
# N.B. Suffix includes file extension .m3u8
URL_SUFFIX                      = ".m3u8?s=6hfu0"

# Global variable for channels
CHANNEL_IPS                     = ["5.63.145.149",
                                    "5.63.145.189",
                                    "80.82.65.14",
                                    "80.82.65.180",
                                    "80.82.69.240",
                                    "80.82.78.62",
                                    "89.248.160.222",
                                    "89.248.171.15",
                                    "93.174.91.104",
                                    "94.102.48.81",
                                    "94.102.49.152",
                                    "146.185.28.197"]
CHANNEL_LIST                    = []

################################################################################
# Initialise the channel
################################################################################
def Start():
    # Set header and referer
    HTTP.Headers["User-agent"]  = USER_AGENT
    HTTP.Headers["Referer"]     = REFERER
    
    # Set title and art
    ObjectContainer.title1      = TITLE
    ObjectContainer.art         = R(ART)
    
################################################################################
# Build the main menu
################################################################################  
@handler(PREFIX, TITLE, thumb = ICON, art = ART)

def MainMenu():    
    # Open and ObjectContainer for the main menu
    MAIN_MENU                   = ObjectContainer()
    
    # Add the live streams HD object
    MAIN_MENU.add(
        DirectoryObject(
            title               = "HD Streams",
            thumb               = R("icon-live-streams-hd.png"),
            summary             = "High definition streams",
            key                 = Callback(
                LiveStreamsHD,
                title           = "HD Streams"
            )
        )
    )
    
    # Add the live streams SD object
    MAIN_MENU.add(
        DirectoryObject(
            title               = "SD Streams",
            thumb               = R("icon-live-streams-sd.png"),
            summary             = "Standard definition streams",
            key                 = Callback(
                LiveStreamsSD,
                title           = "SD Streams"
            )
        )
    )
    
    # Add the today's streams object
    # MAIN_MENU.add(
    #     DirectoryObject(
    #         title               = "Today's Streams",
    #         thumb               = R("icon-todays-streams.png"),
    #         summary             = "What's on today",
    #         key                 = Callback(
    #             TodaysStreams,
    #             title           = "Today's Streams"
    #         )
    #     )
    # )
    
    # Add the upcoming streams object
    # MAIN_MENU.add(
    #     DirectoryObject(
    #         title               = "Upcoming Streams",
    #         thumb               = R("icon-upcoming-streams.png"),
    #         summary             = "What's on in the near future",
    #         key                 = Callback(
    #             UpcomingStreams,
    #             title           = "Upcoming Streams"
    #         )
    #     )
    # )
    
    # Add the preferences object
    MAIN_MENU.add(
        PrefsObject(
            title               = "Preferences",
            thumb               = R("icon-preferences.png"),
            summary             = "Enter your username and password\r\nThe plugin will not work without them"
        )
    )
    
    return MAIN_MENU

################################################################################
# Validate users preferences (username and password)
################################################################################  
def ValidatePrefs(): 
    # Reset the dictionary that contains the login status
    Dict.Reset()
       
    # Test for username AND password
    if Prefs["username"] and Prefs["password"]:
        # If both are present, authenticate the user
        AuthenticateUser()
        
        # Shows message based on authentication attempt
        if "Login" in Dict:
            # Successful login
            ALERT               = SuccessLoggedIn()
        else:
            # Incorrect username or password error
            ALERT               = ErrorIncorrectLogin()
    else:
        # Missing username or password error
        ALERT                   = ErrorMissingLogin()
    
    return ALERT
    
################################################################################
# Live streams HD menu
################################################################################   
# Set the route for the live streams hd menu
@route(PREFIX + "/hd-streams")

def LiveStreamsHD(title):
    # Log the user in initially
    AuthenticateUser
    
    # Test to see if user is logged in
    if "Login" in Dict:
        # Open an ObjectContainer for the live streams HD menu
        LIVE_STREAMS_HD_MENU    = ObjectContainer(
            title1              = title
        )
  
        # Gets the channel list
        CHANNEL_LIST            = GetChannelList()
        
        # Loop through each channel to produce an EpisodeObject
        for CHANNEL in CHANNEL_LIST:
            # Defines channel details from returned channel data
            CHANNEL_QUALITY     = "hd"
            CHANNEL_TITLE       = CHANNEL[0] + " " + CHANNEL_QUALITY.upper()
            CHANNEL_SUMMARY     = CHANNEL[1]
            CHANNEL_NUMBER      = CHANNEL[0].replace("Channel ","channel")
            CHANNEL_THUMB       = "icon-" + CHANNEL[0].replace("Channel ","channel-") + "-" + CHANNEL_QUALITY + ".png"
            
            # Gets channel episode object and adds to menu
            LIVE_STREAMS_HD_MENU.add(CreateChannelEpisodeObject(CHANNEL_QUALITY,CHANNEL_TITLE,CHANNEL_SUMMARY,CHANNEL_NUMBER,CHANNEL_THUMB))
        
        return LIVE_STREAMS_HD_MENU
    else:
        # Get not logged in alert
        ERROR_MESSAGE           = ErrorNotLoggedIn()
        
        return ERROR_MESSAGE
 
################################################################################
# Live streams SD menu
################################################################################   
# Set the route for the live streams hd menu
@route(PREFIX + "/sd-streams")

def LiveStreamsSD(title):
    # Test to see if user is logged in
    if "Login" in Dict:
        # Open an ObjectContainer for the live streams HD menu
        LIVE_STREAMS_SD_MENU    = ObjectContainer(
            title1              = title
        )
        
        # Gets the channel list
        CHANNEL_LIST            = GetChannelList()
        
        # Loop through each channel to produce an EpisodeObject
        for CHANNEL in CHANNEL_LIST:
            # Defines channel details from returned channel data
            CHANNEL_QUALITY     = "sd"
            CHANNEL_TITLE       = CHANNEL[0] + " " + CHANNEL_QUALITY.upper()
            CHANNEL_SUMMARY     = CHANNEL[1]
            CHANNEL_NUMBER      = CHANNEL[0].replace("Channel ","channel")
            CHANNEL_THUMB       = "icon-" + CHANNEL[0].replace("Channel ","channel-") + "-" + CHANNEL_QUALITY + ".png"
            
            # Gets channel episode object and adds to menu
            LIVE_STREAMS_SD_MENU.add(CreateChannelEpisodeObject(CHANNEL_QUALITY,CHANNEL_TITLE,CHANNEL_SUMMARY,CHANNEL_NUMBER,CHANNEL_THUMB))
        
        return LIVE_STREAMS_SD_MENU
    else:
        # Get not logged in alert
        ERROR_MESSAGE           = ErrorNotLoggedIn()
        
        return ERROR_MESSAGE
 
################################################################################
# Today's streams menu
################################################################################   
# Set the route for the live streams hd menu
# @route(PREFIX + "/todays-streams")
#
# def TodaysStreams(title):
#     # Test to see if user is logged in
#     if "Login" in Dict:
#         # Open an ObjectContainer for the live streams HD menu
#         TODAYS_STREAMS_MENU     = ObjectContainer(
#             title1              = title
#         )
#
#         return TODAYS_STREAMS_MENU
#     else:
#         # Get not logged in alert
#         ERROR_MESSAGE           = ErrorNotLoggedIn()
#
#         return ERROR_MESSAGE

################################################################################
# Live streams SD menu
################################################################################   
# Set the route for the live streams hd menu
# @route(PREFIX + "/upcoming-streams")
#
# def UpcomingStreams(title):
#     # Test to see if user is logged in
#     if "Login" in Dict:
#         # Open an ObjectContainer for the live streams HD menu
#         UPCOMING_STREAMS_MENU   = ObjectContainer(
#             title1              = title
#         )
#
#         return  UPCOMING_STREAMS_MENU
#     else:
#         # Get not logged in alert
#         ERROR_MESSAGE           = ErrorNotLoggedIn()
#
#         return ERROR_MESSAGE

################################################################################
# Gets a list of channels to iterate over
################################################################################
def GetChannelList():
    # make sure channel list is blank
    # CHANNEL_LIST                = []
    
    # Check to see if CHANNEL_LIST is already populated, if yes return it, if
    # no construct it.
    if CHANNEL_LIST:
        return CHANNEL_LIST
    else:    
        # Gets the HTML source from the Live Stream URL
        HTML_URL                    = URL_BASE + URL_LIVE
        HTML_SOURCE                 = HTML.ElementFromURL(HTML_URL, headers = CUSTOM_HEADERS)
    
        # Find the channel links in the HTML source with xpath
        CHANNELS                    = HTML_SOURCE.xpath("//a[@class='ch-link']")
    
        # Add each channel's text to CHANNEL_LIST
        for CHANNEL in CHANNELS:
            # Grab the link text, and convert from list to string
            # N.B. xpath ALWAYS returns a list
            CHANNEL_DETAILS         = "".join(CHANNEL.xpath(".//text()"))

            # Test for " – " in string
            if " - " in CHANNEL_DETAILS:
                # If present, populate CHANNEL_NAME and CHANNEL_DESCRIPTION
                CHANNEL_NAME        = CHANNEL_DETAILS.split(" - ",1)[0]
                CHANNEL_DESCRIPTION = CHANNEL_DETAILS.split(" - ",1)[1]
            else:
                # If not present, populate CHANNEL_DESCRIPTION with nothing
                CHANNEL_NAME        = CHANNEL_DETAILS
                CHANNEL_DESCRIPTION = "No Description is available for this channel"
        
            # Appends the channel details to the CHANNEL_LIST
            CHANNEL_LIST.append([CHANNEL_NAME,CHANNEL_DESCRIPTION])
    
        return CHANNEL_LIST

################################################################################
# Return EpisodeObject for channel
################################################################################
def CreateChannelEpisodeObject(QUALITY,TITLE,SUMMARY,NUMBER,THUMB,INCLUDE_CONTAINER=False):
    # Check the CHANNEL_QUALITY and set URL_CHANNEL, HEIGHT and WIDTH 
    # accordingly. N.B. URL wont work unless constructed here (rather than 
    # within the MediaObject)
    if "sd" in QUALITY:
        URL_CHANNEL     = NUMBER + "-" + QUALITY + URL_SUFFIX
        HEIGHT          = 360
        WIDTH           = 640
    else:
        URL_CHANNEL     = NUMBER + URL_SUFFIX
        HEIGHT          = 720
        WIDTH           = 1280
    
    # Builds a correctly formatted URL for each stream using a random IP number
    # from the CHANNEL_IPS array
    URL                 = "http://" + random.choice(CHANNEL_IPS) + "/hls/" + URL_CHANNEL
    
    # Creates a VideoClipObject, with the key being a callback, unsure why, but
    # this re-calling of the same function is necessary to get an object that
    # will play without a URL service.
    #
    # N.B. HTTPLiveStreamURL automatically sets video_codec, audio_codec and 
    # protocol. Adding them back in causes the stream not to work on other
    # devices that are not Chrome and PHT
    CHANNEL_OBJECT              = VideoClipObject(
        key                     = Callback(CreateChannelEpisodeObject,QUALITY=QUALITY,TITLE=TITLE,SUMMARY=SUMMARY,NUMBER=NUMBER,THUMB=THUMB,INCLUDE_CONTAINER=True),
        rating_key              = NUMBER,
        title                   = TITLE,
        summary                 = SUMMARY,
        thumb                   = R(THUMB),
        items                   = [
            MediaObject(
                video_resolution        = HEIGHT,
                audio_channels          = 2,
                optimized_for_streaming = True,
                height                  = HEIGHT,
                width                   = WIDTH,
                parts                   =   [
                    PartObject(
                        key             = HTTPLiveStreamURL(
                            url                     = URL   
                        )
                    )
                ]
            )
        ]
    )
    
    if INCLUDE_CONTAINER:
      return ObjectContainer(objects=[CHANNEL_OBJECT])
    else:
      return CHANNEL_OBJECT

################################################################################
# Authenticate the user
################################################################################        
def AuthenticateUser():
    # Create the login URL
    LOGIN_URL                   = URL_BASE + URL_LOGIN
    
    # Set the post data
    POST_DATA                   = {
        "username": Prefs["username"],
        "password": Prefs["password"]
    }
    
    # Grab the HTTP response to login attempt
    CONTENT                     = HTTP.Request(url = LOGIN_URL, values = POST_DATA).content
    
    if "OK" in CONTENT:
        # Sets Dict["Login"] to True on successful login attempt
        Dict["Login"]           = True
        
        return True
    else:
        # Sets Dict["Login"] to False on unsuccessful login attempt
        Dict["Login"]           = False
        
        return False

################################################################################
# Alerts and error messages
################################################################################ 
# If successful login
def SuccessLoggedIn():
    return ObjectContainer(
        header                  = "Success",
        message                 = "You're now logged in"
    )

# If user tries to access submenus without logging in
def ErrorNotLoggedIn():
    return ObjectContainer(
         header                 = "You're not logged in",
         message                = "You need to be logged in to view streams"       
    )
    
# If login error
def ErrorIncorrectLogin():
    return ObjectContainer(
        header                  = "Something went wrong",
        message                 = "Your username and/or password are incorrect"
    )

# If one or both of username or password are missing
def ErrorMissingLogin():
    return ObjectContainer(
        header                  = "Something's missing",
        message                 = "Your username and/or password is missing"
    )