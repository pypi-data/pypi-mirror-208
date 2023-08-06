import matplotlib.pyplot as plt
import imageio
import os, glob
import time



class AnimatPlot:
  pattern_savefig = 'fig_%(i)s.png'
  pattern_dir = '.data'
  images = None
  
  def __init__(self,f,x,callback_plot:plt,plt:plt=plt,args=None):
    self.__pattern_dir_check()
    self.f = f
    self.plot = callback_plot
    self.args = args
    self.x = x
    self.size = len(self.x)
    self.plt = plt



  def render_cache(self):
    self.images = []
    if os.path.isdir(self.pattern_dir):
      self.images = sorted([file for file in glob.glob(self.pattern_dir+'/'+'*.png')])
      print(f'find {len(self.images)} images in cache! \ngetting it images...')
    
    else:
      time_init = time.time()
      for i,x in enumerate(self.x):
        self.__pattern_dir_check()
        #print(f'[{i}/{self._size}]')
        f = self.f(self.x[:i],*self.args)[:i] if self.args else self.f(self.x[:i])[:i]
        plot = self.plot(self.plt,f[:i],self.x[:i])
        img_plot = self.pattern_dir+'/'+self.pattern_savefig%{'i':str(i)}
        plot.savefig(img_plot)
        plot.cla()
        plot.clf()
        self.images.append(img_plot)

      ping_total = time.time()-time_init
      ping = 1000*ping_total/self.size
      speed = self.size/ping_total
      print(f'ended saved cache images! \n[{self.size} images saved in {ping_total:.1f}s | speed: {speed:.1f}/img/s | ping: {ping:.1f}ms]')




  def render_gif(self,path,fps=8.9):
    time_init = time.time()
    imgs_imread = []

    if len(self.images)>10:
      for i,img in enumerate(self.images):
        imgs_imread.append(imageio.imread(img))
      imageio.mimsave(path,imgs_imread,fps=fps)
      ping_total = time.time() - time_init
    
    else:
      file_imgs = [file for file in glob.glob(self.pattern_dir+'*.png')]

      if file_imgs:
        imgs_imread = []
        for i,img in enumerate(file_imgs):
          imgs_imread.append(imageio.imread(img))
        imageio.mimsave(path,imgs_imread,fps=fps)
    ping_total = time.time() - time_init
    print(f'{path} saved in {ping_total:.1f}s')




  def __pattern_dir_check(self):
    if not os.path.isdir(self.pattern_dir):
      os.mkdir(self.pattern_dir)

  def delete_cache(self):
    if os.path.isdir(self.pattern_dir) and len(self.images)>2:
      for i,image in self.images:
        os.remove(image)





