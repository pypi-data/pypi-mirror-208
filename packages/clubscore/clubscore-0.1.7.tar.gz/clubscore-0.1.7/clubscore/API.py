import requests

def getRoundRobinStandings(id):

    response = requests.get(f"https://api.score7.io/tournaments/{id}/roundRobinGroups")
    data = response.json()
    #print(data)
    field_value = data[0]["id"]
    #print(field_value)

    url = "https://api.score7.io/roundRobinGroups/" + str(field_value) + "/standing"
    response = requests.get(url)
    data = response.json()
    field_value = data["id"]
    #print(field_value)

    url = "https://api.score7.io/standings/" + str(field_value) + "/standingEntries"
    response = requests.get(url)
    data = response.json()
    #print(data)
    lista = []

    for k in data:
            lista.append(k["participant"]["name"])
            lista.append(str(int(k["points"])))


    return lista