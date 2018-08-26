import sys
import http.client
import json
import time
import csv

requestsRemaining = 40

def GetComedyID(data):
    for field in data:
        if field['name'] == 'Comedy':
            return field['id']

def FilterComedyMovies(data, id):
    comedies = []
    for field in data:
        if id in field['genre_ids']:
            comedies.append(field)
    return comedies

def CheckRateLimit(response):
    global requestsRemaining 
    requestsRemaining = response.getheader("X-RateLimit-Remaining")
    #print(requestsRemaining)

def RunQueryGetJSON(url, apiKey):
    global requestsRemaining
    urlBase = url.format(apiKey)

    conn = http.client.HTTPSConnection("api.themoviedb.org", timeout=10000)

    payload = "{}"

    conn.request("GET", urlBase, payload)
    response = conn.getresponse()

    # check to see if we hit request limit and need to wait out current 10 second interval
    CheckRateLimit(response)

    #print("Num requests remaining: " + str(requestsRemaining))
    if int(requestsRemaining) < 1:
        time.sleep(2)
        return RunQueryGetJSON(url, apiKey)

    data = response.read().decode("utf-8")
    return json.loads(data)


def GetComedyMovies(apiKey, comedyID):
    comedies = []
    page = 1
    while len(comedies) < 300:
        # use comedy id to find 300 most popular movies in genre since 1/1/2000
        url = "/3/discover/movie?primary_release_date.gte=2000-1-1&page=" + str(page) + "&include_video=false&include_adult=false&sort_by=popularity.desc&language=en-US&api_key={0}"
        #print(page)
        jsonObj = RunQueryGetJSON(url, apiKey)
        comedies.extend(FilterComedyMovies(jsonObj['results'], comedyID))
        page = page + 1
    return comedies[:300]

def WriteToCSV(fileName, dataList):
    with open(fileName, mode='w', newline='') as csv_file:
        csvWriter = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in dataList:
            csvWriter.writerow(row)

def ReturnValues(item, keys):
    values = []
    for key in keys:
        values.append(item[key])
    return values

def FindSimilarMovies(movieList, apiKey):
    movieDetailsList = []
    for movie in movieList:
        #print("Movies similar to: " + movie[1])
        url = "/3/movie/" + str(movie[0]) + "/similar?page=1&language=en-US&api_key={0}"
        jsonObj = RunQueryGetJSON(url, apiKey)
        movieDetails = ExtractMovieDetails(jsonObj['results'][:5])
        movieDetailsList.extend(list(map(lambda movieDetail: MapSimilarMovies(movieDetail, movie[0]),movieDetails)))
    return movieDetailsList

def MapSimilarMovies(movieDetail, movieID):
    return [movieID, movieDetail[0]]

def ExtractMovieDetails(moviesList):
    keys = ['id','title']
    return list(map(lambda row: ReturnValues(row, keys), moviesList))

def RemoveDuplicates(movieList):
    trimmedSet = []
    seenMovies = []
    for movie1 in range(0, len(movieList) -1):
        movie1ID = movieList[movie1][0]
        movie1SimilarID = movieList[movie1][1]
        alreadyAdded = False
        for movie2 in range(movie1+1, len(movieList)):
            movie2ID = movieList[movie2][0]
            movie2SimilarID = movieList[movie2][1]
            movieIDsSame = movie1ID == movie2SimilarID
            movieSimilarSame = movie2ID == movie2SimilarID
            seenBefore = movie2ID in seenMovies
            if movieIDsSame and movieSimilarSame and seenBefore:
                alreadyAdded = True

        if alreadyAdded == False:
            trimmedSet.append(movieList[movie1])
            seenMovies.append(movie1ID)

    return trimmedSet

def NotSeenYet(movieList, movieDetails):
    haventSeen = True
    for movie in movieList:
        if (movie[0] == movieDetails[0]) and (movie[1] == movieDetails[1]):
            haventSeen = False
    return haventSeen
        

def main():
    args = sys.argv
    # get id for comedy genre
    url = "/3/genre/movie/list?language=en-US&api_key={0}"
    jsonObj = RunQueryGetJSON(url, args[1])
    #print(jsonObj)
    comedyID = GetComedyID(jsonObj['genres'])
    comedies = GetComedyMovies(args[1], comedyID)
    comedyDetails = ExtractMovieDetails(comedies)
    #print(len(list(comedyValues)))
    WriteToCSV("movie_ID_name.csv", comedyDetails)

    # Get similar movie
    movieDetailsList = FindSimilarMovies(comedyDetails, args[1])
    WriteToCSV("movie_ID_sim_movie_ID_with_dupes.csv", movieDetailsList)

    trimmedList = RemoveDuplicates(movieDetailsList)
    WriteToCSV("movie_ID_sim_movie_ID.csv", trimmedList)

    #WriteToCSV("movie_ID_sim_movie_ID.csv", movieDetailsList)

    input("Press enter to continue")
    exit()

main()

