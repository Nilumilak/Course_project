import requests
import time
from YandexDrive import YandexDrive
import json


class GoogleDrive(YandexDrive):
    def __init__(self, number_of_photos, data, path, google_token, progress_bar):
        super().__init__(number_of_photos, data, path, google_token, progress_bar)

    def _create_google_folder(self):
        """
        Creates the folder on google drive in the root folder.
        :return: folder_id - id of the folder on google drive
                 folder_name - name of the folder on google drive
        """
        metadata = {
            'name': self.path,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        self.respond = requests.post('https://www.googleapis.com/drive/v3/files',
                                headers={'Authorization': 'Bearer ' + self.token,
                                         'Content-Type': 'application/json'},
                                data=json.dumps(metadata))  # creates the folder on google drive
        time.sleep(0.5)

        if 'error' in self.respond.json():
            print('Invalid google token')
            return None, None
        else:
            return self.respond.json()['id'], self.respond.json()['name']

    def uploading_to_google(self):
        """
        1. Uploads photos to google drive.
        2. Creates final .json data file with pictures' information.
        """
        self.data_file = {'photos': []}

        folder_id, folder_name = self._create_google_folder()

        if 'error' not in self.respond.json():
            bar_number = self._bar_number()

            self.progress_bar.setValue(0)

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

                    param = {'title': file_name,
                             'parents': [{'id': str(folder_id)}]}

                    requests.post('https://www.googleapis.com/upload/drive/v2/files?uploadType=multipart',
                                  headers={"Authorization": "Bearer " + self.token},
                                  files={"data": ("metadata", json.dumps(param), "application/json; charset=UTF-8"),
                                         "file": requests.get(url).content})  # uploads photos

                    self.progress_bar.setValue(next(steps) + 1)
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

                    param = {'title': file_name,
                             'parents': [{'id': str(folder_id)}]}

                    requests.post('https://www.googleapis.com/upload/drive/v2/files?uploadType=multipart',
                                  headers={"Authorization": "Bearer " + self.token},
                                  files={"data": ("metadata", json.dumps(param), "application/json; charset=UTF-8"),
                                         "file": requests.get(url).content})  # uploads photos
                    self.progress_bar.setValue(next(steps) + 1)
                    time.sleep(0.5)

        with open(f'{self.path}.json', 'w') as new_file:
            json.dump(self.data_file, new_file, ensure_ascii=False, indent=4)  # creates the .json data
