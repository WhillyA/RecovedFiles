import pandas as pd
import glob
import os
import cv2
from config import raiz, raiz2, image_folder
# Cargar datos desde el archivo CSV
csv_data = pd.read_csv('boundingbox_P3X.csv')

image_data = glob.glob(os.path.join(image_folder, '*.jpg'))

# Extraer solo los nombres de los archivos desde el CSV
csv_files = set(csv_data['File'])  # Asegúrate de que 'File' es el nombre correcto de la columna en tu CSV

# Extraer solo los nombres de los archivos de la carpeta de imágenes
image_files = set(os.path.basename(img) for img in image_data)

# Encontrar diferencias
missing_in_csv = image_files - csv_files  # Imágenes que no están en el CSV
missing_in_images = csv_files - image_files  # Archivos del CSV que no están en la carpeta de imágenes



from tqdm.auto import tqdm
csv_len=len(csv_data)
image_len=len(image_data)

for i in tqdm(range(image_len)):
    fname = os.path.basename(image_data[i])
    X= cv2.imread(raiz+'\\'+fname)
    alto = X.shape[0]
    ancho = X.shape[1]
    ok = 0
    c=0
    wn=hn=xn=yn =0.0
    for  k in range(csv_len):
        tnfame = fname[:-4] + '.txt'
        if raiz+"\\"+csv_data['File'].iloc[k] == raiz+"\\"+fname: 
            f = open(raiz2+"\\"+tnfame,'w+')
        
        #print (raiz+"\\"+csv_data['File'].iloc[k] == fname)
        for zz in range(4):
            if raiz+"\\"+csv_data['File'].iloc[k] == raiz+"\\"+fname:
                x1 = csv_data['x1_' + str(zz+1)].iloc[k]
                y1 = csv_data['y1_'+ str(zz+1)].iloc[k]
                x2 = csv_data['x2_'+ str(zz+1)].iloc[k]
                y2 = csv_data['y2_'+ str(zz+1)].iloc[k]
                c = csv_data['c_'+ str(zz+1)].iloc[k]
                wn = float(abs(x2-x1))/ancho
                hn = float(abs(y2-y1))/alto
                xn = (x1+x2)/float(2.0*ancho)
                yn = (y1+y2)/float(2.0*alto)
                
                
                
                if pd.notna(x1) and pd.notna(x2)and pd.notna(y2)and pd.notna(y1):
                    f = open(raiz2+"\\"+tnfame,'a')
                    f.write(str(c)+' '+str(xn)+' '+str(yn)+' '+str(wn)+' '+str(hn)+'\n')
    if ok:
        f.close()
    
print("Imágenes sin datos en CSV:", missing_in_csv)
print("Datos en CSV sin imagen correspondiente:", missing_in_images)