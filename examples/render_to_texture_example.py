from numpy import sin, ones
from pyrr import Matrix44
from moderngl_window import WindowConfig
from moderngl import DEPTH_TEST, CULL_FACE

from tkinter import Tk, Frame, LabelFrame, Button

class ColorsAndTexture(WindowConfig):
    #Renders a floating, oscillating, 3d island with lights
    resource_dir, gl_version, title = 'data', (3, 3),\
                                      "Colors and Textures"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(vertex_shader =\
        '''#version 330
        uniform mat4 Mvp = mat4(0);
        in vec3 in_position, in_normal;
        in vec2 in_texcoord_0;
        out vec3 v_vert, v_norm;
        out vec2 v_text;
        void main() {
            gl_Position = Mvp * vec4(in_position, 1);
            v_vert = in_position;
            v_norm = in_normal;
            v_text = in_texcoord_0;
        }''', fragment_shader =\
        '''#version 330
        uniform vec3 Light = vec3(0), Color = vec3(0);
        uniform bool UseTexture = false; //en minusculas
        uniform sampler2D Texture;
        in vec3 v_vert, v_norm;
        in vec2 v_text;
        out vec4 f_color;
        void main() {
            float lum = clamp(dot(normalize(Light - v_vert), normalize(v_norm)), 0.0, 1.0) * 0.8 + 0.2;
            if (UseTexture) {
                f_color = vec4(texture(Texture, v_text).rgb * lum, 1);
            } else {
                f_color = vec4(Color * lum, 1);
            }
        }''')

        # Note: This is a fairly manual way to loading and rendering wavefront files.
        # There are easier ways when loading multiple objects in a single obj file.
        # Load obj files
        # Extract the VAOs from the scene
        self.vao_ground, self.vao_grass, self.vao_billboard,\
                         self.vao_holder, self.vao_image =\
        (*(obj.root_nodes[0].mesh.vao.instance(self.prog)\
         for obj in (*(self.load_scene(obj + '.obj') for obj in\
        ('scene-1-ground', 'scene-1-grass', 'scene-1-billboard',\
                           'scene-1-billboard-holder',\
                           'scene-1-billboard-image')),)),)
        
        # texture on billboard
        self.texture = self.load_texture_2d('infographic-1.jpg')

    def render(self, time, frame_time):
        self.ctx.clear(*ones(3))
        self.ctx.enable(DEPTH_TEST | CULL_FACE)

        proj, lookat, rotate, self.prog['UseTexture'],\
              self.prog['Light'], self.prog['Color'] =\
              Matrix44.perspective_projection(45,\
                                  self.aspect_ratio, 1/10, 1000),\
                       Matrix44.look_at((47.697, -8.147, 24.498),
                                           (0, 0, 8), (0, 0, 1)),\
              Matrix44.from_z_rotation(sin(time) / 2 + 1 / 5),\
              False, (67.69, -8.14, 52.49), (0.67, 0.49, 0.29)

        self.prog['Mvp'].write((proj * lookat * rotate).astype('f4'))
        self.vao_ground.render()

        for a, b in (((0.46, 0.67, 0.29),\
                       lambda n = 0 : self.vao_grass.render()),\
                      (ones(3),\
                       lambda n = 0 : self.vao_billboard.render()),\
                      (ones(3) / 5,\
                       lambda n = 0 : self.vao_holder.render())):
            self.prog['Color'] = a
            b()       

        self.prog['UseTexture'] = True

        self.texture.use()
        self.vao_image.render()

class RenderToTexture(ColorsAndTexture):
    title, gl_version = "Render to Texture", (3, 3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.texture1 = self.texture
        self.texture2 = self.ctx.texture(self.wnd.size, 3)
        depth_attachment =\
                        self.ctx.depth_renderbuffer(self.wnd.size)
        self.fbo = self.ctx.framebuffer(self.texture2,\
                                        depth_attachment)

    def render(self, *args): #time, frame_time):
        texturas = (self.texture1, self.texture2)
        contextos = (self.fbo, self.ctx.screen)

        for a, b in ((self.texture1, lambda n = 0 : self.fbo.use()),\
                     (self.texture2, lambda n = 0 : self.ctx.screen.use())):
            self.texture = a
            b()
            super().render(*args)

from moderngl import create_standalone_context, create_context

class CWindow_tk(Frame, WindowConfig):
    """
    It does not matter from what the class inhereted is:
    """ 
    def btnCreateContext_onClick (self):
        self.ctx3 = create_standalone_context()                    
        self.ctx4 = create_context()        
        print("CWindow_tk:self.btnCreateContext_onClick : screen.width = {0} , screen.height = {1}".format ( self.ctx4.screen.width, self.ctx4.screen.height) ) 

    def __init__(self, master):
        fraMain_width = 1290
        fraMain_height = 880
        
        self.ctx0 = create_standalone_context()                    
        self.ctx1 = create_context()        
        print("CWindow_tk::__init__ : screen.width = {0},\
              screen.height = {1}".format(self.ctx1.screen.width,\
                                          self.ctx1.screen.height) )  
        
        self.fraMain = LabelFrame(master, width = fraMain_width,\
                height = fraMain_height, 
                text = "Demonstraing the CREATE_CONTEXT()  CTX.SCREEN SIZE problem ------- Look at the printouts on the console")
        self.fraMain.pack()
                
        self.btnRotateClockwise = Button(self.fraMain, 
                    text = "Create context by this button ", 
                    command = self.btnCreateContext_onClick )
        self.btnRotateClockwise.pack(side = 'left')

RenderToTexture.run()

'''root = Tk()
app  = CWindow_tk(root)

root.geometry("1300x950+30+30")
root.title("The opengl example '"'render_to_texture_example.py'"' integrated with a Tkinter window"  )    
root.update()
root.deiconify()
root.mainloop()'''
