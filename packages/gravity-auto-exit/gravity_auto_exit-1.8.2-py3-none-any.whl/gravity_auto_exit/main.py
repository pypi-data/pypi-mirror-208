import datetime
import os
import threading
import time
import uuid
from cad.main import CAD
from whikoperator.main import Wpicoperator
import requests
from gravity_auto_exit.logger import logger
from neurocore_worker.main import NeuroCoreWorker
from qodex_recognition.main import MailNumberRecognitionRus


class AutoExit:
    def __init__(self, cam_host, cam_login, cam_password,
                 neurocore_login, neurocore_password,
                 auth_method='Digest', engine_callback=None,
                 debug=False, failed_callback=None,
                 resize_photo: tuple = False, cam_port=80,
                 catch_event='Line Crossing',
                 simple_callback_func=None,
                 sleep_before=1, engine=None, **kwargs):
        self.engine = engine
        self.simple_callback_func = simple_callback_func
        self.sleep_before = sleep_before
        self.neurocore_worker = NeuroCoreWorker(
            api_login=neurocore_login,
            api_password=neurocore_password,
            plate_frame_size=resize_photo)
        self.cad = CAD(host=cam_host, port=cam_port, login=cam_login,
                       password=cam_password,
                       callback_func=self.cad_callback_func,
                       delay_time=0,
                       logger=logger,
                       catch_event=catch_event)
        cam_ip = cam_host.replace('http://', '')
        cam_ip = f"{cam_ip}:{cam_port}"
        if not logger:
            logger.getLogger(type(self).__name__)
        else:
            logger.name = type(self).__name__
        self.active = True
        self.resize_photo = resize_photo
        self.cam = Wpicoperator(
            cam_ip=cam_ip,
            cam_login=cam_login,
            cam_pass=cam_password,
            auth_method=auth_method)
        self.callback_request_url = None
        self.debug = debug
        self.last_take = datetime.datetime.now()
        self.failed_callback = failed_callback
        self.engine_callback = engine_callback
        self.wait_started = False
        self.cycle_started = False
        logger.debug('AUTO_EXIT has started successfully')

    def set_active(self, activity_bool: bool):
        self.active = activity_bool

    def set_can_wait_others(self, boolean: bool):
        self.can_wait_others = boolean

    def start(self):
        self.cad.mainloop()

    def save_pic(self, pic_name, pic_body, frmt='.jpg'):
        logger.debug(f'Saving picture {pic_name}')
        with open(pic_name + frmt, 'wb') as fobj:
            fobj.write(pic_body)
        logger.debug("Success!")

    def cad_callback_func(self, data=None):
        logger.debug("=====CAD func started=====")
        if self.simple_callback_func:
            threading.Thread(target=self.simple_callback_func).start()
        if not self.active:
            logger.debug("---It is not active---")
            return
        if self.engine and not self.engine.status_ready:
            logger.debug("Engine is not ready!")
            return
        logger.debug(f'Sleeping before: {self.sleep_before}')
        time.sleep(self.sleep_before)
        logger.debug("Recognise cycle has been started")
        for i in range(5):
            if self.engine and not self.engine.status_ready:
                logger.info("Cancel cycle for engine is not ready")
                return
            logger.debug(f"Recognise cycle {i} of 5")
            time.sleep(i + 0.2)
            if not self.active:
                self.active = True
            #    return
            response = self.camera_and_recognise()
            if 'error' in response:
                logger.error(f"{response['error']}")
            else:
                result, photo = response
                if result:
                    self.last_take = datetime.datetime.now()
                    logger.debug(f"Success recognise. Number {result}")
                    self.wait_started = False
                    # self.active = True
                    # self.cycle_started = False
                    return result
                else:
                    logger.error(
                        f"Unknown Error! Number {result}")
            if self.failed_callback and i == 2:
                logger.debug(f'Failed callbaсk working photo...')
                self.failed_callback()
        self.wait_started = False
        self.cycle_started = False

    def camera_and_recognise(self):
        result = self.try_recognise_plate()
        if 'error' in result:
            return result
        photo, result = result['photo'], result['number']
        if result:
            if self.debug:
                self.save_pic(f"{str(uuid.uuid4())}.jpg", photo)
            if self.engine_callback:
                try:
                    self.engine_callback(result, photo)
                except:
                    pass
        return result, photo

    def http_callback(self, number):
        requests.post(self.callback_request_url,
                      params={'number': number})

    def try_recognise_plate(self):
        logger.debug(f'Taking photo...')
        photo = self.cam.take_shot()
        if not photo:
            return photo
        result = self.get_car_number(photo)
        result = self._recognise(photo)
        return result

    def _recognise(self, photo):
        return self.neurocore_worker.get_car_number(photo)

    def get_car_number(self, photo):
        pass

    def set_post_request_url(self, url):
        self.callback_request_url = url
        return url


class CADRecogniseMail(AutoExit, MailNumberRecognitionRus):
    def __init__(self, cam_host, cam_login, cam_password,
                 auth_method='Digest', engine_callback=None,
                 debug=False, failed_callback=None,
                 resize_photo: tuple = False, cam_port=80,
                 simple_callback_func=None,
                 sleep_before=1, engine=None, **kwargs):
        super(CADRecogniseMail, self).__init__(
            cam_host, cam_login,
            cam_password,
            neurocore_login=None,
            neurocore_password=None,
            auth_method=auth_method,
            engine_callback=engine_callback,
            debug=debug,
            failed_callback=failed_callback,
            resize_photo=resize_photo,
            cam_port=cam_port,
            simple_callback_func=simple_callback_func,
            sleep_before=sleep_before,
            engine=engine)

    def _recognise(self, photo):
        res = self.get_result(photo)
        if 'error' in res:
            return res
        return {'number': res, 'photo': photo}

class CADEntrance(AutoExit):
    """ Детекция автомобиля на брутто """
    pass


if __name__ == '__main__':
    def engine_callback(*args, **kwargs):
        print('MAIN')


    inst = CADRecogniseMail(  #
        #'http://192.168.60.107',
         #'http://172.16.6.176',
        "http://127.0.0.1",
        'admin',
        'Assa+123',
        debug=True,
        #        cam_port=80,
        # 1920*1080
        cam_port=82,
        neurocore_login='admin',
        neurocore_password='admin',
        engine_callback=engine_callback
    )
    inst.set_token(os.environ.get("mail_token"))
    inst.start()
    #res = inst.try_recognise_plate()
    #print(res['number'])
