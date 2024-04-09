from flask import Flask, request
import logging
import json
from geo import get_distance, get_geo_info

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Request: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Я могу сказать в какой стране город или сказать расстояние между городами!'
        return
    cities = get_cities(req)
    if len(cities) == 0:
        res['response']['text'] = 'Ты не написал название не одного города!'
    elif len(cities) == 1:
        res['response']['text'] = 'Этот город в стране - ' + get_geo_info(cities[0], 'country')
    elif len(cities) == 2:
        distance = get_distance(get_geo_info(cities[0], 'coordinates'), get_geo_info(cities[1], 'coordinates'))
        res['response']['text'] = 'Расстояние между этими городами: ' + str(round(distance)) + ' км.'
    else:
        res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value'].keys():
                cities.append(entity['value']['city'])
    return cities


if __name__ == '__main__':
    app.run()
