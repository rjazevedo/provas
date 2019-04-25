import pyift.pyift as ift
import sys


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(sys.argv[0]+" <imagem de entrada (jpg,png,pgm)>  <imagem de saida (jpg,png,pgm)>")
    else:        
        img = ift.ReadImageByExt(sys.argv[1])
        A   = ift.Rectangular(4,4)
        img = ift.MeanFilter(img,A)
        A   = ift.Rectangular(2,2)
        img = ift.Erode(img,A,None)
        img = ift.Threshold(img,0,220,255)
        img = ift.Complement(img)
        img = ift.Dilate(img,A,None)
        ift.WriteImageByExt(img,sys.argv[2])
