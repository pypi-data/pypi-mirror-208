from abc import ABC, abstractmethod
import logging
import traceback
from requests.exceptions import ConnectionError
from qodex_cameras import settings
from qodex_cameras import functions
import os
import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from qodex_recognition import main as recognition


class PicsSaver:
    pics_folder = None
    save_pics = False

    def set_pics_folder(self, folder: str):
        self.pics_folder = folder

    def set_test_mode(self, mode: bool = True):
        self.test_mode = mode


class Camera(ABC, PicsSaver):
    schema = "http://"
    ip = None
    port = None
    rtsp_port = None
    cam_login = None
    cam_pass = None
    test_mode = None

    @abstractmethod
    def get_photo_rest(self):
        return

    def make_pic(self, name: str = None):
        # Сделать фото с именем name. Если имя не задано - использовать счетчик
        if self.test_mode:
            with open(settings.TEST_PHOTO, 'rb') as fobj:
                photo_data = fobj.read()
        else:
            photo_data = self.take_shot()
            if not photo_data:
                return
        result = {'photo_data': photo_data}
        if self.save_pics:
            if not self.pics_folder:
                self.pics_folder = settings.CUR_DIR
            photo_abs_name = os.sep.join((self.pics_folder, f"{name}.jpg"))
            functions.save_photo(photo_abs_name, photo_data)
            result['abs_path'] = photo_abs_name
        return result

    def take_shot(self):
        logging.info(f"{__name__}. Taking shot....")
        try:
            return self.get_photo_rest()
        except ConnectionError:
            logging.error(
                f"Connection error: {traceback.format_exc()}")



class HttpMakePic:
    auth_method = None
    cam_login = None
    cam_pass = None
    get_photo_url = None

    def get_http_photo(self):
        print(self.get_photo_url)
        if self.auth_method == "Basic":
            response = requests.get(
                self.get_photo_url,
                auth=HTTPBasicAuth(self.cam_login, self.cam_pass))
        elif self.auth_method == "Digest":
            response = requests.get(
                self.get_photo_url,
                auth=HTTPDigestAuth(self.cam_login, self.cam_pass))
        else:
            return
        return response.content
