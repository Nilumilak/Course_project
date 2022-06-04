import requests
from collections import Counter
import time
import json


class YandexDrive:
    def __init__(self, number_of_photos, data, path, ya_token, progress_bar):
        """
        :param number_of_photos: number of desired photos to download
        :param data: .json file with photos' data
        :param path: name of the folder in cloud storage and name of final .json file
        :param ya_token: token for yandex drive
        :param progress_bar: token for google drive
        """
        self.number_of_photos = number_of_photos
        self.data = data
        self.path = path
        self.token = ya_token
        self.progress_bar = progress_bar
        self.respond = None
        self.data_file = {'photos': []}  # future .json file

    def _same_likes_list(self):
        """
        :return: list of 'likes' that occur more than once
        """
        if 'response' in self.data.json():
            likes_list = Counter([likes['likes']['count'] for likes in self.data.json()['response']['items']])
        else:
            likes_list = Counter([likes['like_count'] for likes in self.data.json()['photos']])
        return list(filter(lambda x: likes_list[x] > 1, likes_list))

    def _bar_number(self):
        """
        Determines the length for the progress bar.
        """
        if 'response' in self.data.json() and self.data.json()['response']['count'] < self.number_of_photos:
            return self.data.json()['response']['count']
        elif 'response' not in self.data.json() and len(self.data.json()['photos']) < self.number_of_photos:
            return len(self.data.json()['photos'])
        else:
            return self.number_of_photos

    def _create_yandex_folder(self):
        """
        Creates the folder on yandex drive in the root folder.
        """
        self.respond = requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                     headers={'Content-Type': 'application/json',
                              'Authorization': f'OAuth {self.token}'},
                     params={'path': f'/{self.path}'})  # creates the folder on yandex drive
        time.sleep(0.5)

    def uploading_to_yandex(self):
        """
        1. Uploads photos to yandex drive.
        2. Creates final .json data file with pictures' information.
        """
        self.data_file = {'photos': []}

        self._create_yandex_folder()

        if ('error' in self.respond.json() and 'DiskPathPointsToExistentDirectoryError' not in self.respond.json().values()):
            print('Invalid yandex token')
        else:
            bar_number = self._bar_number()

            self.progress_bar.setRange(0, bar_number)
            steps = iter(range(bar_number))

            if 'response' in self.data.json():
                for photo in self.data.json()['response']['items']:
                    url = photo['sizes'][-1]['url']
                    size = photo['sizes'][-1]['type']
                    if photo['likes']['count'] in self._same_likes_list():  # checks if a date needs to be added to the name
                        file_name = f"{photo['likes']['count']} - {time.strftime('%d.%b.%Y', time.gmtime(photo['date']))}.jpg"
                    else:
                        file_name = f"{photo['likes']['count']}.jpg"

                    self.data_file['photos'].append({'file_name': file_name, 'size': size})  # adds data to the .json file

                    requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': f'OAuth {self.token}'},
                                  params={'path': f'/{self.path}/{file_name}', 'url': url})  # uploads photos
                    self.progress_bar.setValue(next(steps) +1)
                    time.sleep(0.5)
            else:
                for photo in self.data.json()['photos']:
                    url = photo['pic_max']
                    size = f'{photo["standard_width"]}x{photo["standard_height"]}'
                    if photo['like_count'] in self._same_likes_list():  # checks if a date needs to be added to the name
                        file_name = f"{photo['like_count']} - {time.strftime('%d.%b.%Y', time.gmtime(photo['created_ms'] / 1000))}.jpg"
                    else:
                        file_name = f"{photo['like_count']}.jpg"

                    self.data_file['photos'].append({'file_name': file_name, 'size': size})  # adds data to the .json file

                    requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': f'OAuth {self.token}'},
                                  params={'path': f'/{self.path}/{file_name}', 'url': url})  # uploads photos
                    self.progress_bar.setValue(next(steps) + 1)
                    time.sleep(0.5)

        with open(f'{self.path}.json', 'w') as new_file:
            json.dump(self.data_file, new_file, ensure_ascii=False, indent=4)  # creates the .json data
