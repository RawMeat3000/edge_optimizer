This tool is for optimizng models where lots of edge loops were inserted or booleans were used, which often results in adding edges and verts that don't help describe surface details.

The tool supports adjusting the tolerance of edges to be deleted. It defaults to deleting only edges which add miniscule amounts of curvature, but can be dialed up to get more aggressive if needed.
The tool supports ignoring edges if they are UV borders. Support for other things like verted colors is TODO.

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/4b178bed-14d1-44ff-8c3f-0292214b85f6)

Model before:

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/4026a5bc-16b5-43d3-b2bd-cda8fe29d594)

After

![image](https://github.com/RawMeat3000/edge_optimizer/assets/5659157/f616f859-031a-4d64-92c1-ca1b94dcdf82)

Let me know what you think!
