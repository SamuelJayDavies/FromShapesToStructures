# FromShapesToStructures
This project investigating how 3D object representations can be converted into buildable LEGO-style reconstructions using a constrained artificial intelligence pipeline. 

To run, first ShapeNetCore models are required, if other models are used such as ModelNet40, the reconstruction will work, just on the wrong axis. 

Next, createa folder called model_data/shape_net_core, here place object folders such as Bottle or Chair. Within these folders, each objective needs to be given a number in this format 0001, and then inside have the .obj file. An expected file path for a mug object would look like model_data/shape_net_core/mug/0001/mug.obj. Example models cannot be included as they are part of the ShapeNetCore repository. 

Once models have been added to the folders, just change the model category and number in the test_full_optimsiation class and run it. 
