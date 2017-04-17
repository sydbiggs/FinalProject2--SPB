## Import statements
import unittest
import json
import requests
import tweepy
from bs4 import BeautifulSoup
import re
import twitter_info


#Twitter info:
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())


# Write function(s) to get and cache data from Twitter:

CACHE_FNAME = "206project3_cache.json"
try: 
	cache_file = open(CACHE_FNAME, 'r')
	cache_contents = cache_file.read() # pull all into one big string
	CACHE_DICTION = json.loads(cache_contents) # dictionary that holds all cache data  
	cache_file.close()
except:
	CACHE_DICTION = {}

# A function to get and cache data based on a search term
def get_tweets_from_term(searchterm):
	unique_identifier = searchterm
	if unique_identifier in CACHE_DICTION:
		print("Using cached data for ", searchterm, "\n")
		twitter_results = CACHE_DICTION[unique_identifier]
	else:
		print("Getting data from internet for ", searchterm, "\n")
		twitter_results = api.search(q = searchterm)
		CACHE_DICTION[unique_identifier] = twitter_results
		f = open(CACHE_FNAME, "w")
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return(twitter_results)

# A function to get and cache data about a Twitter user

def get_tweets_from_user(twitter_handle):
	unique_identifier = twitter_handle
	if unique_identifier in CACHE_DICTION:
		print("Using cached data for ", twitter_handle, "\n")
		twitter_results = CACHE_DICTION[unique_identifier]
	else:
		print("Getting data from internet for ", twitter_handle, "\n")
		# twitter_results = api.user_timeline(screen_name = twitter_handle)
		twitter_results = api.get_user(screen_name = twitter_handle)
		CACHE_DICTION[unique_identifier] = twitter_results
		f = open(CACHE_FNAME, "w")
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return(twitter_results)

# Write function(s) to get and cache data from the OMDB API with a movie title search 
def get_movie_data(movie_title):
	unique_identifier = movie_title
	if unique_identifier in CACHE_DICTION:
		print("Using cached data for ", movie_title, "\n")
		results = CACHE_DICTION[unique_identifier]
	else:
		baseurl = "http://www.omdbapi.com/"
		ombd_param = {}
		ombd_param["t"] = movie_title
		ombd_param["type"] = "movie"
		print("Getting data from internet for ", movie_title ,"\n")
		response = requests.get(baseurl, ombd_param)
		results = json.loads(response.text)
		CACHE_DICTION[unique_identifier] = results
		f = open(CACHE_FNAME, "w")
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return(results)

# Class Movie
# Its title
# Its director
# Its IMDB rating
# A list of its actors (check out the data and consider how to get a list of strings that represent actor names!)
# The number of languages in the movie
class Movie():
	def __init__(self, movie_response): #where movie_response = dictionary with info about a movie
		self.title = movie_response["Title"]
		self.director = movie_response["Director"]
		self.production = movie_response["Production"]
		self.released = movie_response["Released"]
		self.languages = movie_response["Language"]
		self.runtime = movie_response["Runtime"]
		self.actors = movie_response["Actors"]
		self.plot = movie_response["Plot"]
		self.genre = movie_response["Genre"]
		self.website = movie_response["Website"]
		self.ratings = {}
		for avalue in movie_response["Ratings"]:
			source = avalue["Source"]
			value = avalue["Value"]
			self.ratings[source] = value
		self.boxoffice = movie_response["BoxOffice"]

	def __str__(self):
		return("{}".format(self.title))

	# Need another method here!

test = get_movie_data("V for Vendetta")

# Class User & class Tweet

test = get_tweets_from_user("lin_manuel")
test2 = get_tweets_from_user("sydbiggs")

class User():
	def __init__(self, twitter_response):
		self.id = twitter_response["id"]
		self.name = twitter_response["name"]
		self.handle = twitter_respone["screen_name"]
		self.description = twitter_response["description"]
		self.num_tweets = twitter_response["statuses_count"]
		self.followers = twitter_response["followers_count"]
		self.following = twitter_response["friends_count"]

class Tweet():
	def __init__(self, twitter_response)








