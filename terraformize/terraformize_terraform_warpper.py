from python_terraform import *

class terraform:

    def __init__(self):
        # just a template that still needs work
        self.tf = Terraform()

    def apply(self):
        # just a template that still needs work
        self.tf.apply('/home/test123123', no_color=IsFlagged, refresh=False, var={'a':'b', 'c':'d'})

    def destory(self):
        # just a template that still needs work
        self.tf.destroy()
