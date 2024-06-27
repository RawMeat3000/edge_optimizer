

"""
TODO
>> Get working in 2015
>> Refactor deleteBooleanEdges()
>> Make this into a more versitile boolean replacement tool, not just cleanup
>> Investigate creating a temp mesh that encompasses boolVerts, 
   could check against that mesh to perform a mergeShortEdges function
   after deleting edges and having things reordered
>> Find better way to do the mesh == om2.MFnMesh(dagPath) line
		it's everywhee rnad it repeats a lot
"""


import maya.api.OpenMaya as om2
import pymel.core as pm


class EdgeOptimizer(object):
    mayaVersion = pm.about(version = True)

	
    def removeFromArray(dagPath, components, deleteMe):
        """
        Helper function that performs a simple but repetative task of removing things from MIntArrays
        """
        for i, k in enumerate(components):
            if k == deleteMe:
                components.remove(i)
        return components
        
		
    def indexToString(self, dagPath, items, componentType):
        """
        Helper function to convert API component indicies to strings that Python and MEL understand
        """
        strings = []
        for item in items:
            strings.append("%s.%s[%d]" % (dagPath, componentType, item))
        return strings
        
		
    def getVertPositions(self, dagPath):
        mesh = om2.MFnMesh(dagPath)
        
        vertIndicies = []
        vertPositions = []
        
        for vert in range(mesh.numVertices - 1):
            vertIndicies.append(vert)
            vertPos = mesh.getPoint(vert)
            vertPositions.append((vertPos.x, vertPos.y, vertPos.z))
            
        return vertIndicies, vertPositions

        
    def getBooleanVertices(self, dagPath, mode):
        # Get input nodes on object to find new edges created by booleans
        obj = pm.ls(dagPath)[0]
        
        if mode == "Entire Mesh":
            print("Iterating over whole mesh")
            boolVerts = range(0, obj.numVertices()-1)

        elif mode == "Boolean History":
            boolNodes = []
            
            # Iterate trough input nodes and find all booleans
            for node in obj.listHistory():
                if node.nodeType() == "polyCBoolOp":
                    node = node.listHistory()[-1]
                    # Move the cut mesh up 1000 units to be safe
                    # This temporarily removes the boolean effects
                    # Pretty hacky, but it works
                    print(node)
                    pm.xform(node, t=[0,1000,0])
                    
                    boolNodes.append(node)
                    
            # Record vert positions
            preVertIndicies, preVertPositions = self.getVertPositions(dagPath)
            
            # move transforms back and record vert positions again
            for boolNode in boolNodes:
                pm.xform(boolNode, t=[0,-1000,0])
                
            postVertIndicies, postVertPositions = self.getVertPositions(dagPath)
            
            # Diff vert lists to find new verts
            diffedVerts = set(preVertPositions).intersection(set(postVertPositions))
            
            boolVerts = []
            for i, vert in enumerate(diffedVerts):
                boolVerts.append(postVertIndicies[i])

        elif mode == "By Material":
            print("Searching by material")
            material = raw_input("Enter material name")
			
            # Select faces by material. Get edges, then get verts
            pm.hyperShade(objects=material)
            boolVerts = pm.ls( pm.polyListComponentConversion(fromFace=True, toVertex=True), fl=True )
			
            for i, vert in enumerate(boolVerts[:]):
                boolVerts[i] = vert.index()
            
        print("Bool verts:", boolVerts)
        
        if boolVerts:
            return boolVerts
        else:
            pm.error( "Script failed to find boolean stuff" )
        
		
    def getEdgeVector(self, mesh, edge):
        edgeVerts = mesh.getEdgeVertices(edge)
        edgeVector = (om2.MVector(mesh.getPoint(edgeVerts[0])) - om2.MVector( mesh.getPoint(edgeVerts[1])))
        return edgeVector
        
		
    def checkOutlyingEdges(self, dagPath, verts, connectedEdges):
        conVertIter = om2.MItMeshVertex(dagPath)
        while not conVertIter.isDone():
            # maya seems to crash if this list is empty!
            if verts: 
                if conVertIter.index() == verts[verts.__len__() - 1]:
                    outlyingEdges = conVertIter.getConnectedEdges()
                    # Deleting this edge could change the mesh in a negative way
                    # we need to check to see if it's safe
                    if outlyingEdges > 4:
                        sharedEdges = list(set(outlyingEdges).intersection(connectedEdges))
                        print(sharedEdges)
                        if sharedEdges:
                            for i, edge in enumerate(sharedEdges):
                                if edge in connectedEdges:
                                    connectedEdges.remove(i)    
                        conVertIter.reset()
                    verts.remove( verts.__len__() - 1 )
                conVertIter.next()
				
            else:
                print("ran out of verts")
                break
            
        return connectedEdges

		
    def checkUVBorders(self, edges):
        print("Checking if edges are part of a UV border")
        safeEdges = []
        for edge in edges:
            numUVs = pm.ls( pm.polyListComponentConversion( edge, fromEdge=True, toUV=True ), fl=True)
            if len(numUVs) < 3:
                safeEdges.append(edge)
        return safeEdges
    
	
    def getParallelEdges(self, dagPath, vert, angleTolerance):
        
        mesh = om2.MFnMesh(dagPath)
        
        # Maya 2014 and 2015 don't have access to certain methods, so they need different methods
        if int(self.mayaVersion) <= 2015:
            faceIter = om2.MItMeshPolygon(dagPath)
            while not faceIter.isDone():
                faceIter.next()
           
        else:
            vertIter = om2.MItMeshVertex(dagPath)
            while not vertIter.isDone():
                
                if vertIter.index() == vert:
                    connectedEdges = vertIter.getConnectedEdges()
                    # See if any edge is parallel to any other
                    for i, edge1 in enumerate(connectedEdges):
                        for edge2 in connectedEdges[i+1:]:
                            
                            edge1Vector = self.getEdgeVector(mesh, edge1)
                            edge2Vector = self.getEdgeVector(mesh, edge2)
                            
                            if edge1Vector.isParallel(edge2Vector, angleTolerance):
                                # If there are parallel edges, remove them from the list
                                connectedEdges = self.removeFromArray(connectedEdges, edge1)
                                connectedEdges = self.removeFromArray(connectedEdges, edge2)
                                
                                # 
                                connectedVerts = vertIter.getConnectedVertices()
                                
                                #connectedEdges = self.checkOutlyingEdges(dagPath, connectedVerts, connectedEdges)
                                print(connectedEdges)
                                connectedEdges = self.checkUVBorders(self.indexToString(dagPath, connectedEdges, "e"))
                                return connectedEdges
                            
                vertIter.next()
    
	
    def mergeBooleanVerts(self, dagPath, boolVertPositions):
        print("Merging verts")
        verts = om2.MFnMesh(fagPath).getPoints()
        
        mergeVerts = set(verts).difference(set(boolVertPositions))
        
        
    def deleteBooleanEdges(self, mode="Entire Mesh", angleTolerance=0.001, mergeVerts=False, mergeDistance=0.01):
        selection = om2.MGlobal.getActiveSelectionList()
        toDelete = []

        if int(self.mayaVersion) <= 2015:
            print("This doesn't work yet in 2015")
            #This will help with older version of maya, or people who don't have service packs installed (curse them)
            for i in range(selection.length()):
                dagPath = selection.getDagPath(i)
                print("Dag path", dagPath)
                meshDag = om2.MFnDagNode(dagPath)
                
                # Get edges and verts to work on
                boolVerts = self.getBooleanVertices(dagPath, mode)
                # Iterate  over verts (unless there's an edge method)
                for vert in boolVerts:
                    edges = self.getParallelEdges(dagPath, vert, angleTolerance)
                    if edges:
                        for edge in edges:
                            if edge not in toDelete:
                                toDelete.append(edge)
                    
        else:
            selIter = om2.MItSelectionList(selection)
            while not selIter.isDone():
                dagPath = selIter.getDagPath()
                meshDag = om2.MFnDagNode(dagPath)
                # Get edges and verts to work on
                boolVerts = self.getBooleanVertices(dagPath, mode)
                # Iterate  over verts (unless there's an edge method)
                for vert in boolVerts:
                    edges = self.getParallelEdges(dagPath, vert, angleTolerance)
                    if edges:
                        for edge in edges:
                            if edge not in toDelete:
                                toDelete.append(edge)
                
                selIter.next()
        
        print("To be deleted", toDelete)
        if toDelete:
            pm.polyDelEdge(toDelete, cv=True)         


class UI(EdgeOptimizer):

    def __init__(self):
        windowName = "EdgeOptimizer"
    
        if pm.window(windowName, exists=True):
            pm.deleteUI(windowName)
        
        pm.window(windowName, t=windowName, menuBar=True)
        
        pm.menuBarLayout()
        pm.menu( label='Help' )
        pm.menuItem( label='There is no help!' )
        #pm.menuItem( label='Polycount Thread' )
        #pm.menuItem( label='Creative Crash' )
        #pm.menuItem( label='My Website' )
        
        # Padding to make things look nicer
        pm.frameLayout(labelVisible=False, marginHeight=10, marginWidth=10)
        
        pm.text(l="Instructions:\r\nThis tool I made in 2015 at work, then recreated at home from scratch. \r\nIt is meant to remove superfluous edges from a model which\
                \r\ndo not add detail and can safely be optimized away without affecting the visual look.\r\n")
        
        pm.frameLayout(label="", marginHeight=5, marginWidth=5)

        pm.columnLayout(rowSpacing=10, adjustableColumn=True)
        self.angleToleranceSlider = pm.floatSliderGrp(l="Angle Tolerance", field=True, value=0.001, minValue=0, maxValue=0.1, step=0.001, 
                                                    adjustableColumn=3, columnWidth=([2,0], [3,150]), columnAttach3=["right","left","right"], 
                                                    columnOffset3=[40,-40,0], annotation="You'll probably never need to adjust this.")
        self.mergeDistSlider = pm.floatSliderGrp(l="Vert Merge Distance", field=True, value=0.05, 
                                               columnWidth=([2,0], [3,150]), adjustableColumn=3, columnAttach3=["right","left","right"], 
                                               columnOffset3=[40,-40,0], annotation="Info text")
        #pm.intSliderGrp(l="Some other option", field=True, value=0)
        
        pm.rowLayout(numberOfColumns=2)
        self.searchTypeDropdown = pm.optionMenuGrp(label='Search Type', columnAlign=[1,"left"], columnAttach=[2,"left", -80] )
        pm.menuItem(label='Entire Mesh')
        pm.menuItem(label='Boolean History')
        pm.menuItem(label='By Material')
        self.mergeVertsCheckbox = pm.checkBoxGrp(label="Merge verts afterward", columnAlign=[1,"left"], columnAttach=[2,"left", -10])
        pm.setParent('..')
        
        pm.button(l="Clean it!", h=40, c=lambda *args:self.buttonPress(), bgc=[0.6,0.6,0.6])
        
        pm.showWindow(windowName)
        
		
    def buttonPress(self):
        angleTolerance = pm.floatSliderGrp(self.angleToleranceSlider, query=True, value=True)
        mergeDistance = pm.floatSliderGrp(self.mergeDistSlider, query=True, value=True)
        searchType = pm.optionMenuGrp(self.searchTypeDropdown, query=True, value=True)
        mergeVerts= pm.checkBoxGrp(self.mergeVertsCheckbox, query=True, value1=True)
        
        self.deleteBooleanEdges(searchType, angleTolerance, mergeVerts, mergeDistance)

		
    def dropDownMenu(self):
        pass
    
	
    def openWebPage(self):
        pass
        
		
edgeOptimizerWindow = UI()