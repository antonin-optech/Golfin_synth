import sys, math
import numpy as np
from PIL import Image
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from objloader import Obj, set_texture  # Assuming this is your custom OBJ loader

# Global variables for camera control
rx, ry = (0, 0)
tx, ty = (0, 0)
zpos = 5
rotate = move = False

theta = 0  # angle init
dtheta = .1 # change of angle per frame
zAmplitudeRot = -.4
xAmplitudeRot = -(1- abs(zAmplitudeRot))
position = [0., 0., 0.]
dx = .0
dy = 1.
dz = .0
dposition = [dx, dy, dz]

frame = 0
fps = 60
frame_stop = 300
width = 1024
height = 1024
bg_texture_id = None


def load_background_texture(image_path):
    global bg_texture_id
    bg_image = Image.open(image_path).transpose(Image.FLIP_TOP_BOTTOM)
    if bg_image.mode != "RGBA":
        bg_image = bg_image.convert("RGBA")
    b_bg_image = np.array(list(bg_image.getdata()), np.uint8)
    
    # Create texture
    bg_texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, bg_texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, bg_image.width, bg_image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, b_bg_image)


def draw_background():
    global bg_texture_id
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, bg_texture_id)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glBegin(GL_QUADS)
    value = 50
    z_off = -100
    glTexCoord2f(0, 0); glVertex3f(-value, -value, z_off)
    glTexCoord2f(1, 0); glVertex3f(value, -value, z_off)
    glTexCoord2f(1, 1); glVertex3f(value, value, z_off)
    glTexCoord2f(0, 1); glVertex3f(-value, value, z_off)
    glEnd()
    
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)


def update_rotation():
    global theta, dtheta, position, dposition
    theta += dtheta
    position = [position[i] - dposition[i] for i in range(3)]
    

def timer(fps):
    if frame < frame_stop:
        update_rotation()
        glutPostRedisplay()
        glutTimerFunc(int(1000/fps), timer, fps)
    else:
        glutLeaveMainLoop()


def save_frame(filename, width, height):
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (width, height), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(filename, format='BMP')


def on_draw():
    global rx, ry, tx, ty, zpos, obj, bg_texture_id
    global frame, theta, xAmplitudeRot, zAmplitudeRot
    global center_x, center_y, center_z
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / float(height), 0.1, 1000.0)  # Adjust these values as needed
    projection_matrix = glGetFloatv(GL_PROJECTION_MATRIX)
    print(projection_matrix)
    glMatrixMode(GL_MODELVIEW)    
    glLoadIdentity()    
    gluLookAt(0, 0, 100,
            0, 0, 0,
            0, 1, 0)
    glDisable(GL_DEPTH_TEST)
    # draw_background()
    glEnable(GL_DEPTH_TEST)
    
    glTranslate(0, 50, -200)
    glTranslatef(*position)
    glRotatef(math.degrees(theta), xAmplitudeRot, 0, zAmplitudeRot)  # Rotating around the z-axis
    # glRotatef(math.degrees(backspin_angle), 1, 0, 0)  # Rotating around the x-axis : This is the backspin
    # glRotatef(math.degrees(4*theta/10), 1, 0, 0)  # Rotating around the x-axis
    
    glPushMatrix()  # Save the current matrix state
    glDisable(GL_TEXTURE_2D)
    glCallList(obj.gl_list) # Render the object
    glEnable(GL_TEXTURE_2D)
    glPopMatrix()

    save_frame("shots/frame" + str(frame) + ".bmp", width, height)
    frame += 1    
    glutSwapBuffers()

    # glDisable(GL_DEPTH_TEST)
    # draw_background()
    # glEnable(GL_DEPTH_TEST)
    # glPushMatrix()
    
    
    # glTranslate(position[0], 0, position[2])
    # glRotatef(10, 0, 1, 0)  # old
    # glTranslate(0, 20, 0)
    # glRotatef(90, 1, 0, 0)

def on_resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90.0, width / float(height), 1, 200.0)
    glMatrixMode(GL_MODELVIEW)

def on_mouse(button, state, x, y):
    global zpos, rotate, move
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        rotate = True
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        move = True
    elif button == GLUT_LEFT_BUTTON and state == GLUT_UP:
        rotate = False
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_UP:
        move = False
    elif button == 3:  # Scroll up
        zpos = max(1, zpos - 1)
    elif button == 4:  # Scroll down
        zpos += 1

def on_motion(x, y):
    global rx, ry, tx, ty
    if rotate:
        rx += x
        ry += y
    if move:
        tx += x
        ty -= y


if __name__ == "__main__":
    global obj
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutCreateWindow("OBJ File Viewer")
    # Initialize the object (Make sure to update the paths accordingly)
    background_image_path = 'texture/green_pad.png'
    load_background_texture(background_image_path)
    
    texture_root = 'texture/golf_ball/Golf_Ball_OBJ/'
    filename = 'Golf Ball OBJ.obj'    
    obj = Obj(texture_root, filename, swapyz=True)
    glutDisplayFunc(on_draw)
    # glutReshapeFunc(on_resize)
    # glutMouseFunc(on_mouse)
    # glutMotionFunc(on_motion)
    glutTimerFunc(0, timer, fps)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)

    # Directional light source
    lightPos = (-40, 200, 100, 0.0) 
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.10, 0.10, 0.10, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.75, 0.75, 0.75, 1.0])

    # Set material properties
    set_texture(obj.materials[obj.material])
    
    glutMainLoop()
