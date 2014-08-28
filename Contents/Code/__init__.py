################################################################################
# Python Imports
################################################################################
# This is only needed for picking a randomised IP address from CHANNEL_IPS array
import random

# This is only needed for removing the new line character (\n) in upcoming event
# data (title and competition)
import re

################################################################################
# Global variables for channel
################################################################################
TITLE                           = "HD Streaming"
PREFIX                          = "/video/hdstreaming"

ART                             = "art-default.png"
ICON                            = "icon-default.png"

# Below values lifted from FilmOn plugin
USER_AGENT                      = "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"

# Using a referrer as the domain for login is different to the channel domain
REFERER                         = "http://news-source.tv/"

# URLs for hd-streaming site
URL_BASE                        = "http://hd-streaming.tv/"
URL_LOGIN                       = "api/?request=login"
URL_LIVE                        = "watch/livehds"
URL_UPCOMING                    = "watch/upcoming-matches"

# File name parts for video URLs
#
# N.B. Suffix includes file extension .m3u8
VIDEO_PREFIX                    = "http://"
VIDEO_DIRECTORY                 = "/hls/"
VIDEO_SUFFIX                    = ".m3u8?s=6hfu0"

# IP addresses used by channel video URLs
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
                                    
CHANNEL_PREFIX                  = "vdn.hd-streaming.tv"
                                    
# Global variable used to store channel list
CHANNEL_LIST                    = []

# Global variable used to store upcoming data
UPCOMING_EVENTS_LIST            = []

# THIS IS USED ONLY FOR LOGGING
# STARS                           = "**********"

################################################################################
# Initialise the channel
################################################################################
def Start():
    # Set title and art
    ObjectContainer.title1      = TITLE
    ObjectContainer.art         = R(ART)

    # Delete the dictionary that contains the login status
    ClearLoginStatus()
    
    # Set header for all HTTP requests
    HTTP.Headers["User-agent"]  = USER_AGENT
    HTTP.Headers["Referer"]     = REFERER

################################################################################
# Clear the login status
################################################################################
def ClearLoginStatus():
    if "Login" in Dict:
        del Dict["Login"]

    return None
    
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
    
# If there are no upcoming events
def AlertNoEvents():
    return ObjectContainer(
        header                  = "No upcoming events",
        message                 = "There are currently no upcoming events"
    )

################################################################################
# Validate users preferences (username and password)
################################################################################
def ValidatePrefs():
    # Tests for username and password
    if Prefs["username"] and Prefs["password"]:
        # If both are present, authenticate the user
        AUTHENTICATE            = AuthenticateUser()
        
        # Shows message based on authentication attempt
        if AUTHENTICATE is True:
            # Successful login
            ALERT               = SuccessLoggedIn()
            
        else:
            # Incorrect username or password error
            ALERT               = ErrorIncorrectLogin()
    
    else:
        # Missing username or password
        ALERT                   = ErrorMissingLogin()
        
    return ALERT

################################################################################
#  Authenticate the user
################################################################################
def AuthenticateUser():
    # Construct login URL
    LOGIN_URL                   = URL_BASE + URL_LOGIN
    
    # Set the POST data to users login details
    POST_DATA                   = {
        "username": Prefs["username"],
        "password": Prefs["password"]
    }
    
    # Grab the HTTP response to login attempt
    LOGIN_RESPONSE_CONTENT      = HTTP.Request(url = LOGIN_URL, values = POST_DATA).content
    
    # Tests to see if we've successfully logged in
    if "OK" in LOGIN_RESPONSE_CONTENT:
        # If "OK" is found within the response set Dict["Login"] to True
        Dict["Login"]           = True
        
        # Save the dictionary immediately
        Dict.Save()
        
        return True
        
    else:
        # If we dont' find "OK" or the response returns null, we return false
        return False
        
################################################################################
# Gets a list of channels to iterate over
################################################################################
def GetChannelList():
    # Check to see if CHANNEL_LIST is already populated, if True return it, if
    # not construct it.
    if CHANNEL_LIST:
        return CHANNEL_LIST
    else:
        # Gets the HTML source from the Live Stream URL
        CHANNEL_LIST_URL        = URL_BASE + URL_LIVE
        CHANNEL_LIST_SOURCE     = HTML.ElementFromURL(CHANNEL_LIST_URL)
        
        # Find the channel links in the HTML source with xPath
        CHANNELS                = CHANNEL_LIST_SOURCE.xpath("//a[@class='ch-link']")
        
        # Add each channel to CHANNEL_LIST
        for CHANNEL in CHANNELS:
            # Grab the link text, and convert from list to string
            #
            # N.B. xpath ALWAYS returns a list
            CHANNEL_DETAILS         = "".join(CHANNEL.xpath(".//text()"))
            
            # Test for " - " in string
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
# Gets a list of upcoming events to iterate over
################################################################################
def GetUpcomingEventsList():
    # Check to see if UPCOMING_EVENTS_LIST is already populated, if True return
    # it, if not construct it.
    if UPCOMING_EVENTS_LIST:
        return UPCOMING_EVENTS_LIST
    else:
        # Gets the HTML source from the Upcoming events URL
        UPCOMING_EVENTS_URL         = URL_BASE + URL_UPCOMING
        UPCOMING_EVENTS_SOURCE      = HTML.ElementFromURL(UPCOMING_EVENTS_URL)
        
        # Find the dates and events in the HTML source with xPath
        UPCOMING_EVENTS_DAYS        = UPCOMING_EVENTS_SOURCE.xpath("//div[@class='view-grouping']")          
        
        # If there are upcoming events loop through each day to produce events
        # list. If not, return a simple array to be used as an alert message
        if len(UPCOMING_EVENTS_DAYS) > 0:
            # Loops through each day to extract date and events
            for UPCOMING_DAY in UPCOMING_EVENTS_DAYS:                
                # Extract date and list of events for this date
                UPCOMING_DATE           = "".join(UPCOMING_DAY.xpath("./div[@class='view-grouping-header']/text()"))
                UPCOMING_EVENTS_SOURCE  = UPCOMING_DAY.xpath(".//div[@class='view-grouping-content']//tbody/tr")
                UPCOMING_EVENTS         = UpcomingEventsForDay(UPCOMING_EVENTS_SOURCE,UPCOMING_DATE)
            
                # Loops through each event and appends it to the 
                # UPCOMING_EVENTS_LIST.
                #
                # N.B. Yes, I know this is probably bad code nesting a for loop
                # within a for loop.
                for EVENT in UPCOMING_EVENTS:
                    UPCOMING_EVENTS_LIST.append(EVENT)
        
            return UPCOMING_EVENTS_LIST
        else:          
            
            return False 
               
################################################################################
# Extract information from list of <tr>s (UPCOMING_EVENTS)
################################################################################
def UpcomingEventsForDay(UPCOMING_EVENTS_SOURCE,UPCOMING_DATE):
    # Open a blank array to house the upcoming days event list
    UPCOMING_EVENTS         = []
    
    # Loop over each event and get details
    for EVENT_SOURCE in UPCOMING_EVENTS_SOURCE:
        
        
        # Grabs the channel/time and sets the date      
        EVENT_CHANNEL       = "".join(EVENT_SOURCE.xpath("./td[contains(@class,'views-field-field-eum-channel')]/a/text()"))
        EVENT_CHANNEL       = EVENT_CHANNEL.replace("CH","Channel ")
        EVENT_TIME          = "".join(EVENT_SOURCE.xpath("./td[contains(@class,'views-field-field-eum-datetime-1')]/span/text()"))
        EVENT_DATE          = UPCOMING_DATE
        
        # For the title and competition we need to get rid of the new line character (\n) and extra spacing
        EVENT_TITLE         = "".join(EVENT_SOURCE.xpath("./td[contains(@class,'views-field-field-eum-title')]/text()"))
        EVENT_TITLE         = re.sub("\n","",EVENT_TITLE.strip())
        EVENT_COMPETITION   = "".join(EVENT_SOURCE.xpath("./td[contains(@class,'views-field-field-eum-league')]/text()"))
        EVENT_COMPETITION   = re.sub("\n","",EVENT_COMPETITION.strip())
        
        # Sets the event icon
        EVENT_THUMB         = "icon-" + EVENT_CHANNEL.replace("Channel ","channel-") + "-hd.png"
        
        # Append the event details to the upcoming event list
        UPCOMING_EVENTS.append([EVENT_CHANNEL,EVENT_TIME,EVENT_DATE,EVENT_TITLE,EVENT_COMPETITION,EVENT_THUMB])
        
    return UPCOMING_EVENTS       

################################################################################
# Defines the channel details
################################################################################
def DefineChannelDetails(CHANNEL,QUALITY):
    # Defines channel details from returned channel data
    CHANNEL_QUALITY     = QUALITY
    CHANNEL_TITLE       = CHANNEL[0] + " " + CHANNEL_QUALITY.upper()
    CHANNEL_SUMMARY     = CHANNEL[1]
    CHANNEL_NUMBER      = CHANNEL[0].replace("Channel ","channel")
    CHANNEL_THUMB       = "icon-" + CHANNEL[0].replace("Channel ","channel-") + "-" + CHANNEL_QUALITY + ".png"
    
    # Build an array containing the above
    CHANNEL_DETAILS     = [CHANNEL_QUALITY,
                            CHANNEL_TITLE,
                            CHANNEL_SUMMARY,
                            CHANNEL_NUMBER,
                            CHANNEL_THUMB]
    
    return CHANNEL_DETAILS

################################################################################
# Return EpisodeObject for channel
################################################################################
def CreateChannelEpisodeObject(QUALITY,TITLE,SUMMARY,NUMBER,THUMB,INCLUDE_CONTAINER=False):
    # Check the CHANNEL_QUALITY and set URL_CHANNEL, HEIGHT and WIDTH 
    # accordingly. N.B. URL wont work unless constructed here (rather than 
    # within the MediaObject)
    if "sd" in QUALITY:
        VIDEO_FILE      = NUMBER + "-" + QUALITY + VIDEO_SUFFIX
        HEIGHT          = 360
        WIDTH           = 640
    else:
        VIDEO_FILE      = NUMBER + VIDEO_SUFFIX
        HEIGHT          = 720
        WIDTH           = 1280
    
    # Builds a correctly formatted URL for each stream using a random IP number
    # from the CHANNEL_IPS array
    # VIDEO_URL           = VIDEO_PREFIX + random.choice(CHANNEL_IPS) + VIDEO_DIRECTORY + VIDEO_FILE
    VIDEO_URL           = VIDEO_PREFIX + CHANNEL_PREFIX + VIDEO_DIRECTORY + VIDEO_FILE
    
    # Creates a VideoClipObject, with the key being a callback, unsure why, but
    # this re-calling of the same function is necessary to get an object that
    # will play without a URL service.
    #
    # N.B. HTTPLiveStreamURL automatically sets video_codec, audio_codec and 
    # protocol. Adding them back in causes the stream not to work on other
    # devices that are not Chrome and PHT
    CHANNEL_OBJECT              = VideoClipObject(
        key                     = Callback(
            CreateChannelEpisodeObject,
            QUALITY             = QUALITY,
            TITLE               = TITLE,
            SUMMARY             = SUMMARY,
            NUMBER              = NUMBER,
            THUMB               = THUMB,
            INCLUDE_CONTAINER   = True
        ),
        rating_key              = NUMBER + QUALITY,
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
                            url         = VIDEO_URL   
                        )
                    )
                ]
            )
        ]
    )
    
    if INCLUDE_CONTAINER:
        return ObjectContainer(
            objects               = [CHANNEL_OBJECT]
        )
    else:
        return CHANNEL_OBJECT

################################################################################
# Build the main menu
################################################################################ 
@handler(PREFIX, TITLE, thumb = ICON, art = ART)

def MainMenu():
    # Check to see if the user is logged in or not, if they are build the main
    # menu options, if not try to authenticate or show an error
    if "Login" in Dict:
        # Open an ObjectContainer for the main menu
        MAIN_MENU               = ObjectContainer()        
        
        # Add the HD streams object
        MAIN_MENU.add(
            DirectoryObject(
                title           = "HD Streams",
                thumb           = R("icon-live-streams-hd.png"),
                summary         = "High definition streams",
                key             = Callback(
                    HDStreams,
                    TITLE       = "HD Streams"
                )
            )
        )
        
        # Add the SD streams object
        MAIN_MENU.add(
            DirectoryObject(
                title           = "SD Streams",
                thumb           = R("icon-live-streams-sd.png"),
                summary         = "Standard definition streams",
                key             = Callback(
                    SDStreams,
                    TITLE       = "SD Streams"
                )
            )
        )
        
        # Add the Upcoming streams object
        MAIN_MENU.add(
            DirectoryObject(
                title           = "Upcoming Streams",
                thumb           = R("icon-upcoming-streams.png"),
                summary         = "Streams for the next week",
                key             = Callback(
                    UpcomingStreams,
                    TITLE       = "Upcoming Streams"
                )
            )
        )
        
        # Add the preferences object
        MAIN_MENU.add(
            PrefsObject(
                title           = "Preferences",
                thumb           = R("icon-preferences.png"),
                summary         = "Enter your username and password\r\nThe plugin will not work without them"
            )
        )
        
        return MAIN_MENU
        
    else:
        # Log the user in initially
        AUTHENTICATE            = AuthenticateUser()
        
        if AUTHENTICATE is True:
            # Return the main menu
            MENU                = MainMenu()
            
            return MENU
        else:
            # Incorrect username or password error
            ERROR_MESSAGE       = ErrorIncorrectLogin()
            
            return ERROR_MESSAGE

################################################################################
# HD Streams menu
################################################################################   
# Set the route for the live streams HD menu
@route(PREFIX + "/hd-streams")

def HDStreams(TITLE):
    # Open an ObjectContainer for the live streams HD menu
    HD_STREAMS_MENU         = ObjectContainer(
        title1              = TITLE
    )

    # Gets the channel list
    CHANNEL_LIST            = GetChannelList()
    
    # Loop through each channel to produce an EpisodeObject
    for CHANNEL in CHANNEL_LIST:
        # Get this channels details
        CHANNEL_DETAILS     = DefineChannelDetails(CHANNEL,"hd")
        
        # Creates an EpisodeObject and adds it to the HD Streams menu
        HD_STREAMS_MENU.add(
            CreateChannelEpisodeObject(
                QUALITY     = CHANNEL_DETAILS[0],
                TITLE       = CHANNEL_DETAILS[1],
                SUMMARY     = CHANNEL_DETAILS[2],
                NUMBER      = CHANNEL_DETAILS[3],
                THUMB       = CHANNEL_DETAILS[4]
            )
        )
        
    return HD_STREAMS_MENU
    
################################################################################
# SD Streams menu
################################################################################   
# Set the route for the live streams SD menu
@route(PREFIX + "/sd-streams")

def SDStreams(TITLE):
    # Open an ObjectContainer for the live streams SD menu
    SD_STREAMS_MENU         = ObjectContainer(
        title1              = TITLE
    )

    # Gets the channel list
    CHANNEL_LIST            = GetChannelList()
    
    # Loop through each channel to produce an Episode object
    for CHANNEL in CHANNEL_LIST:
        # Get this channels details
        CHANNEL_DETAILS     = DefineChannelDetails(CHANNEL,"sd")
        
        # Creates an EpisodeObject and adds it to the HD Streams menu
        SD_STREAMS_MENU.add(
            CreateChannelEpisodeObject(
                QUALITY     = CHANNEL_DETAILS[0],
                TITLE       = CHANNEL_DETAILS[1],
                SUMMARY     = CHANNEL_DETAILS[2],
                NUMBER      = CHANNEL_DETAILS[3],
                THUMB       = CHANNEL_DETAILS[4]
            )
        )
        
    return SD_STREAMS_MENU

################################################################################
# Upcoming streams menu
################################################################################ 
# Set the route for Upcoming streams menu
@route(PREFIX + "/upcoming-streams")

def UpcomingStreams(TITLE):
    # Open an ObjectContainer for Upcoming streams menu
    UPCOMING_STREAMS_MENU   = ObjectContainer(
        title1              = TITLE
    )
    
    # Gets the upcoming event list
    UPCOMING_EVENTS_LIST = GetUpcomingEventsList()

    # If UPCOMING_EVENTS_BY_DATE returns false, display an alert message, otherwise
    # build the menu
    if UPCOMING_EVENTS_LIST is False:
        ALERT               = AlertNoEvents()
        
        return ALERT
    
    else:
        # Loop through all the upcoming dates and return all events       
        for UPCOMING_EVENT in UPCOMING_EVENTS_LIST:
            # Correct channel name so we can display it propely and display
            # correct icon
            CHANNEL                 = UPCOMING_EVENT[0].replace("CH","Channel ")
            
            # Creates a DirectoryObject and add it to the Upcoming streams menu
            UPCOMING_STREAMS_MENU.add(
                DirectoryObject(
                    title           = UPCOMING_EVENT[3] + ", " + UPCOMING_EVENT[2],
                    thumb           = R(UPCOMING_EVENT[5]),
                    summary         = CHANNEL + ", " + UPCOMING_EVENT[1] + ", " + UPCOMING_EVENT[4],
                    key             = Callback(
                        UpcomingEventStreams,
                        TITLE       = UPCOMING_EVENT[3],
                        DATE        = UPCOMING_EVENT[2],
                        TIME        = UPCOMING_EVENT[1],
                        CHANNEL     = UPCOMING_EVENT[0],
                        COMPETITION = UPCOMING_EVENT[4],
                        THUMB       = UPCOMING_EVENT[5]
                    )
                )
            )
            
        return UPCOMING_STREAMS_MENU  
        
################################################################################
# Upcoming event streams menu
################################################################################ 
# Set the route for Upcoming eventstreams menu
@route(PREFIX + "/upcoming-event-streams")

def UpcomingEventStreams(TITLE,DATE,TIME,CHANNEL,COMPETITION,THUMB):
    # Open an ObjectContainer for Upcoming event streams menu
    UPCOMING_EVENT_STREAMS_MENU = ObjectContainer(
        title1                  = TITLE
    )
    
    # Adds VideoObjects for the HD stream of this event
    UPCOMING_EVENT_STREAMS_MENU.add(
       CreateChannelEpisodeObject(
            QUALITY     = "hd",
            TITLE       = TITLE + ", HD Stream",
            SUMMARY     = COMPETITION + " fixture taking place on " + DATE + " at " + TIME,
            NUMBER      = CHANNEL,
            THUMB       = THUMB
       )
    )
    
    # Adds VideoObjects for the SD stream of this event
    UPCOMING_EVENT_STREAMS_MENU.add(
       CreateChannelEpisodeObject(
            QUALITY     = "sd",
            TITLE       = TITLE + ", SD Stream",
            SUMMARY     = COMPETITION + " fixture taking place on " + DATE + " at " + TIME,
            NUMBER      = CHANNEL,
            THUMB       = THUMB.replace("-hd.","-sd.")
       )
    )
    
    return UPCOMING_EVENT_STREAMS_MENU