import requests
import time
from collections import Counter
import json
from progress.bar import IncrementalBar


class VkDownloader:
    def __init__(self, vk_id, ya_token=None, google_token=None):
        """
        :param ya_token: token for yandex drive
        :param google_token: token for google drive
        :param vk_id: vk's page id
        """
        if not any([ya_token, google_token]):
            raise Exception('yandex token or google token should be entered')
        self.vk_id = vk_id
        self.ya_token = str(ya_token)
        self.google_token = str(google_token)
        with open('token.txt', 'r') as token:
            self.vk_token = str(token.read())
        self.respond = None

    def upload_profile_photos_to_yandex_drive(self, number_of_photos=5):
        """
        1. uploads photos to a yandex drive to the folder 'vk_profile_photos' in root directory.
        2. creates a new file 'vk_profile_photos.json' with the list of parameters of photos.
        :param number_of_photos: number of desired photos to download. default = 5
        """
        self.__get_profile_photos_data(number_of_photos)
        self.__create_yandex_folder('vk_profile_photos')
        self.__uploading_to_yandex('vk_profile_photos', number_of_photos)

    def upload_album_photos_to_yandex_drive(self, album_id, number_of_photos=5):
        """
        1. uploads photos to a yandex drive to the folder 'vk_album_photos' in root directory.
        2. creates a new file 'vk_album_photos.json' with the list of parameters of photos.
        :param album_id: id of an album to download
        :param number_of_photos: number of desired photos to download. default = 5
        """
        self.__get_album_photos_data(album_id, number_of_photos)
        self.__create_yandex_folder('vk_album_photos')
        self.__uploading_to_yandex('vk_album_photos', number_of_photos)

    def upload_profile_photos_to_google_drive(self, number_of_photos=5):
        """
        1. uploads photos to a google drive to the folder 'vk_profile_photos' in root directory.
        2. creates a new file 'vk_profile_photos.json' with the list of parameters of photos.
        :param number_of_photos: number of desired photos to download. default = 5
        """
        self.__get_profile_photos_data(number_of_photos)
        folder_id, folder_name = self.__create_google_folder('vk_profile_photos')
        self.__uploading_to_google(folder_id, folder_name, number_of_photos)

    def upload_album_photos_to_google_drive(self, album_id, number_of_photos=5):
        """
        1. uploads photos to a google drive to the folder 'vk_album_photos' in root directory.
        2. creates a new file 'vk_album_photos.json' with the list of parameters of photos.
        :param album_id: id of an album to download
        :param number_of_photos: number of desired photos to download. default = 5
        """
        self.__get_album_photos_data(album_id, number_of_photos)
        folder_id, folder_name = self.__create_google_folder('vk_album_photos')
        self.__uploading_to_google(folder_id, folder_name, number_of_photos)


    def __get_profile_photos_data(self, number_of_photos):
        param = {
            'access_token': self.vk_token,
            'owner_id': str(self.vk_id),
            'album_id': 'profile',
            'extended': '1',
            'count': str(number_of_photos),
            'rev': '1',
            'v': '5.131'
        }

        self.respond = requests.get('https://api.vk.com/method/photos.get',
                                    params=param)  # getting the json for all album photos

    def __get_album_photos_data(self, album_id, number_of_photos):
        param = {
            'access_token': self.vk_token,
            'owner_id': str(self.vk_id),
            'album_id': str(album_id),
            'count': str(number_of_photos),
            'extended': '1',
            'v': '5.131'
        }
        self.respond = requests.get('https://api.vk.com/method/photos.get',
                                    params=param)  # getting the json for all album photos

    def __create_yandex_folder(self, path):
        """
        Creates a folder on yandex drive in root folder
        :param path: name of the folder
        """
        requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                     headers={'Content-Type': 'application/json',
                              'Authorization': f'OAuth {self.ya_token}'},
                     params={'path': f'/{path}'})  # creating the folder on yandex drive
        time.sleep(0.33)

    def __create_google_folder(self, path):
        """
        Creates a folder on google drive in root folder
        :param path: name of the folder
        :return: folder_id - if of the folder on google drive,
                 folder_name - name of the folder on google drive
        """
        metadata = {
            'name': path,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        respond = requests.post('https://www.googleapis.com/drive/v3/files',
                                headers={'Authorization': 'Bearer ' + self.google_token,
                                         'Content-Type': 'application/json'},
                                data=json.dumps(metadata))  # creating the folder on google drive
        time.sleep(0.33)
        return respond.json()['id'], respond.json()['name']

    def __uploading_to_yandex(self, path, number_of_photos):
        likes_list = Counter([likes['likes']['count'] for likes in self.respond.json()['response']['items']])
        same_likes = list(filter(lambda x: likes_list[x] > 1, likes_list))  # likes that encounter more than once

        data_file = {'photos': []}  # future json file

        if self.respond.json()['response']['count'] < number_of_photos:  # determining the length for the progress bar
            bar_number = self.respond.json()['response']['count']
        else:
            bar_number = number_of_photos

        bar = IncrementalBar('Photos', max=bar_number)

        for photo in self.respond.json()['response']['items']:
            url = photo['sizes'][-1]['url']
            size = photo['sizes'][-1]['type']
            if photo['likes']['count'] in same_likes:  # checking if a date needs to be added to the name
                file_name = f"{photo['likes']['count']} - {time.strftime('%d.%b.%Y', time.gmtime(photo['date']))}.jpg"
            else:
                file_name = f"{photo['likes']['count']}.jpg"

            data_file['photos'].append({'file_name': file_name, 'size': size})

            requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                          headers={'Content-Type': 'application/json',
                                   'Authorization': f'OAuth {self.ya_token}'},
                          params={'path': f'/{path}/{file_name}', 'url': url})  # uploading photos
            bar.next()
            time.sleep(0.33)

        with open(f'{path}.json', 'w') as new_file:
            json.dump(data_file, new_file, ensure_ascii=False, indent=4)  # creating the json data

        bar.finish()
        print('Success!')

    def __uploading_to_google(self, folder_id, folder_name, number_of_photos):
        likes_list = Counter([likes['likes']['count'] for likes in self.respond.json()['response']['items']])
        same_likes = list(filter(lambda x: likes_list[x] > 1, likes_list))  # likes that encounter more than once

        data_file = {'photos': []}  # future json file

        if self.respond.json()['response']['count'] < number_of_photos:  # determining the length for the progress bar
            bar_number = self.respond.json()['response']['count']
        else:
            bar_number = number_of_photos

        bar = IncrementalBar('Photos', max=bar_number)

        for photo in self.respond.json()['response']['items']:
            url = photo['sizes'][-1]['url']
            size = photo['sizes'][-1]['type']
            if photo['likes']['count'] in same_likes:  # checking if a date needs to be added to the name
                file_name = f"{photo['likes']['count']} - {time.strftime('%d.%b.%Y', time.gmtime(photo['date']))}.jpg"
            else:
                file_name = f"{photo['likes']['count']}.jpg"

            data_file['photos'].append({'file_name': file_name, 'size': size})

            param = {'title': file_name,
                     'parents': [{'id': str(folder_id)}]}

            requests.post('https://www.googleapis.com/upload/drive/v2/files?uploadType=multipart',
                          headers={"Authorization": "Bearer " + self.google_token},
                          files={"data": ("metadata", json.dumps(param), "application/json; charset=UTF-8"),
                                 "file": requests.get(url).content})  # uploading photos

            bar.next()
            time.sleep(0.33)

        with open(f'{folder_name}.json', 'w') as new_file:
            json.dump(data_file, new_file, ensure_ascii=False, indent=4)  # creating the json data

        bar.finish()
        print('Success!')


if __name__ == '__main__':
    download = VkDownloader(15994285, google_token='')
    download.upload_profile_photos_to_google_drive(10)
    download.upload_album_photos_to_google_drive(138402668, 10)

    download = VkDownloader(15994285, ya_token='')
    download.upload_profile_photos_to_yandex_drive(10)
    download.upload_album_photos_to_yandex_drive(138402668, 10)


