    
import pyrealsense2 as rs



class Frame_Capture_PLY:
   
    def __init__ (self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.points = rs.points()
        self.spatial = rs.spatial_filter()
        self.temporal = rs.temporal_filter()
        self.hole_filling = rs.hole_filling_filter()


    def get_and_configure_device (self):

        self.config.enable_device('017322075378')
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.accel)
        self.config.enable_stream(rs.stream.gyro)
        self.spatial.set_option(rs.option.filter_magnitude, 2)
        self.spatial.set_option(rs.option.filter_smooth_alpha, 0.5)
        self.spatial.set_option(rs.option.filter_smooth_delta, 20)

    def capture (self,filename, high):

        

        # Start streaming with chosen configuration
        pipe_profile = self.pipeline.start(self.config)

        if(high>2):
            depth_sensor = pipe_profile.get_device().first_depth_sensor()

            #Activem High Accuracy Mode (3); High Density (4)
            visualpreset = depth_sensor.get_option_value_description(rs.option.visual_preset,4)
            depth_sensor.set_option(rs.option.visual_preset, 4)
        # We'll use the colorizer to generate texture for our PLY
        # (alternatively, texture can be obtained from color or infrared stream)
        colorizer = rs.colorizer()

        try:
            # Wait for the next set of frames from the camera
            frames = self.pipeline.wait_for_frames()
            colorized = colorizer.process(frames)
            depth = frames.get_depth_frame()
            depth = self.temporal.process(depth)
            depth = self.spatial.process(depth)
            color = frames.get_color_frame()
            # Create save_to_ply object
            ply = rs.save_to_ply(filename+ ".ply")
            # Set options to the desired values
            # In this example we'll generate a textual PLY with normals (mesh is already created by default)
            ply.set_option(rs.save_to_ply.option_ply_binary, False)
            ply.set_option(rs.save_to_ply.option_ply_normals, True)

            print("Saving to 1.ply...")
            # Apply the processing block to the frameset which contains the depth frame and the texture
            ply.process(colorized)
            print("Done")
        finally:
            self.pipeline.stop()
                    