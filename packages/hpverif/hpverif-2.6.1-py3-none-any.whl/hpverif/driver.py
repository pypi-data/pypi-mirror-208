import Verification  as v



verif = v.Verification()
#dp,dc = verif.capture_frame(100, "prueba3m.bag", 0)


       
dp,dc,p = verif.show_files(26,'prueba_estatica2.bag')
min,max,fact= verif.pointCloud(dp,'prueba_estatica2')

dist1,dist2,dist3=verif.segmentation("./prueba_estatica2/prueba_estatica2.ply",min,max, fact)

print(".................")
print(dist1)
print(dist2)
print(dist3)


