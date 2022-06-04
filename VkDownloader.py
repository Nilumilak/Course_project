import requests
import time
from YandexDrive import YandexDrive
from GoogleDrive import GoogleDrive
import configparser


class VkDownloader:
    def __init__(self, profile_id, ya_token, google_token, progress_bar):
        """
        :param profile_id: vk's page id
        :param ya_token: token for yandex drive
        :param google_token: token for google drive
        :param progress_bar: progress bar in GUI
        """
        self.ya_token = ya_token
        self.google_token = google_token
        self.progress_bar = progress_bar
        config = configparser.ConfigParser()
        config.read('settings.ini')
        self.vk_token = config['Vk']['token']
        self.respond = None
        self.profile_id = profile_id
        self.ya_respond = ''
        self.google_respond = ''

    def upload_profile_photos_to_cloud_storage(self, number_of_photos, folder='vk_profile_photos'):
        """
        1. Uploads photos to cloud storage to a folder in the root directory.
        2. Creates a new file with the list of parameters of photos.
        :param number_of_photos: number of desired photos to download
        :param folder: name of the folder in cloud storage
        """
        if self.profile_id:
            self._get_profile_photos_data(number_of_photos)
            if {'error', 'error_msg'} & self.respond.json().keys():
                print('user_id error')
            else:
                self._uploading(number_of_photos, folder)
        else:
            print('invalid_screen_name')

    def upload_album_photos_to_cloud_storage(self, album_id, number_of_photos, folder='vk_album_photos'):
        """
        1. Uploads photos to cloud storage to a folder in the root directory.
        2. Creates a new file with the list of parameters of photos.
        :param album_id: id of an album to download
        :param number_of_photos: number of desired photos to download
        :param folder: name of the folder in cloud storage
        """
        if self.profile_id:
            self._get_album_photos_data(album_id, number_of_photos)
            if {'error', 'error_msg'} & self.respond.json().keys():
                print('album_id error')
            else:
                self._uploading(number_of_photos, folder)
        else:
            print('invalid_screen_name')

    @property
    def profile_id(self):
        return self._profile_id

    @profile_id.setter
    def profile_id(self, user_id):
        if user_id.isdigit():
            self._profile_id = user_id
        else:
            param = {
                'access_token': self.vk_token,
                'user_ids': user_id,
                'v': '5.131'
            }
            respond = requests.get('https://api.vk.com/method/users.get', params=param)  # getting id with a screen_name
            time.sleep(0.5)
            if respond.json()['response']:
                self._profile_id = respond.json()['response'][0]['id']
            else:
                self._profile_id = ''

    def _get_profile_photos_data(self, number_of_photos):
        param = {
            'access_token': self.vk_token,
            'owner_id': str(self._profile_id),
            'album_id': 'profile',
            'extended': '1',
            'count': str(number_of_photos),
            'rev': '1',
            'v': '5.131'
        }

        self.respond = requests.get('https://api.vk.com/method/photos.get',
                                    params=param)  # gets the .json file for the profile photos

    def _get_album_photos_data(self, album_id, number_of_photos):
        param = {
            'access_token': self.vk_token,
            'owner_id': str(self._profile_id),
            'album_id': str(album_id),
            'count': str(number_of_photos),
            'extended': '1',
            'v': '5.131'
        }
        self.respond = requests.get('https://api.vk.com/method/photos.get',
                                    params=param)  # gets the .json file for the album photos

    def _uploading(self, number_of_photos, folder_name):
        """
        Chooses if the program should upload pictures to yandex or google drive.
        """

        if self.ya_token != '':
            yandex_uploader = YandexDrive(number_of_photos, self.respond, folder_name,
                                          self.ya_token, self.progress_bar)
            yandex_uploader.uploading_to_yandex()
            self.ya_respond = yandex_uploader.respond

        if self.google_token != '':
            google_uploader = GoogleDrive(number_of_photos, self.respond, folder_name,
                                          self.google_token, self.progress_bar)
            google_uploader.uploading_to_google()
            self.google_respond = google_uploader.respond
