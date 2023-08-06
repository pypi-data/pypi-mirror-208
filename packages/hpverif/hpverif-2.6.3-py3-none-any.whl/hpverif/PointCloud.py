import open3d as o3d
import cv2
import numpy as np
import os 
import imageio.v3 as iio

class PointCloud:

    def __init__(self) -> None:
        pass

    
    def createPointCloud (self, depthframe, filename):


      
      
        
        os.makedirs(filename, exist_ok=True)
        

        # Load the depth frame as a 16-bit grayscale image
        depth_image = np.array(depthframe)
        height, width = depth_image.shape
        min =  np.min(depth_image)
        max =  np.max(depth_image)
        print("max:"+str(max) +"  min:"+ str(min))
        depth_frame_norm=0
        fact=0
        # Normalize the depth values between 0 and 255
        print(height,width)
        '''
        if((max-min)>=0.50 and (max-min)<0.60):

            depth_frame_norm = (((depth_image - min) / max)*100) #225,2048,1024
        if((max-min)>=0.60 and (max-min)<0.70):

            depth_frame_norm = (((depth_image - min) / max)*100) #225,2048,1024    

        if((max-min)>=0.70 and (max-min)<0.80):

            depth_frame_norm = (((depth_image - min) / max)*120) #225,2048,1024

        if((max-min)>=0.80 and (max-min)<1):

            depth_frame_norm = (((depth_image - min) / max)*150) #225,2048,1024
    '''
        if((max-min)>=0.1 and (max-min)<1):

            depth_frame_norm = (((depth_image - min) / max)*100) #225,2048,1024
            fact = 100
        if((max-min)>=1):

            depth_frame_norm = (((depth_image - min) / max)*200) #225,2048,1024
            fact = 200
        print (depth_image [320][400])
        # Convert the depth frame to a color map
        

        # Save the depth map as a PNG image
        cv2.imwrite("./"+filename + "/"+filename+'.png', depth_frame_norm)

        '''    
        depth_image = cv2.imread("./"+filename + "/"+filename+'.png',cv2.IMREAD_ANYDEPTH)
        print(depth_image)
        hole_mask = depth_image == 0
        cv2.imwrite("./"+filename + "/"+filename+'_mask.png', hole_mask.astype(np.uint8)*255)

        # Apply the inpainting algorithm
        filled_depth = cv2.inpaint(depth_image, hole_mask.astype(np.uint8), 5, cv2.INPAINT_TELEA)

        # Save the filled depth frame
        cv2.imwrite("./"+filename + "/"+filename+ '_filled.png', filled_depth)
        
       #depth_image = filled_depth.astype(np.uint16)
        
        #depth_o3d = o3d.geometry.Image(depth_image)
'''
       # print(depth_o3d)
        depth_image = iio.imread("./"+filename + "/"+filename+ '.png')
        
        
        '''
        # Create a depth image from the numpy array

        intrinsic = o3d.camera.PinholeCameraIntrinsic(640, 480, 616.962, 616.962, 329.215, 237.106)
        im = o3d.geometry.PointCloud.create_from_depth_image(depth_o3d,intrinsic)
        '''
        CX_DEPTH=322.282 # 322.282
        CY_DEPTH = 322.282

        FX_DEPTH=320.818 #320.818
        FY_DEPTH=178.779 #178.779

        pcd = []
        height, width = depth_image.shape
        for i in range(height):
            for j in range(width):
                z = depth_image[i][j]
                x = (j - CX_DEPTH) * z / FX_DEPTH
                y = (i - CY_DEPTH) * z / FY_DEPTH
                pcd.append([x, y, z])
        '''        
        for i in range (100):
             k=i
             
             if (i<200):
                
                pcd.append([0, 0, 2*i])
             for j in range(100):
                 t=j
                 if(i%2):
                     k= i*(-1)
                 if(j%2):
                     t= j*(-1)
                 pcd.append([k, t, 0])
       '''

        pcd_o3d = o3d.geometry.PointCloud()  # create point cloud object
        pcd_o3d.points = o3d.utility.Vector3dVector(pcd)  # set pcd_np as the point cloud points
        # Visualize:
        o3d.visualization.draw_geometries([pcd_o3d])
        
    
        #s = verif.matrixDiagn(dp)

        o3d.io.write_point_cloud("./"+filename + "/"+filename+".ply", pcd_o3d)
        return min,max, fact






