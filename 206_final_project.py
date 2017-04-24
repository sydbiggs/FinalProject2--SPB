## Import statements
import unittest
import json
import requests
import tweepy
from bs4 import BeautifulSoup
import re
import twitter_info
import sqlite3
import collections

#Twitter info:
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())


# Set up cache file:

CACHE_FNAME = "206_final_project_cache.json"
try: 
	cache_file = open(CACHE_FNAME, 'r')
	cache_contents = cache_file.read() # pull all into one big string
	CACHE_DICTION = json.loads(cache_contents) # dictionary that holds all cache data  
	cache_file.close()
except:
	CACHE_DICTION = {}

# PART (A): Write functions to get and cache data from OMDB and Twitter

# A function to get and cache data based on a search term in Twitter:
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

# A function to get and cache data about a Twitter user:
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

# A function to get and cache data from the OMDB API (later we'll use a movie director as a search term):
def get_movie_data(avalue):
	unique_identifier = avalue
	if unique_identifier in CACHE_DICTION:
		print("Using cached data for ", avalue, "\n")
		results = CACHE_DICTION[unique_identifier]
	else:
		baseurl = "http://www.omdbapi.com/"
		ombd_param = {}
		ombd_param["t"] = avalue
		ombd_param["type"] = "movie"
		print("Getting data from internet for ", avalue ,"\n")
		response = requests.get(baseurl, ombd_param)
		results = json.loads(response.text)
		CACHE_DICTION[unique_identifier] = results
		f = open(CACHE_FNAME, "w")
		f.write(json.dumps(CACHE_DICTION))
		f.close()
	return(results)

# PART (B): Define classes
# Define a class to hold info about a particular movie

class Movie():
	def __init__(self, movie_response): #where movie_response = dictionary with info about a movie
		self.title = movie_response["Title"]
		self.director = movie_response["Director"]
		self.released = movie_response["Released"]
		self.num_languages = len([avalue.strip() for avalue in movie_response["Language"].split(",")])
		self.runtime = movie_response["Runtime"]
		self.actors = [avalue.strip() for avalue in movie_response["Actors"].split(",")]
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
		return("{}, directed by {} and starring {}".format(self.title, self.director, self.actors[0]))

	def most_common_plot_word(self):
		punct = ['.', ',', '!', '?']
		new_plot = (("".join(avalue for avalue in self.plot if avalue not in punct)).lower()).split(' ')
		plot_dict = {}
		for avalue in new_plot:
			if avalue not in plot_dict:
				plot_dict[avalue] = 0
			plot_dict[avalue] = plot_dict[avalue] + 1
		sorted_plot = sorted(sorted(plot_dict), key = lambda x: plot_dict[x], reverse = True)
		return(sorted_plot[0])

# OPTIONAL classes
# Define a class to hold info about a particular Twitter user:
class TwitterUser():
	def __init__(self, twitter_response):
		self.user_id = twitter_response["id"]
		self.name = twitter_response["name"]
		self.screen_name = twitter_response["screen_name"]
		self.description = twitter_response["description"]
		self.num_tweets = twitter_response["statuses_count"]
		self.followers = twitter_response["followers_count"]
		self.following = twitter_response["friends_count"]
		self.num_favorites = twitter_response["favourites_count"]
		self.location = twitter_response["time_zone"]

# Define a class to hold info about a particular Tweet:
class Tweet():
	def __init__(self, twitter_response):
		self.id = twitter_response["id"]
		self.user_id = twitter_response["user"]["id"]
		self.time = twitter_response["created_at"]
		self.rt = twitter_response["retweet_count"]
		self.tweet = twitter_response["text"]
		self.user_name = twitter_response["user"]["screen_name"]
		self.num_favorites = twitter_response["favorite_count"]
		self.mentions=[]
		whereweare= twitter_response["entities"]["user_mentions"]
		for avalue in range(len(whereweare)):
			(self.mentions).append(whereweare[avalue]["screen_name"])

	def add_title(self, movie_title):
		self.title = movie_title

# PART (C): Invocations to the functions:
# Pick at least 3 movie title search terms for OMDB. Put those strings in a list. 
movie1 = "Jaws"
movie2 = "Moonrise Kingdom"
movie3 = "Aliens"
movie_list = [movie1, movie2, movie3]

#INVOCATIONS OF EACH FUNCTION ARE AS FOLLOWS:

# Make a request to OMDB on each of those 3 search terms, using your function, accumulate all the dictionaries you get from doing this, 
# each representing one movie, into a list. Using that list of dictionaries, create a list of instances of class Movie.

initialized_movie_list = [Movie(get_movie_data(avalue)) for avalue in movie_list]

# Make invocations to your Twitter functions. Use Twitter search function to search for the titles of each of those three movies
# List of instances of class Tweet:

initialized_tweet_list = []
for avalue in initialized_movie_list: 
	dirt = avalue.director
	mytweets = get_tweets_from_term(dirt)
	for i in range(len(mytweets["statuses"])):
		mytweet = Tweet(mytweets["statuses"][i])
		mytweet.add_title(avalue.title)
		initialized_tweet_list.append(mytweet)

# Use your function to access data about a Twitter user to get information about each of the Users in the "neighborhood", 
# as it's called in social network studies -- every user who posted any of the tweets you retrieved and every user who is mentioned in them

#Get a list of all Users in the "neighborhood"
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

# PART (D): Creating Databases

# Create a database file with 3 tables:

conn = sqlite3.connect('project3_tweets.db')
cur = conn.cursor()

statement = ('DROP TABLE IF EXISTS Movies')
cur.execute(statement)
statement = ('DROP TABLE IF EXISTS Tweets')
cur.execute(statement)

# Table for Movies
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Movies (id INTEGER PRIMARY KEY, '
table_spec += 'Title TEXT, Director TEXT, Num_Languages INTEGER, IMDB INTEGER, Rotton_Tomatoes INTEGER, Main_Actor TEXT, plot TEXT)'
cur.execute(table_spec)

# Table for Tweets
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Tweets(tweet_id TEXT PRIMARY KEY, '
# table_spec += 'Tweet TEXT, User TEXT, Movie_Title TEXT, FOREIGN KEY(Movie_Title) REFERENCES Movies(Title), Num_Favorites INTEGER, number_retweets INTEGER)'
table_spec += 'Tweet TEXT, user_id TEXT, screen_name TEXT, Title TEXT, Num_Favorites INTEGER, number_retweets INTEGER)'
cur.execute(table_spec)

#Table for Users
table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Users(user_id TEXT PRIMARY KEY, '
table_spec += 'screen_name TEXT, num_favorites TEXT, name TEXT, description TEXT, location TEXT)'
cur.execute(table_spec)

#Now put the data into our tables:

Movie_list = []
for i in range(len(initialized_movie_list)):
	Title = initialized_movie_list[i].title
	Director = initialized_movie_list[i].director
	Number_Languages = initialized_movie_list[i].num_languages
	IMDB_Rating = initialized_movie_list[i].ratings["Internet Movie Database"]
	Rotton_Tomatoes_Rating_perc = initialized_movie_list[i].ratings["Rotten Tomatoes"]
	Rotton_Tomatoes_Rating = Rotton_Tomatoes_Rating_perc[:(len(Rotton_Tomatoes_Rating_perc)-1)]
	Main_Actor = initialized_movie_list[i].actors[0]
	plot = initialized_movie_list[i].plot
	Movie_list.append((None, Title, Director, Number_Languages, IMDB_Rating, Rotton_Tomatoes_Rating, Main_Actor, plot))

statement = 'INSERT INTO Movies VALUES (?,?,?,?,?,?,?,?)'
for avalue in Movie_list:
	cur.execute(statement, avalue)

Tweet_list = []
for i in range(len(initialized_tweet_list)):
	tweet_id = initialized_tweet_list[i].id
	text = initialized_tweet_list[i].tweet
	userid = initialized_tweet_list[i].user_id
	user = initialized_tweet_list[i].user_name
	movie_title = initialized_tweet_list[i].title
	number_favorites = initialized_tweet_list[i].num_favorites
	number_retweets = initialized_tweet_list[i].rt
	Tweet_list.append((tweet_id, text, userid, user, movie_title, number_favorites, number_retweets))

# Table for Users
statement = 'INSERT INTO Tweets VALUES (?,?,?,?,?,?,?)'
for avalue in Tweet_list:
	cur.execute(statement,avalue)

statement = 'INSERT OR IGNORE INTO Users VALUES (?,?,?,?,?,?)'
for i in range(len(initialized_TwitterUsers)):
	user_id = initialized_TwitterUsers[i].user_id
	screen_name = initialized_TwitterUsers[i].screen_name
	num_favorites = initialized_TwitterUsers[i].num_favorites
	name = initialized_TwitterUsers[i].name
	description = initialized_TwitterUsers[i].description
	location = initialized_TwitterUsers[i].location
	cur.execute(statement, (user_id, screen_name, num_favorites, name, description, location))
conn.commit()

## THREE+ QUERIES TO THE DATABASES:

## Get the most popular locations for each movie to be tweeted about for tweets that actually have some relevance (i.e. rt > 100)
query = "SELECT Tweets.title,Users.location FROM Users INNER JOIN Tweets ON Users.user_id WHERE number_retweets > 100"
cur.execute(query)
loc_list = [avalue for avalue in cur]

#Get tweets about movies that have been retweeted more than 100 times
query = "SELECT Title, Tweet FROM Tweets WHERE number_retweets > 100"
cur.execute(query)
popular_tweets = [avalue for avalue in cur]

# Get movies with a very high IMDB score
query = "SELECT Title, IMDB FROM Movies WHERE Rotton_Tomatoes > 90"
cur.execute(query)
great_scores_movies = [avalue for avalue in cur]

# Get user descriptions and movie descriptions and see what words they have in common
query = "SELECT Title, number_retweets FROM Tweets WHERE number_retweets > 0"
cur.execute(query)
num_rt_list = [avalue for avalue in cur]
# for avalue in description_list:
# 	print(avalue)

# Get movie plot
query = "SELECT Title, plot from Movies"
cur.execute(query)
Title_Plot = [avalue for avalue in cur]
conn.close()

# PART (E): Process the data and create an output file

## (1) Use Counter to count the number of locations for each movie-- i.e. find the most common time zone for each movie

loc_dict = {}
for avalue in loc_list:
	temp_title = avalue[0]
	temp_location = avalue[1]
	if temp_location == None:
		pass
	elif temp_title not in loc_dict:
		loc_dict[temp_title] = [temp_location]
	else:
		loc_dict[temp_title].append(temp_location)

count_jaws = (collections.Counter(loc_dict[movie1]).most_common(1))[0][0]
# print(count_jaws)
count_MR = collections.Counter(loc_dict[movie2]).most_common(1)[0][0]
# print(count_MR)
count_aliens = collections.Counter(loc_dict[movie3]).most_common(1)[0][0]
# print(count_aliens)

## (2) From the tweets that have been retweeted more than 100 times, return the shortest one using SORTED method

def shortest_popular_tweet(alist, amovie):
	pop_list = [avalue[1] for avalue in alist if avalue[0] == amovie]
	temp = []
	for avalue in pop_list:
		new = avalue.replace(',', '')
		temp.append(new)
	sorted_list = sorted(sorted(temp), key = lambda x: len(x), reverse = False)
	return(sorted_list[0])

popular_jaws = shortest_popular_tweet(popular_tweets, movie1)
popular_MK = shortest_popular_tweet(popular_tweets, movie2)
popular_aliens = shortest_popular_tweet(popular_tweets, movie3)


# (3) Use dictionary comprehension to make dict of movie and it's plot

#first, remove commas from the movies plot (we can't write to a CSV file when there are commas)
new_title_plot = []
for avalue in Title_Plot:
	new = avalue[1].replace(',', '')
	new_title_plot.append((avalue[0], new))

title_to_plot_dict = {avalue[0]: avalue[1] for avalue in new_title_plot} 

# (4) Use regrex to get every IMDB score as a number, not a TEXT (which is how it is imported into the database)
def get_imdb_score(imdb_score):
	regex = r".+?(?=/)"
	score = re.findall(regex, imdb_score)
	return(score[0])

IMDB_jaws = get_imdb_score(great_scores_movies[0][1])
IMDB_MK = get_imdb_score(great_scores_movies[1][1])
IMDB_aliens = get_imdb_score(great_scores_movies[2][1])

# (5) Average number of retweets per movie
rt_movies = [movie1, movie2, movie3]
def average_rts(alist, amovie):
	count = 0
	total = 0
	for avalue in alist: #(Title, num_rts)
		if avalue[0] == amovie:
			count = count + avalue[1]
			total = total + 1
	return(count/total)

movie1_rts = average_rts(num_rt_list, movie1)
movie2_rts = average_rts(num_rt_list, movie2)
movie3_rts = average_rts(num_rt_list, movie3)

print("And finally, the movies we will be putting in our output file are: ")
for avalue in initialized_movie_list:
	print(avalue)

##### WRITE TO FILE ########
final_file = "206_Final_Project_Bigelow.csv"
outfile = open(final_file, "w")
outfile.write("Title, Most popular tweet location, Shortest popular tweet, movie plot, Average number of retweets, Most popular plot word, IMDB score (out of 10)\n")
titles = [movie1, movie2, movie3]
loc = [count_jaws, count_MR, count_aliens]
pop = [popular_jaws, popular_MK, popular_aliens]
plt = [title_to_plot_dict[movie1], title_to_plot_dict[movie2], title_to_plot_dict[movie3]]
rts = [movie1_rts, movie2_rts, movie3_rts]
popular_plt_word = []
for avalue in initialized_movie_list:
	popular_plt_word.append(avalue.most_common_plot_word())
imdb = [IMDB_jaws, IMDB_MK, IMDB_aliens]
for i in range(len(titles)):
	first = titles[i]
	second = loc[i]
	third = pop[i]
	fourth = plt[i]
	fourpointfive = rts[i]
	fifth = popular_plt_word[i]
	sixth = imdb[i]
	try:
		outfile.write(str(first)  + "," + str(second) + "," + str(third) + "," + str(fourth) + "," + str(fourpointfive) + "," + str(fifth) + "," + str(sixth) + "\n")
	except:
		print("Oops, something went wrong")
outfile.close()


######################### TESTS #########################
class Test_Project_Functions(unittest.TestCase):
	def test_get_tweets_from_term_type(self):
		self.assertEqual(type(get_tweets_from_term("V for Vendetta")), type({}))
	def test_get_tweets_from_user_type(self):
		self.assertEqual(type(get_tweets_from_user("sydbiggs")), type({}))
	def test_get_movie_data_type(self):
		self.assertEqual(type(get_movie_data("Pitch Perfect")), type({}))

class Test_Movie_Class(unittest.TestCase):
	def test_Movie_title(self):
		mymovie = get_movie_data("The Avengers")
		testmovie = Movie(mymovie)
		self.assertEqual(testmovie.title, "The Avengers")
	def test_Movie_director(self):
		mymovie = get_movie_data("The Avengers")
		testmovie = Movie(mymovie)
		self.assertEqual(testmovie.director, "Joss Whedon")
	def test_Movie_string(self):
		mymovie = get_movie_data("The Avengers")
		testmovie = Movie(mymovie)
		self.assertEqual(testmovie.__str__(), "The Avengers, directed by Joss Whedon and starring Robert Downey Jr.")
	def test_Movie_ratings_type(self):
		mymovie = get_movie_data("The Avengers")
		testmovie = Movie(mymovie)
		self.assertEqual(type(testmovie.ratings),type({}))
	def test_most_common_plot_word(self):
		mymovie = get_movie_data("The Avengers")
		test = Movie(mymovie)
		self.assertEqual(type(test.most_common_plot_word()), type("hi"))

class Test_TwitterUser_Class(unittest.TestCase):
	def test_TwitterUser_screen_name(self):
		myuser = get_tweets_from_user("Lin_Manuel")
		testuser = TwitterUser(myuser)
		self.assertEqual(testuser.screen_name, "Lin_Manuel")
	def test_TwitterUser_description_type(self):
		myuser = get_tweets_from_user("Lin_Manuel")
		testuser = TwitterUser(myuser)
		self.assertEqual(type(testuser.description), type("the OG"))
	def test_TwitterUser_numtweets_type(self):
		myuser = get_tweets_from_user("lin_manuel")
		testuser = TwitterUser(myuser)
		self.assertEqual(type(testuser.num_tweets), type(4))

class Test_Tweet_Class(unittest.TestCase):
	def test_Tweet_id_type(self):
		mytweet = get_tweets_from_term("popsicle")
		testtweet = Tweet(mytweet["statuses"][0])
		self.assertEqual(type(testtweet.id), type(4))
	def test_Tweet_mentions_type(self):
		mytweet = get_tweets_from_term("popsicle")
		testtweet = Tweet(mytweet["statuses"][0])
		self.assertEqual(type(testtweet.mentions), type([]))
	def test_Tweet_num_favorites_type(self):
		mytweet = get_tweets_from_term("popsicle")
		testtweet = Tweet(mytweet["statuses"][0])
		self.assertEqual(type(testtweet.num_favorites), type(4))
	def test_add_title(self):
		mytweet = get_tweets_from_term("popsicle")
		testtweet = Tweet(mytweet["statuses"][0])
		testtweet.add_title("Not a real movie")
		self.assertEqual(testtweet.title, "Not a real movie")

class Test_everything_else(unittest.TestCase):
	def test_shortest_popular_tweet(self):
		mylist = [("test movie", "hi my name is Sydney"), ("test movie", "okay"), ("diff movie", "something else that is longer than okay")]
		self.assertEqual(shortest_popular_tweet(mylist, "test movie"), "okay")
	def test_shortest_popular_tweet_type(self):
		mylist = [("test", "edge case, just one value")]
		self.assertEqual(type(shortest_popular_tweet(mylist, "test")), type("hi"))
	def test_get_IMDB_score(self):
		self.assertEqual(get_imdb_score("8.0/10"), '8.0')
	def test_IMDB_type(self):
		self.assertEqual(type(get_imdb_score("9/10")), type("hi"))
	def test_IMDB_score_no_dec(self):
		self.assertEqual(get_imdb_score("9/10"), "9")
	def test_average_rts(self):
		mylist = [("movie", 4), ("movie", 10)]
		self.assertEqual(average_rts(mylist, "movie"), 7)

if __name__ == "__main__":
	unittest.main(verbosity=2)