import matplotlib.image as mpimg
import matplotlib.pyplot as plt
I = mpimg.imread('./an2i_straight_neutral_open.jpg')

print (I.shape)
print(I)
plt.imshow(I)
