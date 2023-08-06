def read_access_display():
    s="""img= imread ('D:\flower.jpg');
figure;
title('Original image')
imshow(img);
img1=rgb2gray(a);
figure;
title('Grayscle image')
imshow(img1);"""
    return s
def sampling():
    s="""clc;
clear all;
close all;
n=8;
img = rgb2gray(imread('D:\flower.jpg'));
a=size(img);
w=a(2);
h=a(1);
im=zeros(100);
for i=1:n:h
for j=1:n:w
for k=0:n-1
for l=0:n-1
im(i+k,j+l)=img(i,j);
end
end
end
end
subplot(1,2,1);
imshow(uint8(img));title('Original Image');
subplot(1,2,2);
imshow(uint8(im));title('Sampled Image');"""
    return s
def neighbourhood_matrics():
    s="""
    I = rgb2gray(imread('D:\flower.jpg'));
I_noise=imnoise(I,'salt & pepper');
subplot(2,3,1);
title('original image')
imshow(I)
subplot(2,3,2);
title('noisy image')
imshow(I_noise)
flinear1=1/25*ones(5,5);
Ilinear1=imfilter(I_noise,flinear1);
subplot(2,3,3);
title('Linear average filtered ')
imshow(Ilinear1)
hsize=[5,5];
sigma=1;
flinear2=fspecial('gaussian',hsize,sigma );
Ilinear2=imfilter(I_noise,flinear2);
subplot(2,3,4);
title('Linear Gaussian Filtered')
imshow(Ilinear2)
fnonlinear=[3,3];
Inonlinear=immedian(I_noise,fnonlinear);
subplot(2,3,5);
title('Median Filtered(Non-Linear)')
imshow(Inonlinear)

    program2
    clc;
clear all;
close all;
I = rgb2gray(imread('D:\flower.jpg'));
I_noise=imnoise(I,'salt & pepper');
FilterSize = [3 3];
I_3x3 = immedian ( I_noise , FilterSize ) ;
I_5x5 = immedian ( I_noise ,[5 5]) ;
I_7x7 = immedian ( I_noise ,[7 7]) ;
I_9x9 = immedian ( I_noise ,[9 9]) ;
subplot(2,3,1);
title('original image')
imshow(I)
subplot(2,3,2);
title('noisy image')
imshow(I_noise)
subplot(2,3,3);
title('Filter size 3x3')
imshow(I_3x3)
subplot(2,3,4);
title('Filter size 5x5')
imshow(I_5x5)
subplot(2,3,5);

Downloaded by Monica Bhavani M (monicabm@srmist.edu.in)

lOMoARcPSD|20319323

title('Filter size 7x7')
imshow(I_7x7)
subplot(2,3,6);
title('Filter size 9x9')
imshow(I_9x9)"""
    return s
def image_enhancement():
    s="""clc ;
clear;
close;
img= imread ('D:\cameraman.jpg');
img=rgb2gray(img);
I =im2double(img) ;
J = imcomplement(I); // Image Negative
subplot(2,3,1);
title('Original Image');
imshow(img);
subplot(2,3,2);
title('Image Negative');
imshow(J);
gamma=1.5
k=I.^gamma; // Gamma Transformation
subplot(2,3,3);
title('Gamma transformation');
imshow(k);
contrast1=1./(1+(0.2./(I+%eps)).^4); // Contrast Enhancement
contrast2=1./(1+(0.5./(I+%eps)).^5);
contrast3=1./(1+(0.7./(I+%eps)).^10);
subplot(2,3,4),imshow(contrast1);title('Contrast enhancement 0.2');
subplot(2,3,5),imshow(contrast2);title('Contrast enhancement 0.5');
subplot(2,3,6),imshow(contrast3);title('Contrast enhancement 0.7');"""
    return s
def histogram():
    s="""Program 1:
clc ;
clear;
close;
img= imread ('D:\cameraman.jpg');
img=rgb2gray(img);
[count,cells ]= imhist (img); // compute histogram
subplot(2,2,1);
title('Original image');
imshow(img);
subplot(2,2,2);
plot2d3 ('gnn' , cells , count )
title('Histogram plot for original image');
Iheq = imhistequal(img);
[count,cells ]= imhist (Iheq); // compute histogram equalization
subplot(2,2,3);
title('Histogram Equalized image');
imshow(Iheq);
subplot(2,2,4);
plot2d3 ('gnn' , cells , count )
title('Histogram plot for histogram equalized image');




    Program 2:
clc ;
clear;
close;
img= imread ('D:\cameraman.jpg');
img=rgb2gray(img);
//I = imresize (img ,[256 ,256]) ;
[ count , cells ]= imhist (img) ;
Iheq = imhistequal(img);
[count1,cells1 ]= imhist (Iheq);
// correlation between original image and Histogram equalized image
corrbsameimg = corr2(img,Iheq)
disp(corrbsameimg);
// correlation between the histograms of original image
x = xcorr ( count , count ) ;
//correlation between the histogram of original image and equalized image
x1 = xcorr ( count , count1 ) ;
subplot(2,1,1);
plot2d3 ( 'gnn' ,1: length ( x ) ,x ,2);
title('correlation b/w histograms of original image');

Downloaded by Monica Bhavani M (monicabm@srmist.edu.in)

lOMoARcPSD|20319323

subplot(2,1,2);
plot2d3 ('gnn' ,1: length ( x1 ) ,x1 ,2);
title('correlation b/w histogram of original and equalized image')"""
    return s
def smoothing():
    s="""clc ;
close ;
a= imread( 'D:\flower.jpeg' );
subplot(2,3,1)
title('Original image');
imshow(a)
b= imresize(a ,[256 ,256]) ;
b= imnoise (b,'salt & pepper',0.1);
subplot(2,3,2)
title('noise image');
imshow(b)
[m n]= size (b);
R=b(: ,: ,1);
G=b(: ,: ,2);
B=b(: ,: ,3);
exec('D:\scilab-6.1.1\experiments\Func_medianall.sci')
Out_R = Func_medianall(R,N);
Out_G = Func_medianall(G,N);
Out_B = Func_medianall(B,N);
Out_Image (: ,: ,1)= Out_R ;
Out_Image (: ,: ,2)= Out_G ;
Out_Image (: ,: ,3)= Out_B ;
b = uint8 (b);
Out_Image = uint8(Out_Image);
subplot(2,3,3)
title( '3x3 median filtered' )
imshow(Out_Image)

Downloaded by Monica Bhavani M (monicabm@srmist.edu.in)

lOMoARcPSD|20319323

Function func_medianall
function [Out_Imag]=Func_medianall(a, N)
a= double (a);
[m n]= size (a);
Out_Imag =a;
if( modulo (N ,2) ==1)
Start =(N +1) /2;
End = Start ;
else
Start =N /2;
End = Start +1;
end
if( modulo (N ,2) ==1)
limit1 =(N -1) /2;
limit2 = limit1 ;
else
limit1 =(N/2) -1;
limit2 = limit1 +1;
end
for i= Start :(m-End +1) ,
for j= Start :(n-End +1) ,
I =1;
for k=- limit1 :limit2 ,
for l=- limit1 :limit2 ,
mat (I)=a(i+k,j+l);
I=I+1;
end
end
mat = gsort ( mat ); // So r t the e l eme n t s to
if( modulo (N ,2) ==1)
Out_Imag (i,j)=( mat ((( N ^2) +1) /2) );
else
Out_Imag (i,j)=( mat ((N ^2) /2)+ mat ((( N^2)/2)+1) ) /2;
end
end
end
endfunction"""
    return s
def thresholding():
    s="""RGB = imread ("D:\DSC\teaset.jfif");
Image = rgb2gray(RGB);
InvertedImage = uint8(255 * ones(size(Image,1), size(Image,2))) - Image;
Histogram=imhist(InvertedImage);
figure();plot(0:255, Histogram')
xgrid(color('black'),1,8)
LogicalImage = im2bw(InvertedImage, 100/255);
f1=scf(1);f1.name='Original Image';
imshow(Image);
f2=scf(2);f2.name='Inverted Image';
imshow(InvertedImage);
f3=scf(3);f3.name='Result of Thresholding';
imshow(LogicalImage);"""
    return s
def edge_detection():
    s="""close ;
clc ;
a = imread('D:\ImageProcessing\sunset.jfif');
a = rgb2gray (a);
c = edge (a, 'sobel' );
d = edge (a, 'prewitt');
e = edge (a, 'log' );
f = edge (a, 'canny' );
imshow(a)
title ('Original Image' )
figure
imshow(c)
title ( 'Sobel' )
figure
imshow(d)
title ( 'Prewitt' )
figure
imshow(e)
title ( ' Log ' )
figure
imshow(f)
title ( 'Canny ' )"""
    return s
def hough_transform():
    s="""I = imread('C:\SRM\SEM6\Image Processing\LabExercises\image6.png');
imshow(I)
title('original image')
figure
I =im2bw(double(I),0.5);
[y,x]=find(I);
[sy,sx]=size(I);
imshow(I);
title('binary image')
figure
totalpix = length(x);
HM = zeros(sy,sx);
R = 34;
R2 = R^2;
b = 1:sy;
for cnt = 1:totalpix
a = (round(x(cnt) - sqrt(R2 - (y(cnt) - [1:sy]).^2)));
for cnt2 =1:sy
if isreal(a(cnt2),0) & real(a(cnt2))>0
HM(cnt2,real(a(cnt2))) = HM(cnt2,real(a(cnt2))) + 1;
end
end
end
[maxval, maxind] = max(max(HM));
[B,A] = find(HM==maxval);
imshow(double(I));
title('Hough transform')
figure
mtlb_hold on;
plot(mean(A),sy-mean(B),'rx');"""
    return s
def feature_extraction():
    s="""clc
clear;
close;
S= imread ("D:\ImageProcessing\nift.jpg");
fobj = imdetect_FAST(S);
title("Extracted image");
imshow(S);
plotfeature( fobj );"""
    return s
def dilation_erosion():
    s="""clc
clear;
close;
//Importing the image
I = imread("D:\ImageProcessing\sunset.jfif");
subplot(2, 3, 1),
imshow(I);
title("Original image");
//Dilated Image
se = imcreatese('ellipse',7,7);
dilate = imdilate(I, se);
subplot(2, 3, 2),
imshow(dilate);
title("Dilated image");
//Eroded image
erode = imerode(I, se);
subplot(2, 3, 3),
imshow(erode);
title("Eroded image");
//Opened image
open = imopen(I, se);
subplot(2, 3, 4),
imshow(open);
title("Opened image");
//Closed image
Close = imclose(I, se);
subplot(2, 3, 5),
imshow(Close);
title("Closed image");"""
    return s