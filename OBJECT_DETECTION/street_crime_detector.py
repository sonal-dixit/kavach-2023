import threading
import urllib3
import time
import cv2
from geopy.geocoders import Nominatim
import numpy as np

class DETECTOR :
    def __init__(self) :
        self.frontfacefile = "haarcascade_frontalface_default.xml"
        self.sidefacefile = "haarcascade_profileface.xml"
        self.gunfile = "gun_cascade.xml"

        self.PREV_CROWD_REPORT_TIME = time.time() - 60*5
        self.PREV_GUN_REPORT_TIME = time.time() - 60*5

        self.GEOLOCATOR = Nominatim(user_agent="MyApp")

        self.LOCATION = "Chennai"
        location = self.GEOLOCATOR.geocode(self.LOCATION)
        self.COORDINATES = [location.latitude, location.longitude]
        self.POLICE_STATION = "CHOWKI N"

        self.HTTP_POOL = urllib3.PoolManager()

        self.CROWD_COUNT = 0
        self.GUN_COUNT = 0

        self.CAPTURE_DEVICE = cv2.VideoCapture(0)

        self.FRONT_FACE_CASCADE = cv2.CascadeClassifier(self.frontfacefile)
        self.SIDE_FACE_CASCADE = cv2.CascadeClassifier(self.sidefacefile)
        self.GUN_CASCADE = cv2.CascadeClassifier(self.gunfile)

    def run_image_capture(self) :
        while True :
            time.sleep(1/1000)
            rect, img = self.CAPTURE_DEVICE.read()

            frame = cv2.resize(img, (500, 300))
            graystyle_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces1 = self.FRONT_FACE_CASCADE.detectMultiScale(graystyle_img,
                                                              scaleFactor=1.1,
                                                              minNeighbors=4, 
                                                              minSize=(10, 10),
                                                              flags=cv2.CASCADE_SCALE_IMAGE)
            faces2 = self.SIDE_FACE_CASCADE.detectMultiScale(graystyle_img,
                                                             scaleFactor=1.1,
                                                             minNeighbors=5,
                                                             minSize=(10, 10),
                                                             flags=cv2.CASCADE_SCALE_IMAGE)
            guns = self.GUN_CASCADE.detectMultiScale(graystyle_img,
                                                     scaleFactor=1.1,
                                                     minNeighbors=3,
                                                     minSize=(10, 10),
                                                     flags=cv2.CASCADE_SCALE_IMAGE)

            faces = []
            #if list(faces2) != [] :
            #    faces += list(faces2)
            if list(faces1) != [] :
                faces += list(faces1)

            person_boxes = []

            for _ in faces :
                cv2.rectangle(graystyle_img,
                              (_[0] - int(_[2]*0.33),
                               _[1] - int(_[3]*0.33)),
                              (_[0] + int(_[2]*1.33),
                               _[1] + int(_[3]*1.33)),
                              (255, 255, 255),
                              2)
                person_boxes.append([_[0] - int(_[2]*0.33),
                                     _[1] - int(_[3]*0.33),
                                     _[0] + int(_[2]*1.33),
                                     _[1] + int(_[3]*1.33)])

            crowded = self.chek_if_crowded(person_boxes)

            if crowded :
                self.CROWD_COUNT += 1
            if self.CROWD_COUNT > 1 :
                if time.time() - self.PREV_CROWD_REPORT_TIME > 60*3 :
                    self.update_server(level="LOW", nature="Street Crime")
                    self.PREV_CROWD_REPORT_TIME = time.time()
                self.CROWD_COUNT = 0
            
            if len(guns) != 0 :
                self.GUN_COUNT += 1
            if time.time() - self.PREV_GUN_REPORT_TIME > 60*3 :
                if self.GUN_COUNT == 2 and len(person_boxes) > 1 :
                    self.update_server(level="HIGH", nature="Violence")
                    self.GUN_COUNT = 0
                if self.GUN_COUNT == 2 and len(person_boxes) == 1 :
                    self.update_server(level="MODERATE", nature="Burglary")
                    self.GUN_COUNT = 0
                self.PREV_GUN_REPORT_TIME = time.time()

            cv2.imshow('frame',graystyle_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def update_server(self, **kwargs) :
        field_data = kwargs
        field_data['city'] = self.LOCATION
        field_data['coordinates'] = str(self.COORDINATES)
        field_data['reported'] = self.POLICE_STATION
        try :
            self.HTTP_POOL.request('POST',
                                   'http://172.16.42.54:5000/put',
                                   fields=field_data)
            print("[#] DATA SENT TO SERVER")
        except :
            print("[!] ERROR")

    def chek_if_crowded(self, frame_areas) :
        if 1 < len(frame_areas) :
            number_of_people = len(frame_areas)
            overlaps = 0
            for _ in range(len(frame_areas)) :
                for __ in range(0, len(frame_areas)) :
                    if _ != __ :
                        if ( frame_areas[_][0] < frame_areas[__][0] < frame_areas[_][2] and frame_areas[_][1] < frame_areas[__][1] < frame_areas[_][3] ) or \
                                ( frame_areas[_][0] < frame_areas[__][2] < frame_areas[_][2] and frame_areas[_][1] < frame_areas[__][1] < frame_areas[_][3] ) or \
                                ( frame_areas[_][0] < frame_areas[__][0] < frame_areas[_][2] and frame_areas[_][1] < frame_areas[__][3] < frame_areas[_][3] ) or \
                                ( frame_areas[_][0] < frame_areas[__][2] < frame_areas[_][2] and frame_areas[_][1] < frame_areas[__][3] < frame_areas[_][3] ) :
                            overlaps += 1
            if overlaps >= (number_of_people*1.5 - 1) :
                return True
            return False
        return False

if __name__ == "__main__" :
    DETECTOR_OBJ = DETECTOR()
    DETECTOR_OBJ.run_image_capture()
