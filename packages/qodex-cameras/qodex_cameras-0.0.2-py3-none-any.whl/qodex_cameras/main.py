from qodex_cameras import mixins
from qodex_recognition import main as recognition


class HikCamera(mixins.Camera, mixins.ABC, mixins.HttpMakePic):
    def __init__(self, ip, port, login, password,
                 pics_folder=None, rtsp_port=554, test_mode=False,
                 auth_method="Basic", save_pics=False):
        self.ip = ip
        self.port = port
        self.rtsp_port = rtsp_port
        self.cam_login = login
        self.cam_pass = password
        self.pics_folder = pics_folder
        self.test_mode = test_mode
        self.auth_method = auth_method
        self.save_pics = save_pics
        self.get_photo_url = f"{self.schema}{self.cam_login}-{self.cam_pass}@" \
                             f"{self.ip}:{self.port}" \
                             f"/ISAPI/Streaming/channels/101/" \
                             f"picture?snapShotImageType=JPEG"

    def get_photo_rest(self):
        return self.get_http_photo()


class HikCameraCarNumberRecognition(HikCamera,
                                    recognition.MailNumberRecognitionRus):
    def __init__(self, ip, port, login, password, mail_token,
                 pics_folder=None, rtsp_port=554, test_mode=False,
                 auth_method="Basic", save_pics=False):
        super().__init__(ip, port, login, password,
                         pics_folder=pics_folder, rtsp_port=rtsp_port,
                         test_mode=test_mode,
                         auth_method=auth_method,
                         save_pics=save_pics)
        self.set_token(mail_token)


    def make_pic(self, name: str = None):
        res = super().make_pic(name=name)
        if 'error' in res:
            return res
        res['car_number'] = self.get_result(res['photo_data'])
        return res
