import glob
from PIL import Image
import cv2
import numpy as np
import imageio
import os


width = 512.0
height = 512.0
RATIO = width/height


def imgs_to_gif(path_list, out_name, width=250, height=int(250 * RATIO), fps=2.5, interpolation=cv2.INTER_CUBIC, cmap=None, format='mp4', resize=(512, 512)):
    
    frames = []
    for path in path_list:
        image = cv2.imread(path)
        # img = imageio.read(image)
        if cmap:
            image = cmap(image)
        if resize:
            image = cv2.resize(image, resize, interpolation=interpolation).astype(np.uint8)
        frames.append(image)
    imageio.mimsave(out_name, frames, fps=fps, format=format)

def stack_imgs(path_0, path_1, out_name, fps=2.5, format='mp4'):
    assert len(path_0) == len(path_1)
    frames = []
    for idx in range(len(path_0)):
        img_r = cv2.imread(path_0[idx])
        img_l = cv2.imread(path_1[idx])
        frames.append(np.concatenate((img_l, img_r), axis=1))
    imageio.mimsave(out_name, frames, fps=fps, format=format)

def create_gif(path_list, out_name, fps=60):
    duration = 1000*fps/60
    images = []
    for path in path_list:
        images.append(Image.open(path))
    images[0].save(out_name, save_all=True, append_images=images[1:], optimize=False, duration=duration, loop=0)

paths = sorted(glob.glob('test_video/frames/frame*.png'), key=os.path.getmtime)
# create_gif(paths, "out.mp4")
imgs_to_gif(paths[1:], "gif/out_bg_raft.mp4", fps=30, resize=(512, 512))

# paths_r = sorted(glob.glob('shots/*_right.png'), key=os.path.getmtime)
# paths_l = sorted(glob.glob('shots/*_left.png'), key=os.path.getmtime)
# stack_imgs(paths_l, paths_r, out_name='gif/stacked.mp4', fps=30)
