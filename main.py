import requests
import time
import json
from collections import Counter
from progress.bar import IncrementalBar
from hashlib import md5


class VkDownloader:
    def __init__(self, profile_id, ya_token=None, google_token=None):
        """
        :param profile_id: vk's page id
        :param ya_token: token for yandex drive
        :param google_token: token for google drive
        """
        if not any([ya_token, google_token]):
            raise Exception('yandex token or google token should be entered')
        self.profile_id = profile_id
        self.data_file = {'photos': []}  # future json file
        self.ya_token = str(ya_token)
        self.google_token = str(google_token)

        with open('vk_token.txt', 'r') as token:
            self.vk_token = str(token.read())  # getting token from file 'vk_token.txt'
        self.respond = None

    def upload_profile_photos_to_cloud_storage(self, number_of_photos=5, folder='vk_profile_photos'):
        """
        1. uploads photos to a yandex drive to the folder 'vk_profile_photos' in root directory.
        2. creates a new file 'vk_profile_photos.json' with the list of parameters of photos.
        :param number_of_photos: number of desired photos to download. default = 5
        :param folder: name of the folder on yandex drive
        """
        self._get_profile_photos_data(number_of_photos)
        self._uploading(number_of_photos, folder)

    def upload_album_photos_to_cloud_storage(self, album_id, number_of_photos=5, folder='vk_album_photos'):
        """
        1. uploads photos to a yandex drive to the folder 'vk_album_photos' in root directory.
        2. creates a new file 'vk_album_photos.json' with the list of parameters of photos.
        :param album_id: id of an album to download
        :param number_of_photos: number of desired photos to download. default = 5
        :param folder: name of the folder on yandex drive
        """
        self._get_album_photos_data(album_id, number_of_photos)
        self._uploading(number_of_photos, folder)

    def _get_profile_photos_data(self, number_of_photos):
        param = {
            'access_token': self.vk_token,
            'owner_id': str(self.profile_id),
            'album_id': 'profile',
            'extended': '1',
            'count': str(number_of_photos),
            'rev': '1',
            'v': '5.131'
        }

        self.respond = requests.get('https://api.vk.com/method/photos.get',
                                    params=param)  # getting the json for all profile photos

    def _get_album_photos_data(self, album_id, number_of_photos):
        param = {
            'access_token': self.vk_token,
            'owner_id': str(self.profile_id),
            'album_id': str(album_id),
            'count': str(number_of_photos),
            'extended': '1',
            'v': '5.131'
        }
        self.respond = requests.get('https://api.vk.com/method/photos.get',
                                    params=param)  # getting the json for all album photos

    def _same_likes_list(self):
        """
        :return: list of likes that encounter more than once
        """
        likes_list = Counter([likes['likes']['count'] for likes in self.respond.json()['response']['items']])
        return list(filter(lambda x: likes_list[x] > 1, likes_list))

    def _bar_number(self, number_of_photos):
        if self.respond.json()['response']['count'] < number_of_photos:  # determining the length for the progress bar
            return self.respond.json()['response']['count']
        else:
            return number_of_photos

    def _create_yandex_folder(self, path):
        """
        Creates a folder on yandex drive in root folder
        :param path: name of the folder
        """
        requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                     headers={'Content-Type': 'application/json',
                              'Authorization': f'OAuth {self.ya_token}'},
                     params={'path': f'/{path}'})  # creating the folder on yandex drive
        time.sleep(0.33)

    def _create_google_folder(self, path):
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

    def _uploading_to_yandex(self, same_likes, path, bar):
        """
        Uploads photos to yandex drive
        :param same_likes: list of likes that encounter more than once
        :param path: folder_name on yandex drive where photos will  be uploaded
        :param bar: progress bar in terminal
        """
        self.data_file = {'photos': []}

        self._create_yandex_folder(path)

        for photo in self.respond.json()['response']['items']:
            url = photo['sizes'][-1]['url']
            size = photo['sizes'][-1]['type']
            if photo['likes']['count'] in same_likes:  # checking if a date needs to be added to the name
                file_name = f"{photo['likes']['count']} - {time.strftime('%d.%b.%Y', time.gmtime(photo['date']))}.jpg"
            else:
                file_name = f"{photo['likes']['count']}.jpg"

            self.data_file['photos'].append({'file_name': file_name, 'size': size})

            requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                          headers={'Content-Type': 'application/json',
                                   'Authorization': f'OAuth {self.ya_token}'},
                          params={'path': f'/{path}/{file_name}', 'url': url})  # uploading photos
            bar.next()
            time.sleep(0.33)

    def _uploading_to_google(self, same_likes, path, bar):
        """
        Uploads photos to google drive
        :param same_likes: list of likes that encounter more than once
        :param path: folder_id on yandex drive where photos will be uploaded
        :param bar: progress bar in terminal
        """
        self.data_file = {'photos': []}

        folder_id, folder_name = self._create_google_folder(path)

        for photo in self.respond.json()['response']['items']:
            url = photo['sizes'][-1]['url']
            size = photo['sizes'][-1]['type']
            if photo['likes']['count'] in same_likes:  # checking if a date needs to be added to the name
                file_name = f"{photo['likes']['count']} - {time.strftime('%d.%b.%Y', time.gmtime(photo['date']))}.jpg"
            else:
                file_name = f"{photo['likes']['count']}.jpg"

            self.data_file['photos'].append({'file_name': file_name, 'size': size})

            param = {'title': file_name,
                     'parents': [{'id': str(folder_id)}]}

            requests.post('https://www.googleapis.com/upload/drive/v2/files?uploadType=multipart',
                          headers={"Authorization": "Bearer " + self.google_token},
                          files={"data": ("metadata", json.dumps(param), "application/json; charset=UTF-8"),
                                 "file": requests.get(url).content})  # uploading photos

            bar.next()
            time.sleep(0.33)

    def _uploading(self, number_of_photos, folder_name):
        """
        1. Chooses if the program should upload pictures to yandex or google drive
        2. Creates a .json data file with pictures information
        """

        same_likes = self._same_likes_list()

        bar_number = self._bar_number(number_of_photos)

        if self.ya_token != 'None' != self.google_token:
            bar_number *= 2

        bar = IncrementalBar('Photos', max=bar_number)  # setting the progress bar

        if self.ya_token != 'None':
            self._uploading_to_yandex(same_likes, folder_name, bar)
        if self.google_token != 'None':
            self._uploading_to_google(same_likes, folder_name, bar)

        with open(f'{folder_name}.json', 'w') as new_file:
            json.dump(self.data_file, new_file, ensure_ascii=False, indent=4)  # creating the json data

        bar.finish()
        print('Success!')


class OkDownloader(VkDownloader):
    def __init__(self, profile_id, ya_token=None, google_token=None):
        """
        :param ya_token: token for yandex drive
        :param google_token: token for google drive
        :param profile_id: ok's page id
        """
        super().__init__(profile_id, ya_token, google_token)
        if not any([ya_token, google_token]):
            raise Exception('yandex token or google token should be entered')
        self.profile_id = profile_id
        self.data_file = {'photos': []}  # future json file
        with open('ok_token.txt', 'r') as token:
            self.ok_app_id = str(token.readline()).strip()
            self.ok_app_key = str(token.readline()).strip()
            self.ok_access_token = str(token.readline()).strip()
            self.ok_secret_session_key = str(token.readline()).strip()
        self.respond = None
        self.data_file = {'photos': []}

    def upload_profile_photos_to_cloud_storage(self, number_of_photos=5, folder='ok_profile_photos'):
        super().upload_profile_photos_to_cloud_storage(number_of_photos, folder)

    def upload_album_photos_to_cloud_storage(self, album_id, number_of_photos=5, folder='ok_album_photos'):
        super().upload_album_photos_to_cloud_storage(album_id, number_of_photos, folder)

    def _get_profile_photos_data(self, number_of_photos):
        sig_params = [f'application_id={self.ok_app_id}',
                      f'application_key={self.ok_app_key}',
                      f'fid={self.profile_id}',
                      f'count={number_of_photos}'
                      ]

        sig = md5((''.join(sorted(sig_params)) + self.ok_secret_session_key).encode())

        param = {
            'application_id': f'{self.ok_app_id}',
            'application_key': f'{self.ok_app_key}',
            'access_token': f'{self.ok_access_token}',
            'sig': str(sig),
            'fid': f'{self.profile_id}',
            'count': f'{number_of_photos}'
        }

        self.respond = requests.get('https://api.ok.ru/api/photos/getPhotos', params=param)

    def _get_album_photos_data(self, album_id, number_of_photos):
        sig_params = [f'application_id={self.ok_app_id}',
                      f'application_key={self.ok_app_key}',
                      f'aid={album_id}',
                      f'count={number_of_photos}'
                      ]

        sig = md5((''.join(sorted(sig_params)) + self.ok_secret_session_key).encode())

        param = {
            'application_id': f'{self.ok_app_id}',
            'application_key': f'{self.ok_app_key}',
            'access_token': f'{self.ok_access_token}',
            'sig': str(sig),
            'aid': f'{album_id}',
            'count': f'{number_of_photos}'
        }

        self.respond = requests.get('https://api.ok.ru/api/photos/getPhotos', params=param)

    def _bar_number(self, number_of_photos):
        if len(self.respond.json()['photos']) < number_of_photos:  # determining the length for the progress bar
            return len(self.respond.json()['photos'])
        else:
            return number_of_photos

    def _uploading_to_yandex(self, path, bar):
        """
        Uploads photos to yandex drive
        :param path: folder_name on yandex drive where photos will  be uploaded
        :param bar: progress bar in terminal
        """
        self.data_file = {'photos': []}

        self._create_yandex_folder(path)

        for photo in self.respond.json()['photos']:
            url = photo['pic640x480']
            size = 'pic640x480'
            file_name = f"{photo['id']}.jpg"

            self.data_file['photos'].append({'file_name': file_name, 'size': size})

            requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                          headers={'Content-Type': 'application/json',
                                   'Authorization': f'OAuth {self.ya_token}'},
                          params={'path': f'/{path}/{file_name}', 'url': url})  # uploading photos
            bar.next()
            time.sleep(0.33)

    def _uploading_to_google(self, path, bar):
        """
        Uploads photos to google drive
        :param path: folder_id on yandex drive where photos will be uploaded
        :param bar: progress bar in terminal
        """
        self.data_file = {'photos': []}

        folder_id, folder_name = self._create_google_folder(path)

        for photo in self.respond.json()['photos']:
            url = photo['pic640x480']
            size = 'pic640x480'
            file_name = f"{photo['id']}.jpg"

            self.data_file['photos'].append({'file_name': file_name, 'size': size})

            param = {'title': file_name,
                     'parents': [{'id': str(folder_id)}]}

            requests.post('https://www.googleapis.com/upload/drive/v2/files?uploadType=multipart',
                          headers={"Authorization": "Bearer " + self.google_token},
                          files={"data": ("metadata", json.dumps(param), "application/json; charset=UTF-8"),
                                 "file": requests.get(url).content})  # uploading photos

            bar.next()
            time.sleep(0.33)

    def _uploading(self, number_of_photos, folder_name):
        """
        1. Chooses if the program should upload pictures to yandex or google drive
        2. Creates a .json data file with pictures information
        """

        bar_number = self._bar_number(number_of_photos)

        if self.ya_token != 'None' != self.google_token:
            bar_number *= 2

        bar = IncrementalBar('Photos', max=bar_number)  # setting the progress bar

        if self.ya_token != 'None':
            self._uploading_to_yandex(folder_name, bar)
        if self.google_token != 'None':
            self._uploading_to_google(folder_name, bar)

        with open(f'{folder_name}.json', 'w') as new_file:
            json.dump(self.data_file, new_file, ensure_ascii=False, indent=4)  # creating the json data

        bar.finish()
        print('Success!')


if __name__ == '__main__':
    download = VkDownloader('profile_id', ya_token='', google_token='')

    download.upload_profile_photos_to_cloud_storage(5)
    download.upload_album_photos_to_cloud_storage('album_id')

    download = OkDownloader('profile_id', ya_token='', google_token='')

    download.upload_profile_photos_to_cloud_storage(5)
    download.upload_album_photos_to_cloud_storage('album_id')
