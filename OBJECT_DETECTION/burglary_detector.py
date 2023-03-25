import cv2
import time
import urllib3
from geopy.geocoders import Nominatim

#$$$$$$$$$$#

class BURGLARY_DETECTOR :
    def __init__(self) :
        self.COUNT = 0
        self.PREV_REPORT_TIME = time.time() - 60*5

        self.GEOLOCATOR = Nominatim(user_agent="MyApp")

        self.LOCATION = "Chennai"
        location = self.GEOLOCATOR.geocode(self.LOCATION)
        self.COORDINATES = [location.latitude, location.longitude]
        self.POLICE_STATION = "CHOWKI HUH"

        self.BACKGROUND_SUBTRACTOR = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=False)

        self.HTTP_POOL = urllib3.PoolManager()
        self.CAPTURE_DEVICE = cv2.VideoCapture(0)

    def run_image_capture(self) :
        while True :
            rect, img = self.CAPTURE_DEVICE.read()
            frame = cv2.resize(img,
                               (500, 300))
            foreground_mask = self.BACKGROUND_SUBTRACTOR.apply(frame)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            foreground_mask = cv2.morphologyEx(foreground_mask,
                                               cv2.MORPH_OPEN,
                                               kernel)
            contours, hierarchy = cv2.findContours(foreground_mask,
                                                   cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 200 :
                    print("Unauthorized access detected!", self.COUNT)
                    self.COUNT += 1
                    if self.COUNT == 100 :
                        curr_time = time.time()
                        if curr_time - self.PREV_REPORT_TIME > 60*5 :
                            self.update_server(level="MODERATE", nature="Burglary")
                            self.PREV_REPORT_TIME = curr_time
                        self.COUNT = 0
                else :
                    pass

            cv2.imshow("Frame", frame) 
            cv2.imshow("Foreground Mask", foreground_mask)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):                                                           
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

if __name__ == "__main__" :
    DETECTOR_OBJ = BURGLARY_DETECTOR()
    print("HUH")
    DETECTOR_OBJ.run_image_capture()
