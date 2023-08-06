import onnxruntime

import cv2
import os
import numpy as np

class Onnx_session:
    def __init__(self,model_path,**kwargs):
        onnx_device = kwargs.get("onnx_device",'cpu')
        if onnx_device=='cpu':
            self.providers = ['CPUExecutionProvider']
        else:
            self.providers = ['CUDAExecutionProvider']
        print("providers:",self.providers)
        self.net = onnxruntime.InferenceSession(model_path,providers=self.providers)
        self.input_name = self.net.get_inputs()[0].name
        self.output_names_= [ output.name for output in self.net.get_outputs() ]
        self.outs_len = len(self.output_names_)

        self.output_sort=kwargs.get("output_sort",False)

        self.input_mean = kwargs.get("input_mean",127.5)
        self.input_std = kwargs.get("input_std",128.0)

        if self.output_sort:
            self.output_names = sorted(self.output_names_)
        else:
            self.output_names = self.output_names_

        self.torch_image = kwargs.get("torch_image",False)


    def __call__(self,img):
        
        if self.torch_image: # type torch, transpose, expand (N,C,H,W)
            img = np.array(img,dtype=np.float32)
        else:
            img = img.astype(np.float32).transpose(2, 0, 1)
            img = np.expand_dims(img, axis=0).astype(np.float32) #NCHW
            
        img = (img - self.input_mean) / self.input_std
        inp_dct = {self.input_name:img}
        outs = self.net.run(self.output_names, input_feed=inp_dct)

        return outs


