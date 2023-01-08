import numpy as np
from pyrr import Matrix44
import moderngl
from ported._example import Example
from numpy import ones
from moderngl import DEPTH_TEST, TRIANGLE_STRIP
from numpy import sin, cos, array

z = (0, 0, 1)
r = range(5)

class MultiTextireTerrain(Example):
    title = "Multitexture Terrain"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(vertex_shader =
            '''#version 460

            uniform mat4 Mvp;
            uniform sampler2D Heightmap;

            in vec2 in_vert;
            out vec2 v_text;

            void main() {
                gl_Position = Mvp * vec4(in_vert - 1.0 / 2,
                    texture(Heightmap, in_vert).r / 5, 1);
                v_text = in_vert;
            }''', fragment_shader=
            '''#version 460

            uniform sampler2D Heightmap, Color1, Color2, Cracks,
                Darken;

            in vec2 v_text;

            out vec4 f_color;

            void main() {
                float height = texture(Heightmap, v_text).r,
                    border = smoothstep(0.5, 0.7, height);
                
                f_color = vec4((((texture(Color1, v_text * 7).rgb *
                    (1 - border) + texture(Color2, v_text * 6).rgb * border) / 5 * (4 + texture(Darken, v_text * 3).r)) / 2 * (1 + texture(Cracks, v_text * 5).r)) / 2 * (1 + height), 1);
            }''')

        self.mvp = self.prog['Mvp']
        size = 32
        vertices = np.dstack(np.mgrid[:size, :size][::-1]) / size #secciones :size - 10
        temp = np.dstack([np.arange(0, size ** 2 - size),\
            np.arange(size, size ** 2)])
        index = np.pad(temp.reshape(size - 1, 2 * size),\
            ((0, 0), (0, 1)), 'constant', constant_values = -1)
        self.vbo, self.ibo = (*(self.ctx.buffer(e) for e in\
            (vertices.astype('f4'), index.astype('i4'))),)
        vao_content = ((self.vbo, '2f', 'in_vert'),)
        self.vao = self.ctx.vertex_array(self.prog, vao_content,\
            self.ibo)
        self.tex0, self.tex1, self.tex2, self.tex3, self.tex4 =\
            (*(self.load_texture_2d(e) for e in ('heightmap.jpg',\
            'grass.jpg', 'rock.jpg', 'cracks.jpg', 'checked.jpg')),)
        self.es = (self.tex0, self.tex1, self.tex2, self.tex3,\
            self.tex4)

        (*(e.build_mipmaps() for e in self.es),)

        self.prog['Heightmap'], self.prog['Color1'],\
            self.prog['Color2'], self.prog['Cracks'],\
            self.prog['Darken'] = r

    def render(self, time, frame_time):
        angle = time / 5
        e = self.ctx

        e.clear(*ones(3))
        e.enable(DEPTH_TEST) 

        (*(e.use(i) for e, i in
            (*((self.es[i], i) for i in r),)),)

        proj, lookat = Matrix44.perspective_projection(45,
            self.aspect_ratio, 1 / 10, 1000),\
            Matrix44.look_at((cos(angle), sin(angle), 8 / 10),
            array(z) / 10, z)

        self.mvp.write((proj * lookat).astype('f4'))
        self.vao.render(TRIANGLE_STRIP)

MultiTextireTerrain.run()
