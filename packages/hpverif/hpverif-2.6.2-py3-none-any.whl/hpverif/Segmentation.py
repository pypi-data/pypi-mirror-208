import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import math


class Segmentation:

    def __init__(self,filename,min,max,fact) :
        self.pcd =   o3d.io.read_point_cloud(filename)
        #pcd =self.pcd.voxel_down_sample(voxel_size=0.02)  #down sampling por si imagen muy compleja
        self.pcd.remove_statistical_outlier(nb_neighbors= 10, std_ratio=2.0)
        o3d.visualization.draw_geometries([self.pcd]) 
        self.min = min
        self.max = max
        self.fact = fact
        #pcd.remove_radius_outlier(nb_points=16, radius=0.05) # esta eliminacion tarda mucho si la imagen tiene muchos puntos


    def planeSegmentation(self):
        
        if ((self.max-self.min) > 1):
            rest = 0.035 
        else :
            rest= 0.02

        plane_model, inliers = self.pcd.segment_plane(distance_threshold=(((rest - self.min) / self.max)*self.fact), ransac_n=3,num_iterations=1000) #0.02. El q funcionaba bien era 0.008 #3
        [a, b, c, d] = plane_model
        print(f"Plane equation: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0")
        theta = (math.acos(abs(c) / math.sqrt(a**2 + b**2 + c**2)))*180/math.pi
        print(f"Plane orientation:{theta:.2f}")
        inlier_cloud = self.pcd.select_by_index(inliers)
        inlier_cloud.paint_uniform_color([1.0, 0, 0])
        outlier_cloud = self.pcd.select_by_index(inliers, invert=True)     
        o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])  
        self.pcd = outlier_cloud

        depth_values_plane= np.asarray(inlier_cloud.points)[:,2] 
        depth_value_plane= ((np.mean(depth_values_plane)/self.fact)*self.max)+self.min
        print("Background Plane Distance: " + str(depth_value_plane))


        plane_model, inliers = self.pcd.segment_plane(distance_threshold=(((0.015 - self.min) / self.max)*self.fact), ransac_n=3,num_iterations=1000) #2.8
        [a, b, c, d] = plane_model
        print(f"Plane equation: {a:.2f}x + {b:.2f}y + {c:.2f}z + {d:.2f} = 0")
        inlier_cloud = self.pcd.select_by_index(inliers)
        outlier_cloud = self.pcd.select_by_index(inliers, invert=True) 
        inlier_cloud.paint_uniform_color([1.0, 0, 0])
        outlier_cloud.paint_uniform_color([1.0, 0, 0])
        o3d.visualization.draw_geometries([inlier_cloud]) 
        o3d.visualization.draw_geometries([outlier_cloud]) 
        self.pcd = outlier_cloud

        depth_values_obj= np.asarray(inlier_cloud.points)[:,2]
        varianza = np.var(depth_values_obj)
        print("Variance of second Detection: " +str(varianza))

        segment = 0
        depth_value_obj= ((np.mean(depth_values_obj)/self.fact)*self.max)+self.min
        if(varianza <100):
            print("Distance to Object: " + str(depth_value_obj))
        else:
            segment=1
            print("DIstance to Floor " + str(depth_value_obj))

        return depth_value_plane,depth_value_obj, segment

        



    def segmentation(self):   

        with o3d.utility.VerbosityContextManager(
            o3d.utility.VerbosityLevel.Debug) as cm:
            labels = np.array(
                self.pcd.cluster_dbscan(eps=(((0.03 - self.min) / self.max)*self.fact), min_points=50, print_progress=True)) # inclinado: 3.2, y min_p=50.     1.8

        max_label = labels.max()
        print(f"point cloud has {max_label + 1} clusters")
        colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
        colors[labels < 0] = 0
        self.pcd.colors = o3d.utility.Vector3dVector(colors[:, :3])
        o3d.visualization.draw_geometries([self.pcd])


    
        #Buscamos la region que nos interesa
        target_label= 0
        selected_indices = np.where(labels == target_label)[0]
        selected_pcd = self.pcd.select_by_index(selected_indices)
        max_pcd= selected_pcd


        for i in range(max_label):
            target_label = i
            if(target_label> 0):
                selected_indices = np.where(labels == target_label)[0]
                selected_pcd = self.pcd.select_by_index(selected_indices)

                if(i==1):
                    max2_pcd= selected_pcd
            
                if( len(selected_pcd.points) > len(max2_pcd.points) ):
                    max2_pcd = selected_pcd

                if( len(selected_pcd.points)> len(max_pcd.points)):  # np.asarray(selected_pcd.points).size> np.asarray(max_pcd.points).size
                    max2_pcd = max_pcd
                    max_pcd= selected_pcd
                
        o3d.visualization.draw_geometries([max_pcd])
        o3d.visualization.draw_geometries([max2_pcd])
        max_points = np.asarray(max_pcd.points)
        max_points2 = np.asarray(max2_pcd.points)

        print("varianza:" + str(np.var(max_points2[:,2])))

        print("varianza:" + str(np.var(max_points[:,2])))

        ''' 
        if( (np.var(max_points[:,2]) <= np.var(max_points[:,2]) +1.2*np.var(max_points2[:,2]))):
            pcd_final = max_pcd
        elif(np.var(max_points2[:,2])<0.8*np.var(max_points[:,2]) ):
            pcd_final = max2_pcd
        else:
            pcd_final= max_pcd
        '''
        if(np.var(max_points2[:,2])<np.var(max_points2[:,2])):
            pcd_final=max2_pcd
        else:
            pcd_final=max_pcd


        o3d.visualization.draw_geometries([pcd_final])

        depth_values_obj= np.asarray(pcd_final.points)[:,2] 
        depth_value_plane= ((np.mean(depth_values_obj)/self.fact)*self.max)+self.min
        print("distancia objeto inclinado: " + str(depth_value_plane))
        return depth_value_plane