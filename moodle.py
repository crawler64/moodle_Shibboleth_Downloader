# encoding=utf8  
import sys, getopt

reload(sys)  
sys.setdefaultencoding('utf8')

import mechanize
import re
import ssl
import os
import os.path
from ConfigParser import ConfigParser

# moodle.py -d 1/True turns Debug mode on. 
# You can turn this on, to turn on the "file found:" comment, just to check


def main(argv):
   Debug = False
   try:
      opts, args = getopt.getopt(argv,"d:",["dbgpara="])
	
   except getopt.GetoptError:
		Debug = False
		return Debug
	
   for opt, arg in opts:
	if opt in ("-d","--dbgpara"):
		if (arg == 'True') or (arg == '1'):
			Debug = True
	return Debug


if __name__ == "__main__":
   Debug = main(sys.argv[1:])


conf = ConfigParser()
project_dir = os.path.dirname(os.path.abspath(__file__))
conf.read(os.path.join(project_dir, 'config.ini'))

# Read config Settings - Do not change URLs if no necessary !
root_directory = conf.get("dirs", "root_dir")
shibboleth_username = conf.get("auth", "username")
shibboleth_password = conf.get("auth", "password")
moodle_url = conf.get("auth", "moodle_url")


# Logging into Moodle
br = mechanize.Browser()

br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17')]
ssl._create_default_https_context = ssl._create_unverified_context

response_Startpage = br.open(moodle_url)
response_Authpage = br.follow_link(text='Login')

selection_form = br.select_form(nr=0)
br["j_username"] = shibboleth_username
br["j_password"] = shibboleth_password
response_loginpage = br.submit()
response_nextpage = br.select_form(nr=0)
response_finalpage = br.submit()

# now i'm logged in

for links_mainpage in br.links(url_regex="moodle.hm.edu/course/view.php?"):
	#Filter Coursenames
	links_mainpage.text = links_mainpage.text.replace("/","-")
	
	print links_mainpage.text
	if not os.path.isdir(root_directory + "/" + links_mainpage.text):
		try:
			os.mkdir(root_directory + "/" + links_mainpage.text)
			
		except WindowsError:
			print ('ERROR: Directory Error ' + file_info)
			br.back()
			continue
	response = br.follow_link(links_mainpage)
	for links_subpage in br.links(url_regex="mod/resource"):
		
		try:
			response_file = br.follow_link(links_subpage)
			file_info = response_file.info()['Content-Disposition'].split('filename=')[-1].replace('"','').replace(';','')
			filename = root_directory + "/" + links_mainpage.text + "/" + file_info
			br.back()
			if os.path.isfile(filename):
				if(Debug):
					print "File found : ", file_info
				continue	
			print("Getting " + file_info)
			br.retrieve(links_subpage.url,filename)[0]

		except IOError:
			print('ERROR: cannot open file ' + links_subpage.text)
		except KeyError:
		# handle popup relinking
			response_file_redirection = br.follow_link(links_subpage)
			for links_popup in br.links(url_regex="mod_resource"):
				try:
					response_file_popup = br.follow_link(links_popup)
					filename_info = response_file_popup.info()['Content-Disposition'].split('filename=')[-1].replace('"','').replace(';','')
					filename_pop =  root_directory + "/" + links_mainpage.text + "/" + filename_info
					br.back()
					if os.path.isfile(filename_pop):
						if(Debug):
							print "File found : ", filename_info
						continue
					print("Getting " + filename_info)
					br.retrieve(links_popup.url,filename_pop)[0]
				except IOError:
					print('ERROR: cannot open file ' + links_subpage.text)
		except UnicodeDecodeError:
			print ('ERROR: Unicode Decode Error at ' + file_info)
			br.back()
	br.back()

print(" Download Complete from Moodle ")
