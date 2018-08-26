import sys
import http.client
import json


def GetComedyID(data):
    for field in data:
        if field['name'] == 'Comedy':
            return field['id']

def FilterComedyMovies(data, id):
    for field in data:
        if id in field['genre_ids']:
            print(field['title'])

def RunQueryGetJSON(url, apiKey):
    urlBase = url.format(apiKey)

    conn = http.client.HTTPSConnection("api.themoviedb.org")

    payload = "{}"

    conn.request("GET", urlBase, payload)

    data = conn.getresponse().read().decode("utf-8")
    return json.loads(data)


def main():
    args = sys.argv
    # get id for comedy genr
    url = "/3/genre/movie/list?language=en-US&api_key={0}"
    jsonObj = RunQueryGetJSON(url, args[1])
    comedyID = GetComedyID(jsonObj['genres'])

    # use comedy id to find 300 most popular movies in genre since 1/1/2000
    url = "/3/discover/movie?primary_release_date.gte=2000-1-1&page=1&include_video=false&include_adult=false&sort_by=popularity.desc&language=en-US&api_key={0}"
    #print(comedyID)
    jsonObj = RunQueryGetJSON(url, args[1])
    FilterComedyMovies(jsonObj['results'], comedyID)
    input("Press enter to continue")
    exit()

main()

