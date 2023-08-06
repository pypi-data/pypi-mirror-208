import googlemaps


def google_places(text: str = None) -> str:
    '''
    Petición a la API GOOLE PLACE para buscar el lugar almacenado en la cadena de texto de la varibale text


    '''

    response = googlemaps.places(query=text)
    if response['status'] == 'OK':
        results = response.get('results')[0]
        name = results['name']
    else:
        name = 'N/A'

    return name
