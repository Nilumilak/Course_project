import requests
from VkDownloader import VkDownloader
from hashlib import md5
import configparser


class OkDownloader(VkDownloader):
    def __init__(self, profile_id, ya_token, google_token, progress_bar):
        """
        :param profile_id: ok's page id
        :param ya_token: token for yandex drive
        :param google_token: token for google drive
        :param progress_bar: progress bar in GUI
        """
        super().__init__(profile_id, ya_token, google_token, progress_bar)
        config = configparser.ConfigParser()
        config.read('settings.ini')
        self.ok_app_id = config['Ok']['app_id']
        self.ok_app_key = config['Ok']['app_key']
        self.ok_access_token = config['Ok']['access_token']
        self.ok_secret_session_key = config['Ok']['secret_session_key']
        self.respond = None

    def upload_profile_photos_to_cloud_storage(self, number_of_photos, folder='ok_profile_photos'):
        super().upload_profile_photos_to_cloud_storage(number_of_photos, folder)

    def upload_album_photos_to_cloud_storage(self, album_id, number_of_photos, folder='ok_album_photos'):
        super().upload_album_photos_to_cloud_storage(album_id, number_of_photos, folder)

    def _get_profile_photos_data(self, number_of_photos):
        sig_params = [f'application_id={self.ok_app_id}',
                      f'application_key={self.ok_app_key}',
                      f'fid={self.profile_id}',
                      f'count={number_of_photos}',
                      f'fields=photo.created_ms, photo.like_count, '
                      f'photo.pic_max, photo.standard_height, photo.standard_width'
                      ]

        sig = md5((''.join(sorted(sig_params)) + self.ok_secret_session_key).encode())

        param = {
            'application_id': f'{self.ok_app_id}',
            'application_key': f'{self.ok_app_key}',
            'access_token': f'{self.ok_access_token}',
            'sig': str(sig),
            'fid': f'{self.profile_id}',
            'count': f'{number_of_photos}',
            'fields': 'photo.created_ms, photo.like_count, photo.pic_max, photo.standard_height, photo.standard_width'
        }

        self.respond = requests.get('https://api.ok.ru/api/photos/getPhotos', params=param)

    def _get_album_photos_data(self, album_id, number_of_photos):
        sig_params = [f'application_id={self.ok_app_id}',
                      f'application_key={self.ok_app_key}',
                      f'aid={album_id}',
                      f'count={number_of_photos}'
                      f'fields=photo.created_ms, photo.like_count, '
                      f'photo.pic_max, photo.standard_height, photo.standard_width'
                      ]

        sig = md5((''.join(sorted(sig_params)) + self.ok_secret_session_key).encode())

        param = {
            'application_id': f'{self.ok_app_id}',
            'application_key': f'{self.ok_app_key}',
            'access_token': f'{self.ok_access_token}',
            'sig': str(sig),
            'aid': f'{album_id}',
            'count': f'{number_of_photos}',
            'fields': 'photo.created_ms, photo.like_count, photo.pic_max, photo.standard_height, photo.standard_width'
        }

        self.respond = requests.get('https://api.ok.ru/api/photos/getPhotos', params=param)
