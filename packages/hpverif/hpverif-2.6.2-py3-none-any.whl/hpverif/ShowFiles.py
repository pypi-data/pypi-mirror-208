import cv2                                # state of the art computer vision algorithms library
import numpy as np                        # fundamental package for scientific computing
import pyrealsense2 as rs  




class Show_Files:
   
    def __init__ (self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.pc = rs.pointcloud()




    def enable_file (self, file):
         

        rs.config.enable_device_from_file(self.config , file)
        self.config.enable_stream(rs.stream.depth, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        profile = self.pipeline.start(self.config)



    def show (self, frame):

        cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)
  
        pointcloud=rs.pointcloud()
       

        # Create colorizer object
        colorizer = rs.colorizer()
        iter = 0
            # Streaming loop
        while True:
                iter = iter + 1
                # Get frameset of depth
                frames = self.pipeline.wait_for_frames()

                # Get depth frame
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()

                #points = pointcloud.calculate(depth_frame)

                #verts = np.asarray(points.get_vertices())
                #rgbs = np.asarray(color_frame.get_data())
                #pcd = o3d.geometry.PointCloud()
                #pcd.points = o3d.utility.Vector3dVector(verts)
                #pcd.colors = o3d.utility.Vector3dVector(rgbs)

                 # Visualizar el pointcloud
                #o3d.visualization.draw_geometries([pcd])

                if(iter == frame-6):
                     final_depth = depth_frame
                     final_rgb = color_frame 
                # Colorize depth frame to jet colormap
                depth_color_frame = colorizer.colorize(depth_frame)

                # Convert depth_frame to numpy array to render image in opencv
                depth_color_image = np.asanyarray(depth_color_frame.get_data())

                # Render image in opencv window
                cv2.imshow("Depth Stream", depth_color_image)
                key = cv2.waitKey(1)
                # if pressed escape exit program
                if key == 27:
                    cv2.destroyAllWindows()
                    return final_depth, final_rgb, self.pc