    
import pyrealsense2 as rs
import numpy as np
import cv2


class Frame_Capture:
   
    def __init__ (self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()



    def get_and_configure_device (self, high):
        
        if(high<2):
            pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
            pipeline_profile = self.config.resolve(pipeline_wrapper)
            device = pipeline_profile.get_device()
            device_product_line = str(device.get_info(rs.camera_info.product_line))

            found_rgb = False
            for s in device.sensors:
                if s.get_info(rs.camera_info.name) == 'RGB Camera':
                    found_rgb = True
                    break
            if not found_rgb:
                print("The demo requires Depth camera with Color sensor")
                exit(0)

            self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

            if device_product_line == 'L500':
                self.config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
            else:
                self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        
        
        else :
            self.config.enable_device('017322075378')
            self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
            self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
            self.config.enable_stream(rs.stream.accel)
            self.config.enable_stream(rs.stream.gyro)
        

    def capture (self, frames ,filename, high):

        self.config.enable_record_to_file(filename)
        
        # Start streaming
        pipe_profile = self.pipeline.start(self.config)

        if(high>2):
            depth_sensor = pipe_profile.get_device().first_depth_sensor()

            #Activem High Accuracy Mode (3); High Density (4)
            visualpreset = depth_sensor.get_option_value_description(rs.option.visual_preset,4)
            depth_sensor.set_option(rs.option.visual_preset, 4)
            
        # rs.recorder() #Start recording
        try:
            for i in range(frames):

                # Wait for a coherent pair of frames: depth and color
                frames = self.pipeline.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                if not depth_frame or not color_frame:
                    continue

                # Convert images to numpy arrays
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())

                if(i==10):
                    fin_depth_image = depth_image
                    fin_color_image = color_image

                # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

                depth_colormap_dim = depth_colormap.shape
                color_colormap_dim = color_image.shape

                # If depth and color resolutions are different, resize color image to match depth image for display
                if depth_colormap_dim != color_colormap_dim:
                    resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
                    images = np.hstack((resized_color_image, depth_colormap))
                else:
                    images = np.hstack((color_image, depth_colormap))

                # Show images
                cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
                cv2.imshow('RealSense', images)
                cv2.waitKey(1)

        finally:
            # Stop streaming
            self.pipeline.stop()
            return fin_depth_image,fin_color_image
            