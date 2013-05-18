import xbmcplugin, xbmcgui, xbmcaddon
import sys
import urllib
import brightcovePlayer

from brightcove.api import Brightcove

addon = xbmcaddon.Addon(id='plugin.video.geode')

thisPlugin = int(sys.argv[1])
baseLink = "http://www.geo.de/"

token = "CNnmbZ-jMglpvUShxdYM16UleH57pO_wyHnfYYhQRns."

const = "b3f62157d9cc6d851582f14e85c406fb3afbe32b"
playerKey = "AQ~~,AAAAAFI1EN8~,BmfQKhANWKOs7JJ08MqKSzutSgN-PmSr"
publisherID = "1379209439"
playerID = "52515973001"

pageSize = 12

brightcove = Brightcove(token)

def mainPage():
	showPage(0)

def showPage(pageNumber):
	page = brightcove.find_all_playlists(page_size=pageSize, get_item_count=True, page_number=pageNumber)
	
	for playlist in page.items:
		pic = unicode(playlist.thumbnailURL)
		addDirectoryItem(playlist.name,{"action":"showPlaylist","playlistId":playlist.id},pic)
		
	if page.total_count > pageSize*(pageNumber+1):
		addDirectoryItem("Mehr anzeigen",{"action":"showPage","pageNumber":pageNumber+1},"")
		
	xbmcplugin.endOfDirectory(thisPlugin)

def showPlaylist(playlistId):
	page = brightcove.find_playlist_by_id(playlist_id=playlistId)
	
	for video in page.videos:
		print video.length
		addDirectoryItem(video.name,{"action":"playVideo","videoId":video.id},video.thumbnailURL,False,duration=str(video.length/1000/60),plot=video.longDescription)
	xbmcplugin.endOfDirectory(thisPlugin)
		

def playVideo(videoPlayer):
	stream = brightcovePlayer.play(const, playerID, videoPlayer, publisherID, playerKey)
	
	if stream[1][0:5] == "http:":
		finalurl = stream[1]
	else:
		rtmpbase = stream[1][0:stream[1].find("&")]
		rtmpbase = rtmpbase + stream[1][stream[1].find("?"):]
		playpath = stream[1][stream[1].find("&") + 1:]
		finalurl = rtmpbase + ' playpath=' + playpath
	
	item = xbmcgui.ListItem(path=finalurl)
	xbmcplugin.setResolvedUrl(thisPlugin, True, item)

def addDirectoryItem(name, parameters={}, pic="", folder=True, duration=None, plot=None, date=None, size=None, year=None):
    if not folder:
        li = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=pic)
        li.setProperty('IsPlayable', 'true')
        li.setInfo("video",{
            "size": size,
            "date": date,
            "year": year,
            "title": name,
            "plot": plot,
            "duration": duration
          }); 
    else:
        li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=pic)
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    
    return param
	
if not sys.argv[2]:
    mainPage()
else:
    params = get_params()
    if params['action'] == "showPage":
        showPage(int(params['pageNumber']))
    elif params['action'] == "showPlaylist":
        showPlaylist(int(params['playlistId']))
    elif params['action'] == "playVideo":
        playVideo(params['videoId'])
    elif params['action'] == "search":
        searchVideo()
    else:
        mainPage()