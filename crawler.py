#/usr/sbin/python2
import sys
import re
import urllib2
import html5lib
from html5lib import treebuilders, treewalkers, serializer
from html5lib.filters import sanitizer
from lepl.apps.rfc3696 import HttpUrl
from urlparse import urlparse

urllist=[]
Valid_Url = HttpUrl()

def access(url):
	try:
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
	except urllib2.HTTPError as e:
		print 'Error: De server kan de aanvraag niet verwerken'
		print e.code
		print '------------'
		return 0
	except urllib2.URLError as e:
		print 'Error: De server kan niet bereikt worden'
		print e
		print '------------'
		return 0
	except:
		print 'de url is hoogstwaarschijnlijk fout'
		print '------------'
		return 0
	return response.read()

def parsehtml(pagestring,Parsed_Url):
	parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
	dom_tree = parser.parse(pagestring)
	walker = treewalkers.getTreeWalker("dom")
	stream = walker(dom_tree)
#-----------
	rtrnlist = []
	titleNode = False
	title = u''
	for token in stream:
		#Link en Titel detectiecode
		try:
			if token['type'] == 'StartTag' and token['name'] == 'title':
				titleNode = True
			elif titleNode:
				if token['type'] == 'EndTag' and token['name'] == 'title':
					titleNode = False
				elif token.has_key('data'):
					title += token['data']
					print 'Titel: ' + title.strip() + '\n'
			elif token['type'] == 'StartTag' and token['data'][0][0] == u'href':
				link = token['data'][0][1]
				if link[:4] != 'http' and (link[0] != '/' and link[0] != '\\'):
					link = '/' + link
				if link in urllist:
					print 'link al reeds in memory: ' + link
				elif Valid_Url(link):
					print 'added:' + link
					rtrnlist.append(token['data'][0][1])
				elif Valid_Url(Parsed_Url.scheme + '://' + Parsed_Url.netloc + link):
					if Parsed_Url.scheme + '://' + Parsed_Url.netloc + link in urllist:
						print 'link al reeds in memory: ' + Parsed_Url.scheme + '://' + Parsed_Url.netloc + link
					else:
						print 'added parsed: ' + Parsed_Url.scheme + '://' + Parsed_Url.netloc + link
					rtrnlist.append(Parsed_Url.scheme + '://' + Parsed_Url.netloc + link)
				else:
					print 'Not a valid URL: ' + link
		except:
			"donothing"
	print '------------'
	return rtrnlist

def crawl(url):
	print 'url: ' + url + '\n'
	pagestring = access(url)
	if pagestring == 0:
		return []
	return parsehtml(pagestring,urlparse(url))

def main():
	args = sys.argv[1:]
	if not args:
		print 'usage: [file]'
		sys.exit(1)
	urllist.append(args[0])
	for url in urllist:
		urllist.extend(crawl(url))
	print '-------\n\nFinished'

main()
