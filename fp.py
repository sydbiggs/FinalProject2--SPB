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
CACHE_FNAME_U = "206project3_cache_users.json"
CACHE_FNAME_T = "206project3_cache_tweets.json"

try: 
	cache_file = open(CACHE_FNAME, 'r')
	cache_contents = cache_file.read() # pull all into one big string
	CACHE_DICTION = json.loads(cache_contents) # dictionary that holds all cache data  
	cache_file.close()
except:
	CACHE_DICTION = {}

try: 
	cache_file = open(CACHE_FNAME_U, 'r')
	cache_contents = cache_file.read() # pull all into one big string
	CACHE_DICTION_U = json.loads(cache_contents) # dictionary that holds all cache data  
	cache_file.close()
except:
	CACHE_DICTION_U= {}

try: 
	cache_file = open(CACHE_FNAME_T, 'r')
	cache_contents = cache_file.read() # pull all into one big string
	CACHE_DICTION_T = json.loads(cache_contents) # dictionary that holds all cache data  
	cache_file.close()
except:
	CACHE_DICTION_T= {}

# A function to get and cache data based on a search term
def get_tweets_from_term(searchterm):
	unique_identifier = searchterm
	if unique_identifier in CACHE_DICTION_T:
		print("Using cached data for ", searchterm, "\n")
		twitter_results = CACHE_DICTION_T[unique_identifier]
	else:
		print("Getting data from internet for ", searchterm, "\n")
		twitter_results = api.search(q = searchterm)
		CACHE_DICTION_T[unique_identifier] = twitter_results
		f = open(CACHE_FNAME_T, "w")
		f.write(json.dumps(CACHE_DICTION_T))
		f.close()
	return(twitter_results)

# A function to get and cache data about a Twitter user

def get_tweets_from_user(twitter_handle):
	unique_identifier = twitter_handle
	if unique_identifier in CACHE_DICTION_U:
		print("Using cached data for ", twitter_handle, "\n")
		twitter_results = CACHE_DICTION_U[unique_identifier]
	else:
		print("Getting data from internet for ", twitter_handle, "\n")
		# twitter_results = api.user_timeline(screen_name = twitter_handle)
		twitter_results = api.get_user(screen_name = twitter_handle)
		CACHE_DICTION_U[unique_identifier] = twitter_results
		f = open(CACHE_FNAME_U, "w")
		f.write(json.dumps(CACHE_DICTION_U))
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
test3 = get_tweets_from_term("V for Vendetta")

class TwitterUser():
	def __init__(self, twitter_response):
		self.id = twitter_response["id"]
		self.name = twitter_response["name"]
		self.handle = twitter_response["screen_name"]
		self.description = twitter_response["description"]
		self.num_tweets = twitter_response["statuses_count"]
		self.followers = twitter_response["followers_count"]
		self.following = twitter_response["friends_count"]

class Tweet():
	def __init__(self, twitter_response):
		self.id = twitter_response["id"]
		self.time = twitter_response["created_at"]
		self.rt = twitter_response["retweet_count"]
		self.tweet = twitter_response["text"]
		self.user_name = twitter_response["user"]["screen_name"]
		self.mentions=[]
		whereweare= twitter_response["entities"]["user_mentions"]
		for avalue in range(len(whereweare)):
			(self.mentions).append(whereweare[avalue]["screen_name"])

# mention_list = []
# for tweet in umich_tweets:
# 	whereweare = tweet["entities"]["user_mentions"]
# 	for avalue in range(len(whereweare)):
# 		mention_list.append(whereweare[avalue]["screen_name"])

# Pick at least 3 movie title search terms for OMDB. Put those strings in a list. 
movie1 = "V for Vendetta"
movie2 = "Superbad"
movie3 = "Pitch Perfect"
movie_list = [movie1, movie2, movie3]

# Make a request to OMDB on each of those 3 search terms, using your function, accumulate all the 
# dictionaries you get from doing this, each representing one movie, into a list
# Using that list of dictionaries, create a list of instances of class Movie.

initialized_movie_list = [Movie(get_movie_data(avalue)) for avalue in movie_list]

# Make invocations to your Twitter functions
# Use Twitter search function to search for the titles of each of those three movies
# List of instances of class Tweet:

initialized_tweet_list = []
for avalue in initialized_movie_list: 
	title = avalue.title
	mytweets = get_tweets_from_term(title)
	for i in range(len(mytweets["statuses"])):
		mytweet = Tweet(mytweets["statuses"][i])
		initialized_tweet_list.append(mytweet)

# Then, use your function to access data about a Twitter user to get information about each of the Users in the "neighborhood", 
# as it's called in social network studies -- every user who posted any of the tweets you retrieved and every user who is mentioned in them

mentions_and_users = []
for avalue in initialized_tweet_list:
	mentions_and_users.append(avalue.user_name)
	for auser in avalue.mentions:
		mentions_and_users.append(auser)

# Save a resulting list of instances of class TwitterUser
initialized_TwitterUsers = []
for avalue in mentions_and_users:
	temp_user = get_tweets_from_user(avalue)
	initialized_TwitterUsers.append(TwitterUser(temp_user))


# Create a database file with 3 tables:
# A Tweets table
# A Users table (for Twitter users)
# A Movies table

# Your Tweets table should hold in each row:
# Tweet text
# Tweet ID (primary key)
# The user who posted the tweet (represented by a reference to the users table)
# The movie search this tweet came from (represented by a reference to the movies table)
# Number favorites
# Number retweets

conn = sqlite3.connect('project3_tweets.db')
cur = conn.cursor()

statement = ('DROP TABLE IF EXISTS Tweets')
cur.execute(statement)

# Table for Tweets
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Tweets (tweet_id TEXT PRIMARY KEY, '
table_spec += 'text TEXT, user TEXT, time_posted TIMESTAMP, retweets INTEGER)'
cur.execute(table_spec)



















