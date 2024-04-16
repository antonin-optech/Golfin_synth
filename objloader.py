from OpenGL.GL import *


def mtl(root_path, filename):
    materials = {}
    material = None
    for line in open(root_path + filename, "r"):
        line = line.lstrip().strip()
        
        if line.startswith('#'): continue
        
        if not line: continue
        
        if line.startswith('newmtl'):
            materials[line.split()[1]] = material = {}
        else:
            key, *value = line.split(' ')
            material[key] = [float(item) for item in value]
    return materials


def set_texture(mtl):
    glMaterialfv(GL_FRONT, GL_SHININESS, *mtl['Ns'])
    glMaterialfv(GL_FRONT, GL_AMBIENT, mtl['Ka'])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mtl['Kd'])
    glMaterialfv(GL_FRONT, GL_SPECULAR, mtl['Ks'])
    glMaterialfv(GL_FRONT, GL_EMISSION, mtl['Ke'])


def geometric_center(vertices):
    x = [v[0] for v in vertices]
    y = [v[1] for v in vertices]
    z = [v[2] for v in vertices]
    center_x = sum(x) / len(vertices)
    center_y = sum(y) / len(vertices)
    center_z = sum(z) / len(vertices)
    return (center_x, center_y, center_z)


class Obj:
    def __init__(self, root_path, filename, swapyz=False) -> None:
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.material = None
        self.materials = None
        self.root_path = root_path
        self.filename = filename
        self.swapyz = swapyz
        self.gl_list = None
        self.texture_id = None
        self.load_obj()

    def load_obj(self):
        for line in open(self.root_path + self.filename, "r"):
            if line.startswith('#'): continue

            values = line.split()
            if not values: continue
            
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if self.swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if self.swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            
            elif values[0] in ('usemtl', 'usemat'):
                self.material = values[1]
            
            elif values[0] == 'mtllib':
                self.materials = mtl(self.root_path, line.split('mtllib')[-1].strip())
            
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')

                    vertex_idx = int(w[0])
                    if vertex_idx < 0:
                        vertex_idx = len(self.vertices) + vertex_idx + 1
                    face.append(vertex_idx)

                    texcoord_idx = int(w[1]) if len(w) >= 2 and w[1] else 0
                    if texcoord_idx < 0:
                        texcoord_idx = len(self.texcoords) + texcoord_idx + 1
                    texcoords.append(texcoord_idx)

                    norm_idx = int(w[2]) if len(w) >= 3 and w[2] else 0
                    if norm_idx < 0:
                        norm_idx = len(self.normals) + norm_idx + 1
                    norms.append(norm_idx)

                self.faces.append((face, norms, texcoords, self.material))
    
        center = geometric_center(self.vertices)
        self.vertices = [(v[0] - center[0], v[1] - center[1], v[2] - center[2]) for v in self.vertices]  # centering the object at the origin
        self.texture_id = glGenTextures(1)  # binding default texture params to the object
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glFrontFace(GL_CCW)
        for face in self.faces:
            vertices, normals, texture_coords, material = face
            mat = self.materials[material]
            glColor(mat['Kd'])
            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()