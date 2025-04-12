
PATH_TRAIN = r'C:\Users\AnTrAx\Desktop\INFORMATICA\Taller 1\2. Anotaciones\data\images\train'
PATH_VAL   = r'C:\Users\AnTrAx\Desktop\INFORMATICA\Taller 1\2. Anotaciones\data\images\val'
PATH_TEST  = r'C:\Users\AnTrAx\Desktop\INFORMATICA\Taller 1\2. Anotaciones\data\images\test'
N_CLASSES  = 4 # 0: fecha, 1: numero de serie, 2: comprador, 3: detalle

class_names = ['date','nro', 'user', 'datail']


f = open('data/data.yaml','w+')

f.write('train: '+PATH_TRAIN+'\n')
f.write('val:   '+PATH_VAL+'\n')
f.write('test:  '+PATH_TEST+'\n')
f.write('nc:  '+str(N_CLASSES)+'\n')
f.write('names:  '+str(class_names)+'\n')

f.close()