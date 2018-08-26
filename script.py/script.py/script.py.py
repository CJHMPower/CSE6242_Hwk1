import sys
import http.client
import json
import time

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

    conn = http.client.HTTPSConnection("api.themoviedb.org")

    payload = "{}"

    conn.request("GET", urlBase, payload)
    response = conn.getresponse()

    # check to see if we hit request limit and need to wait out current 10 second interval
    CheckRateLimit(response)

    print("Num requests remainig: " + str(requestsRemaining))
    if int(requestsRemaining) < 1:
        time.sleep(2)
        RunQueryGetJSON(url, apiKey)

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
    return comedies

def main():
    args = sys.argv
    # get id for comedy genre
    url = "/3/genre/movie/list?language=en-US&api_key={0}"
    jsonObj = RunQueryGetJSON(url, args[1])
    #print(jsonObj)
    comedyID = GetComedyID(jsonObj['genres'])
    print(len(GetComedyMovies(args[1], comedyID)))
    
    input("Press enter to continue")
    exit()

main()

