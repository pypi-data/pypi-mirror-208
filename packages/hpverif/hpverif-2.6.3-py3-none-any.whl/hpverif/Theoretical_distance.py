import matplotlib.pyplot as plt
import numpy as np
import math
import ast

class Theoretical_distance:

    def __init__ (self):
        pass

    def theoric_distance(self, mapa, point, angle_degrees, show):
        #Carreguem mapa
        lines = self.loadMap(mapa)

        # Definim posició i angles (graus)
        #point, angle_degrees = (150, 100), 30

        #Ample de visió de la càmara d435i
        angle_FOV = 86/2

        #Calculem distancia central
        dist, interseccio_paret = self.distancia_propera(point, angle_degrees, lines)

        #Camp de visió càmara
        FOV_right, interseccio_paret_right = self.distancia_propera(point, angle_degrees - angle_FOV, lines)
        FOV_left, interseccio_paret_left = self.distancia_propera(point, angle_degrees + angle_FOV, lines)

        angles = array = np.arange(-angle_FOV, angle_FOV, 0.5)
        scalar_angles = [math.radians(angle) for angle in angles]

        d = []                          #Vector de distancies
        interseccio_paret_aa = []       #Vector de les interseccions
        distancia_max = 0               #inicialitzacio pel calcul de la distancia max
        distancia_min_c = 1500          #inicialitzacio pel calcul de la distancia min
        cares_columna = 0               #Indica el nombre de cares d'una columna que veu la camara
        estam_veiem_columna = False     #boolean que indica si en quin moment s'esta observant la columna dintra de la iteracio 
        index_columna_final = -1        #inicialitzacio per a la distancia de la columna
        index_columna_inici = -1        #idem
        index_min_c = 1500
        hem_estat_columna = False

        for i in range(len(scalar_angles)):
            distancia, interseccio = self.distancia_propera(point, angle_degrees + angles[i], lines)
            distancia = distancia*math.cos(scalar_angles[i])
            #print(i,distancia, angles[i])
            d.append(distancia)
            interseccio_paret_aa.append(interseccio)
            if distancia > distancia_max: #Guardem el valor i index de la distancia maxima i per tant, cantonada
                index_max = i-1
                distancia_max = distancia

            if abs(distancia-d[i-1]) > 10: #Si hi ha salts de valors "grans" significa que la camara veu una columna
                if not estam_veiem_columna: 
                    print("entrem de la columna",i)
                    index_columna_inici = i
                    estam_veiem_columna = True
                    hem_estat_columna = True
        
                else:
                    print("sortim de la columna",i)
                    index_columna_final = i-1
                    estam_veiem_columna = False

            if distancia < distancia_min_c and estam_veiem_columna: #Veiem la cantonada de la columna
                index_min_c = i
                distancia_min_c = distancia

        #La columna es recte, per tant si el valor maxim esta al principi o al final, ja sabem que la camara no veu
        #cap cantonada, en el cas que el maxim no coincideixi amb inici o final, sabem que hi haura una cantonada
        #si hi ha cantonada sabem que la camara veu dues cares de la columna
        if hem_estat_columna:
            if abs(distancia_min_c-d[index_columna_inici]) < 0.01 or abs(distancia_min_c-d[index_columna_final]) < 0.01:
                cares_columna = 1
            else:
                cares_columna = 2

        plt.plot(angles,d)
        plt.xlabel("Degrees")
        plt.ylabel("Distancia")  

        #print(distancia_max,angles_distancia_max, index_max)

        
        #La paret es recte, per tant si el valor maxim esta al principi o al final, ja sabem que no topem cap cantonada
        #En el cas que el maxim no coincideixi amb inici o final, sabem que hi haura una cantonada

        if(abs(distancia_max-d[0]) < 0.01 or abs(distancia_max-d[len(scalar_angles)-1]) < 0.01):
            veiem_cantonada = False
        else:
            veiem_cantonada = True

        #--------------------< CALCUL DE LES DISTANCIES FINALS >--------------------

        print("cares columna", cares_columna)

        if cares_columna == 0:
            if not veiem_cantonada: 
                print("Veiem una paret")

                #Distancia mitja de la paret
                dist = sum(d) / len(d)

            else:
                print("Veiem cantonada (dues parets)")
                mean_1_np = np.mean(d[:index_max-1],dtype=np.float64)
                mean_2_np = np.mean(d[index_max:],dtype=np.float64)

                #Distacia mitja de les dues parets
                dist = [mean_1_np, mean_2_np]

        elif cares_columna == 1:

            mean_columna = np.mean(d[index_columna_inici:index_columna_final-1],dtype=np.float64)
            mean_paret_1 = np.mean(d[:index_columna_inici-1],dtype=np.float64)
            mean_paret_2 = np.mean(d[index_columna_final+1:],dtype=np.float64)

            #Distancia mitja de la de la columna i la dels dos trossos de paret
            dist = [mean_columna, mean_paret_1, mean_paret_2]

        elif cares_columna == 2:
            print("Veiem columna amb dues cares")

            mean_columna_a = np.mean(d[index_columna_inici:index_min_c-1],dtype=np.float64)
            mean_columna_b = np.mean(d[index_min_c:index_columna_final-1],dtype=np.float64)
            mean_paret_1 = np.mean(d[:index_columna_inici],dtype=np.float64)
            mean_paret_2 = np.mean(d[index_columna_final+1:],dtype=np.float64)

            #Distancia mitja de les dues cares (a i b) de la columna i la dels dos trossos de paret
            dist = [mean_columna_a,mean_columna_b, mean_paret_1, mean_paret_2]




        #--------------------< REPRESENTACIÓ >--------------------
        if(show):
            #Creem mapa
            fig, ax = plt.subplots()
            # Setejem la nostra posició
            ax.scatter(point[0],point[1], label=f'Camera location: {(point[0], point[1])}' + ' cm.', color='blue', marker='o', s=30)
            # Graficar mapa
            for i in range(len(lines)):
                x1, y1 = lines[i][0][0], lines[i][0][1]
                x2, y2 = lines[i][1][0], lines[i][1][1]
                ax.plot([x1, x2], [y1, y2], 'k-')

            #Mostrem distancia  
            #ax.plot([point[0],interseccio_paret[0]], [point[1],interseccio_paret[1]], 'g-', label=f'Central distance: {round(dist, 3)}' + ' cm.')
            ax.scatter(point[0],point[1], label=f'Distance to object: {round(dist[0])}' + ' cm.', color='green', marker='o', s=30)

            #Mostrem rang de visió de la càmara
            ax.plot([point[0],interseccio_paret_right[0]], [point[1],interseccio_paret_right[1]], 'r-', label=f'Field of view.')
            ax.plot([point[0],interseccio_paret_left[0]], [point[1],interseccio_paret_left[1]], 'r-')

            ax.legend(loc='upper left')

            #Redimensionar finestra
            ax.set_aspect('equal')

            plt.title('Distance between HP SitePrint and the objective')
            plt.xlabel('X Axis (cm)')
            plt.ylabel('Y Axis (cm)')

            #Establim valor de la distància teòrica
            #plt.text(interseccio_paret[0], interseccio_paret[1], f"{round(dist, 3)}" + " cm", ha='right', va='bottom')
            plt.text(point[0], point[1], f"{(point[0], point[1])}" + " cm  ", ha='right', va='bottom')


            plt.show()

        return dist
    
    def line_intersection(self, line1, line2):
        x1, y1 = line1[0]
        x2, y2 = line1[1]
        x3, y3 = line2[0]
        x4, y4 = line2[1]
        det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        if det == 0:
            return (-1,-1) #si no hi ha interseccio
        else:
            px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / det
            py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / det
            if (x1-1 <= px<= x2+1 or x1+1>=px>=x2-1)and(y1-1<=py<=y2+1 or y1+1>=py>=y2-1) and (x3-1 <= px <= x4+1 or x3+1>=px>=x4-1)and(y3-1<=py<=y4+1 or y3+1>=py>=y4-1):
                return (px, py)
            else:
                return(-1,-1)

    def distance_between_points(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def loadMap(self, map_name):
        if '.txt' in map_name:
            map_name = map_name.replace(".txt", "")
        with open(map_name + '.txt', 'r') as file:
            lines = file.readlines()
            #Assignem a un vector els valors de archiu
            lines_strip = [line.strip() for line in lines]
            #Separem les coordenades dels punts per poder-hi accedir posteriorment
            lines_clean = [ast.literal_eval(linea) for linea in lines_strip]
            
            return lines_clean
        
    def distancia_propera(self, point, angle_degrees, lines):  

        # Convert the angle to radians
        angle_radians = (angle_degrees*math.pi)/180

        # Calculate the coordinates of the end point of the ray
        dx = 1000 * math.cos(angle_radians)
        dy = 1000 * math.sin(angle_radians)
        ray_end = (point[0] + dx, point[1] + dy)

        # Check which line the ray intersects with
        intersection_points = []
        for line in lines:
            intersection_point = self.line_intersection((point, ray_end), line)
            
            if intersection_point[0] >= 0 and intersection_point[1] >= 0:
                intersection_points.append(intersection_point)

        # Find the closest intersection point to the point
        closest_intersection_point = None
        closest_distance = float("inf")
        for p in intersection_points:
            distance = self.distance_between_points(p, point)
            if distance < closest_distance:
                closest_intersection_point = p
                closest_distance = distance

        return(closest_distance, closest_intersection_point)