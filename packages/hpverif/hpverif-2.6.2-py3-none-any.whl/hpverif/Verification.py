from .Calibraton import Calibration
from .FrameCapture import Frame_Capture
from .ShowFiles import Show_Files
from .FrameCapturePLY import Frame_Capture_PLY
from .PointCloud import PointCloud
from .Segmentation import Segmentation
from .Theoretical_distance import Theoretical_distance 
import numpy as np


class Verification:
    def __init__ (self):
        pass

    
    def calibration(self):
        calibrate = Calibration()
        calibrate.enable_stream()
        calibrate.calibrate()


    def capture_frame(self,frames, filename, high):
        frame_capture = Frame_Capture()
        frame_capture.get_and_configure_device(high)
        return frame_capture.capture(frames, filename, high)
    
    def capture_frame_ply(self,filename, high):
        frame_capture = Frame_Capture_PLY()
        frame_capture.get_and_configure_device()
        frame_capture.capture(filename, high)

    def show_files(self, frame,  filename):
        show = Show_Files()
        show.enable_file(filename)
        return show.show(frame)
    
    #def kmeans (self,matrix, k):
      #  km = Kmeans()
       # km.CalculateKMeans(matrix, k)
    
    def pointCloud (self, dp, filename):
        pc = PointCloud()
        return pc.createPointCloud(0.001*np.asanyarray(dp.get_data()),filename)
        
    
    def segmentation (self, filename, min, max , fact):
        seg = Segmentation(filename,min,max,fact)
        dist_pared, dist_obj_plane, segment=seg.planeSegmentation()
        dist_obj_incline=0
        if(segment==1):
            dist_obj_incline= seg.segmentation()
        return dist_pared,dist_obj_plane, dist_obj_incline
    

    def dist_teorica(self, mapa, point, angle_degrees, show):
        d = Theoretical_distance()
        dist = d.theoric_distance(mapa, point, angle_degrees,show)
        print("Distància teorica: " + str(dist))
        return dist