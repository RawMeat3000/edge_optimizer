This tool is for optimizng models where lots of edge loops were inserted or booleans were used, which often results in adding edges and verts that don't help describe surface details.

The tool supports adjusting the tolerance of edges to be deleted. It defaults to deleting only edges which add miniscule amounts of curvature, but can be dialed up to get more aggressive if needed.
The tool supports ignoring edges if they are UV borders. Support for other things like verted colors is TODO.

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/2d19e334-c832-4f13-8d18-5c51e704a668)

Feature 1 - Unnecessary edge deletion.
   
Model before:

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/4026a5bc-16b5-43d3-b2bd-cda8fe29d594)

After

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/f616f859-031a-4d64-92c1-ca1b94dcdf82)


Feature 2 - Fixing "hard" edges that inflate vertex counts during rendering. These usually happen when assets get exported/re-imported using wrong settings or via formats like OBJ which don't support smoothing very well. This was a shockingly common issue in the production of Call of Duty: WWII. It happened most often in characters, likely due to artists moving the model data between apps like Maya and Zbrush often and losing information. 

Before - When debugging tangent directions, you may notice that some of the blue vectors point multiple directions per vertex. This results in duplicated vertices and inflated asset costs. 

Vertices: 1596
Normals: 5706

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/b28648d4-8bd6-4eb9-a7d9-b4fc95e37d63)


After - There should only be as many tangents as there are normals, roughly. The model is fixed. 

Vertices: 1596
Normals: 1608 (~3.5x reduction from before)

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/a0837c22-d107-45b5-a7e1-346353b8e0fa)
