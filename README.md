This tool is meant for optimizing meshes in some commonly needed ways, with a focus on edges.  


![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/2d19e334-c832-4f13-8d18-5c51e704a668)

Feature 1 - Unnecessary edge deletion. The tool can delete edges which do not add noticeable complexity to a model, such as leftover edge loops from construction or boolean operations. The detection algorith can be dialed up to delete edges more aggressively if additional optimization is needed. The tool supports ignoring edges if they are things like UV borders to avoid visual artifacts. 
   
Model before:

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/4026a5bc-16b5-43d3-b2bd-cda8fe29d594)

After

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/f616f859-031a-4d64-92c1-ca1b94dcdf82)


Feature 2 - This function smooths "hard" edges which inflate vertex counts through duplication of vertices via broken tangents/binormals. These usually happen when assets get exported/re-imported using wrong settings or via formats like OBJ which don't support smoothing very well. This was a shockingly common issue in situations where content moves frequently between programs and gets converted to different file types. It happened most often in characters, likely due to artists moving the model data between apps like Maya and Zbrush often and losing information. 

Before - When debugging tangent directions, you may notice that some of the blue vectors point multiple directions per vertex. This results in duplicated vertices and inflated asset costs. 

Vertices: 1596

Normals: 5706

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/b28648d4-8bd6-4eb9-a7d9-b4fc95e37d63)


After - There should only be as many tangents as there are normals, roughly. The model is fixed. 

Vertices: 1596

Normals: 1608 (~3.5x reduction from before)

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/a0837c22-d107-45b5-a7e1-346353b8e0fa)
