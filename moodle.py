# -*- coding: utf-8 -*-
import os
import os.path
import re
import cookielib
import urllib2
import urllib
from bs4 import BeautifulSoup
from ConfigParser import ConfigParser

conf = ConfigParser()
project_dir = os.path.dirname(os.path.abspath(__file__))
conf.read(os.path.join(project_dir, 'config.ini'))

# Read config Settings - Do not change URLs if no necessary !
root_directory = conf.get("dirs", "root_dir")
shibboleth_username = conf.get("auth", "username")
shibboleth_password = conf.get("auth", "password")
moodle_url = conf.get("auth", "moodle_url")
shibboleth_url	= conf.get("auth", "shibboleth_url")

# Store the cookies and create an opener that will hold them
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

# Add our headers
opener.addheaders = [('User-agent', 'Mozilla\5.0')]

# Install our opener (note that this changes the global opener to the one
# we just made, but you can also just call opener.open() if you want)
urllib2.install_opener(opener)

# Input parameters we are going to send
payload = {
    'j_username': shibboleth_username,
    'j_password': shibboleth_password
}

# Use urllib to encode the payload
data = urllib.urlencode(payload)

print("Logging into " + moodle_url)

# Build our Request object (supplying 'data' makes it a POST)
req = urllib2.Request(moodle_url)

# Make the request and read the response
response = urllib2.urlopen(req)


# Logging into Shibboleth Server
request_shibboleth = urllib2.Request(shibboleth_url, data)
response_shibboleth = urllib2.urlopen(request_shibboleth)
contents_shibboleth = response_shibboleth.read()

# Parse received data
soup = BeautifulSoup(contents_shibboleth,"html.parser")
readaction = soup.find_all('form')
actionurl = readaction[0].get('action')
redditAll = soup.find_all("input")

# Get received values
RelayState = redditAll[0].get('value')
SAMLResponse = redditAll[1].get('value')

# Received Tokens
payload_token = {
	'RelayState':  RelayState,
	'SAMLResponse': SAMLResponse
}

# POST received token and open address
data_shibboleth = urllib.urlencode(payload_token)
request_shi_auth = urllib2.Request(actionurl, data_shibboleth)

# Receive logged in site
response_shi_auth = urllib2.urlopen(request_shi_auth)
contents_shi_auth = response_shi_auth.read()


# Verify the contents
if "KursÃ¼bersicht" not in contents_shi_auth:
    print "Cannot connect to moodle"
    exit(1)

print("Succesfully logged into Moodle Account")
	
# Filter received data
courses = contents_shi_auth.split('-header">KursÃ¼bersicht</h2>')[1].split('<aside id="block-region-side-pre" ')[0]

regex = re.compile('<h2 class="title">(.*?)</h2>')
course_list = regex.findall(courses)
courses = []


for course_string in course_list:
    soup = BeautifulSoup(course_string, "html.parser")
    a = soup.find('a')
    course_name = a.text.decode('utf-8')
    course_link = a.get('href')
    courses.append([course_name, course_link])

for course in courses:
	if "/" in course[0]:
		course[0] = course[0].replace('/','-')
	
	if not os.path.isdir(root_directory + course[0]):
		os.mkdir(root_directory+course[0])
            
	response_course = urllib2.urlopen(course[1])
	scrap = response_course.read()
	
	# parsing for active links
	soup = BeautifulSoup(scrap, "html.parser")
	course_links = soup.findAll("li", class_="activity resource modtype_resource ")

	course_new_links = []
	for activelinks in course_links:
		activelink_list = activelinks.find('a')
		if (activelink_list):
			course_new_links.append(activelink_list)

	for link in course_new_links:
		current_dir = root_directory + course[0] + "/"
		href = link.get('href')

	# Checking only resources... Ignoring forum and folders, etc
		if "resource" in href:
			webFile = urllib2.urlopen(href)
			
		# Checking if url needs to be opened in an additional window
		if webFile.geturl().split('/')[-1].split('?')[0] == 'view.php':
			request_website = urllib2.Request(href)
			response_website = urllib2.urlopen(request_website).read()
			
			# extracting important data
			response_website_par = response_website.split('<div class="resourceworkaround">')[1]
			soup_website = BeautifulSoup(response_website_par, "html.parser")
			link_website = soup_website.find('a')
			webFile = urllib2.urlopen(link_website.get('href'))
			file_name = current_dir + link_website.text
		
		else:
			url = webFile.geturl().split('/')[-1].split('?')[0]
			file_name = current_dir + urllib.unquote(url).decode('utf-8')
			
		if os.path.isfile(file_name):
			print "File found : ", file_name
			continue	
		print"Creating file :" ,file_name
		pdfFile = open(file_name, 'wb')
		pdfFile.write(webFile.read())
		webFile.close()
		pdfFile.close()
print("Update Complete")
