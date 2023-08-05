import subprocess
subprocess.run(['pip', 'install', '--upgrade', 'sb6'], check=False)

def pg1():
    print(r"""
import cv2
img = cv2.imread('lena.tiff')
height = img.shape[0]
width = img.shape[1]
width_cutoff = width // 2
left1 = img[:,:width_cutoff]
right1 = img[:,width_cutoff:]
img = cv2.rotate(left1,cv2.ROTATE_90_CLOCKWISE)
height = img.shape[0]
width = img.shape[1]
width_cutoff = width // 2
l2 = img[:,:width_cutoff]
l1 = img[:,width_cutoff:]
l2 = cv2.rotate(l2,cv2.ROTATE_90_COUNTERCLOCKWISE)
cv2.imwrite('lena_2.tiff',l2)
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
img = Image.open('lena_2.tiff')
I1 = ImageDraw.Draw(img)
myFont = ImageFont.truetype('Arial.ttf',25);
I1.text((10,10),"2nd Quadrant",font=myFont,fill=(255,0,0))
img.show()
img.save('lena_2.tiff')
l1 = cv2.rotate(l1,cv2.ROTATE_90_COUNTERCLOCKWISE)
cv2.imwrite('lena_1.tiff',l1)
img = Image.open('lena_1.tiff')
I1 = ImageDraw.Draw(img)
myFont = ImageFont.truetype('Arial.ttf',25);
I1.text((10,10),"1st Quadrant",font=myFont,fill=(255,0,0))
img.show()
img.save('lena_1.tiff')
img = cv2.rotate(right1,cv2.ROTATE_90_CLOCKWISE)
height = img.shape[0]
width = img.shape[1]
width_cutoff = width // 2
r4 = img[:,:width_cutoff]
r3 = img[:,width_cutoff:]
r4 = cv2.rotate(r4,cv2.ROTATE_90_COUNTERCLOCKWISE)
cv2.imwrite('lena_4.tiff',r4)
img = Image.open('lena_4.tiff')
I1 = ImageDraw.Draw(img)
myFont = ImageFont.truetype('Arial.ttf',25);
I1.text((10,10),"4th Quadrant",font=myFont,fill=(255,0,0))
img.show()
img.save('lena_4.tiff')
r3 = cv2.rotate(r3,cv2.ROTATE_90_COUNTERCLOCKWISE)
cv2.imwrite('lena_3.tiff',r3)
img = Image.open('lena_3.tiff')
I1 = ImageDraw.Draw(img)
myFont = ImageFont.truetype('Arial.ttf',25);
I1.text((10,10),"3rd Quadrant",font=myFont,fill=(255,0,0))
img.show()
img.save('lena_3.tiff')
img = cv2.imread('lena.tiff')
height = img.shape[0]
width = img.shape[1]
width_cutoff = width // 2
left1 = img[:,:width_cutoff]
rigth1 = img[:,width_cutoff:]
cv2.imwrite('lena_left.tiff',left1)
cv2.imshow('lena_left.tiff',left1)
cv2.imwrite('lena_right.tiff',right1)
cv2.imshow('lena_right.tiff',right1)
image = cv2.imread('lena.tiff')
height,width,channels = image.shape
half_height = height//2
top_section = image[:half_height,:]
bottom_section = image[half_height:,:]
cv2.imshow('lena_top',top_section)
cv2.imshow('lena_bottom',bottom_section)
cv2.imwrite('lena_top.tiff',top_section)
cv2.imwrite('lena_bottom.tiff',bottom_section)
cv2.waitKey(0)
    """)
    
def pg2():
    print(r"""
import cv2
import numpy as np
try:
    img = cv2.imread('camaraman.png')
    (rows,cols)=img.shape[:2]
    M = cv2.getRotationMatrix2D((cols/2,rows/2),45,1)
    rotation = cv2.warpAffine(img,M,(cols,rows))
    cv2.imwrite('rotation.png',rotation)
    cv2.imshow('rotation',rotation)
    img_scaled = cv2.resize(img,None,fx=1.2,fy=1.2,interpolation = cv2.INTER_LINEAR)
    cv2.imshow('Scaling - linear interpolation',img_scaled)
    cv2.imwrite('Scaling - linear interpolation.png',img_scaled)
    img_scaled = cv2.resize(img,None,fx=1.2,fy=1.2,interpolation = cv2.INTER_CUBIC)
    cv2.imshow('Scaling - Cubic interpolation',img_scaled)
    cv2.imwrite('Scaling - Cubic interpolation.png',img_scaled)
    img_scaled = cv2.resize(img,(600,600),interpolation = cv2.INTER_AREA)
    cv2.imshow('Scaling - Skewed Size',img_scaled)
    cv2.imwrite('Scaling - Skewed Size.png',img_scaled)
    img_translation = cv2.warpAffine(img,M,(cols,rows))
    cv2.imwrite('translation.png',img_translation)
    cv2.imshow('translation',img_translation)
    cv2.waitKey()
except IOError:
	print('Error while readning files !!!')
    """)
    
def pg3():
    print(r"""
import cv2
import numpy as np
img = cv2.imread('lena.png')
kernel = np.ones((5,5),np.uint8)
threshold_lower = 100
threshold_upper = 200
edges = cv2.Canny(img,threshold_lower,threshold_upper)
img_erosion = cv2.erode(img, kernel, iterations=1)
img_dilation = cv2.dilate(img, kernel, iterations=1)
cv2.imshow('Image',img)
cv2.imshow('Erosion',img_erosion)
cv2.imshow('Dilation',img_dilation)
cv2.imwrite('Image.png',img)
cv2.imwrite('Erosion.png',img_erosion)
cv2.imwrite('Dilation.png',img_dilation)
erosion_edges = cv2.erode(edges, kernel, iterations=1)
dilation_edge = cv2.dilate(edges, kernel, iterations=1)
cv2.imshow('Edge image using Erosion',erosion_edges)
cv2.imshow('Edge image using Dilation',dilation_edge)
#cv2.imwrite('Edge image using Erosion.png',erosion_edges)
cv2.imwrite('Edge image using Dilation.png',dilation_edge)
result = cv2.subtract(img,img_erosion)
cv2.imshow('result after subtraction',result)
cv2.imwrite('result after subtraction.png',result)
cv2.waitKey(0)
cv2.destroyAllWindows()
    """)
    
def pg4():
    print(r"""
import cv2
import numpy as np
img = cv2.imread('lena.png')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
cv2.imshow('gray scale image',gray)
blur = cv2.GaussianBlur(gray, (5,5), cv2.BORDER_DEFAULT)
sobelx = cv2.Sobel(blur, cv2.CV_64F, 1, 0, ksize=5)
sobely = cv2.Sobel(blur, cv2.CV_64F, 0, 1, ksize=5)
sobel_edges = cv2.addWeighted(sobelx,0.5,sobely,0.5,0)
laplacian = cv2.Laplacian(blur, cv2.CV_64F) 
canny_edges = cv2.Canny(blur, 100, 200) 
blur_median = cv2.medianBlur(gray,5)
cv2.imshow('Blur Median',blur_median)
cv2.imshow('Filtered output',blur)
cv2.imshow('Sobel Edges',sobel_edges)
cv2.imshow('laplacian',laplacian)
cv2.imshow('Canny Edge detection',canny_edges)
bilateral = cv2.bilateralFilter(gray,15,75,75)
ksize = 31
sigma = 5
theta = 0
lambda = 10
gamma = 0.5
phi = 0
kernel = cv2.getGaborKernel((ksize,ksize),sigma,theta,lambda,gamma,phi,ktype=cv2.CV_32F)
gabor = cv2.filter2D(gray,cv2.CV_8UC3,kernel)
cv2.imshow('Bilateral Filter',bilateral)
cv2.imshow('Gabor Filter',gabor)
cv2.waitKey(0)
cv2.destroyAllWindows()
    """)
    
def pg5():
    print(r"""
import cv2
import numpy as np
img = cv2.imread('lena.png')
img_g = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
img_equalize = cv2.equalizeHist(img_g)
result = np.hstack((img_g,img_equalize))
ret,img_thresh = cv2.threshold(img_equalize,0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)
cv2.imshow('Original Image',img)
cv2.imshow('Original Image Converted to grayscale',img_g)
cv2.imshow('Enhanced Image',img_equalize)
cv2.imshow('Original Image & Enhanced Image',result)
cv2.imshow('Segmented Image',img_thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
    """)