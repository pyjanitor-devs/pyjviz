import graphviz
import IPython.display
import rdflib

from . import viz

def show_method_chain(dot_code):
    gvz = graphviz.Source(dot_code)

    # NB: I don't understand how code below works in jupyter notebook
    # somehow obj gvz of type graphviz.Source converted to image by IPython module
    # and note that no temp files in current dirctory are visible
    if 1:
        print("gvz:", type(gvz))
        #print(dir(gvz))
        IPython.display.display_png(gvz)
    else:
        gvz.render(format = 'png')
        print("gvz:", type(gvz))
        #print("filename:", gvz.filename)
        #image = IPython.display.Image(filename = gvz.filename + '.png')
        image = gvz.view()
        print("image:", type(image), image[:20])
        #scale = 0.3
        #image = image.resize(( int(image.width * scale), int(image.height * scale)))
        IPython.display.display_png(image)
