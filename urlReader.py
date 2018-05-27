# -*- coding: utf-8 -*-
import re
import HTMLParser
from bs4 import BeautifulSoup
import urllib
import sys
import os
import pycurl


c = pycurl.Curl()

showList = ["Hannibal", "Game of Thrones", "Peaky Blinders"]

def languageFilter(lang):
	return "spa" in lang and not "atino" in lang

def cd(dir):
	os.chdir(dir)

def mkdir(show_name):
	if not os.path.exists(show_name):
		os.makedirs(show_name)

def filterName(name):
	name = name.encode(sys.stdout.encoding, errors='replace')
	name = name.replace(":",".")
	name = name.replace("\\",".")
	name = name.replace("*","·")
	name = name.replace("\"","'")
	name = name.replace("/",".")
	name = name.replace(">",".")
	name = name.replace("<",".")
	name = name.replace("|",".")
	name = name.replace("?","")
	name = name.lstrip()
	name = name.rstrip()
	return name

def getShows(html):
	soup = BeautifulSoup(html, 'html.parser',from_encoding="utf-8")
	return soup.find_all(class_="line0")

def getHTML(site):
	return urllib.urlopen('https://www.tusubtitulo.com/'+site).read()

def getSubtitle(episode_name, subtitle_url):
	c.setopt(c.URL, subtitle_url)
	c.setopt(c.HTTPHEADER, ['Accept-Encoding: gzip, deflate, sdch',
							'Accept-Language: es-ES,es;q=0.8',
							'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
							'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
							'Referer: http://www.tusubtitulo.com/'])
	file_name = episode_name+'.srt'
	n=2
	while(os.path.isfile(file_name)):
		file_name = episode_name+ " (" + str(n) +').srt'
		n=n+1
	f = open(file_name, 'w')
	c.setopt(c.WRITEDATA, f)
	c.perform()
	
def getSeasons(show_id,season):

	season_html = getHTML('ajax_loadShow.php?show='+str(show_id)+'&season='+str(season))
	soup = BeautifulSoup(season_html, 'html.parser',from_encoding="utf-8")
	episode_list = soup.find_all("table")
	if len(episode_list)<1:
		#print "error on season: " + str(season)
		pass
	else:
		mkdir("Temporada "+str(season))
		cd("Temporada "+str(season))
		for episode in episode_list:
			elements = episode.find_all('tr')
			episode_title = elements[0].find_all('td')
			episode_name = filterName(episode_title[2].text)
			episode_name = episode_name.split("\n")[1]
			
			
			#getSubtitles
			for unit in elements[1:]:
				lang = unit.find_all(class_="language")
				url = unit.find_all('a')
				if len(lang)>0 and len(url)>0:
					episode_language = lang[0].text
					episode_url = url[0].get('href')
					if languageFilter(episode_language):
						getSubtitle(episode_name,str(episode_url))
		cd("..")
		getSeasons(show_id,season+1)
		
		
	
def getShow(show_url):
	#show_html = getHTML(show_url)
	show_id = re.search(r'show/(?P<id>\w+)', show_url)
	show_id = show_id.group('id')
	getSeasons(show_id,1)
		
		
def main():
	woher = getHTML('series.php')
	shows = getShows(woher)
	for show in shows:
		show_name = filterName(show.string)
		
		if not show_name in showList:
			continue
		
		show_url = show.a.get('href')
		mkdir(show_name)
		cd(show_name)
		getShow(show_url)
		cd("..")

main()

