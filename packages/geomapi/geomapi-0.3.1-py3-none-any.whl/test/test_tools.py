import os
from pathlib import Path
import shutil
import time
import unittest

import cv2
import geomapi.tools as tl
import geomapi.utils.geometryutils as gmu
from rdflib import RDF, RDFS, Graph, Literal, URIRef

 ################################## SETUP/TEARDOWN MODULE ######################

# def setUpModule():
#     #execute once before the module 
#     print('-----------------Setup Module----------------------')

# def tearDownModule():
#     #execute once after the module 
#     print('-----------------TearDown Module----------------------')

class TestTools(unittest.TestCase):

 ################################## SETUP/TEARDOWN CLASS ######################
  
    @classmethod
    def setUpClass(cls):
        #execute once before all tests
        print('-----------------Setup Class----------------------')
        st = time.time()
        cls.path= Path.cwd() / "test" / "testfiles" 
       
        #POINTCLOUD - E57_1
        cls.e57Path1=os.path.join(cls.path,'PCD',"week 22 - Lidar.e57")     

        #POINTCLOUD - E57_2
        cls.e57Path2=os.path.join(cls.path,'PCD',"week22_photogrammetry_densecloud - Cloud.e57")  

        #POINTCLOUD - XML
        cls.e57XmlPath=os.path.join(cls.path,'PCD',"week 22 - Lidar.xml") 

        #MESH
        cls.meshPath=os.path.join(cls.path,'MESH',"week22.obj")  
        # cls.mesh= o3d.io.read_triangle_mesh(cls.meshPath)
    
        #IMG
        cls.xmlPath1=os.path.join(cls.path,'IMG',"camera_position.xml")  
        cls.xmlPath2=os.path.join(cls.path,'IMG',"ReferenceLAMBERT08_TAW.xml")  
        cls.xmlPath3=os.path.join(cls.path,'IMG',"cameras_bridge.xml")  
        cls.xmlPath4=os.path.join(cls.path,'IMG',"cameras_paestum.xml") 
        
        #IFC1
        cls.bimGraphPath1= os.path.join(cls.path,'sampleBimGraph.ttl') #os.path.join(cls.path,'bimGraph1.ttl')
        # cls.bimGraph1=Graph().parse(cls.bimGraphPath1)
        cls.ifcPath1=os.path.join(cls.path,'IFC',"Academiestraat_building_1.ifc")  
        # cls.ifc1=ifcopenshell.open(cls.ifcPath1)   
        
        #IFC2 
        cls.bimGraphPath2= os.path.join(cls.path,'sampleBimGraph.ttl') #os.path.join(cls.path,'bimGraph2.ttl')
        # cls.bimGraph2=Graph().parse(cls.bimGraphPath2)
        cls.ifcPath2=os.path.join(cls.path,'IFC',"Mariakerke_AWV_Conform_3D_BT_l72.ifc")  
        # cls.ifc2=ifcopenshell.open(cls.ifcPath2)  

        #IFC3 
        cls.bimGraphPath3= os.path.join(cls.path,'sampleBimGraph.ttl') #os.path.join(cls.path,'bimGraph3.ttl')
        # cls.bimGraph3=Graph().parse(cls.bimGraphPath3)
        cls.ifcPath3=os.path.join(cls.path,'IFC',"Academiestraat_parking.ifc")  
        # cls.ifc3=ifcopenshell.open(cls.ifcPath3)   
        
        #IFC4 (IfcDoor)
        cls.bimGraphPath4= os.path.join(cls.path,'bimGraph4.ttl')
        # cls.bimGraph4=Graph().parse(cls.bimGraphPath4)
        cls.ifcPath4=os.path.join(cls.path,'IFC',"B1_ALG_Model.ifc")  
        # cls.ifc4=ifcopenshell.open(cls.ifcPath4)   
        
        #resourceGraph (data)
        cls.resourceGraphPath=os.path.join(cls.path,'resourceGraph.ttl')
        # cls.resourceGraph=Graph().parse(cls.resourceGraphPath)
        # cls.linkedSubjects=[s for s in cls.resourceGraph.subjects(RDF.type)]

        #RESOURCES
        cls.resourcePath=os.path.join(cls.path,"resources")
        if not os.path.exists(cls.resourcePath):
            os.mkdir(cls.resourcePath)
   
        et = time.time()
        print("startup time: "+str(et - st))
        print('{:50s} {:5s} '.format('tests','time'))
        print('------------------------------------------------------')

    @classmethod
    def tearDownClass(cls):
        #execute once after all tests
        print('-----------------TearDown Class----------------------')
        if os.path.exists(cls.resourcePath):
            shutil.rmtree(cls.resourcePath)  
        if os.path.exists(os.path.join(os.getcwd(),'resources') ):
            shutil.rmtree(os.path.join(os.getcwd(),'resources') )

################################## SETUP/TEARDOWN ######################

    def setUp(self):
        #execute before every test
        self.startTime = time.time()   

    def tearDown(self):
        #execute after every test
        t = time.time() - self.startTime
        print('{:50s} {:5s} '.format(self._testMethodName,str(t)))

################################## TEST FUNCTIONS ######################

    def test_e57xml_to_nodes(self):
        # e57XML
        nodes=tl.e57xml_to_nodes(e57XmlPath=self.e57XmlPath)
        self.assertEqual(len(nodes),2)
        #0
        self.assertAlmostEqual(nodes[0].cartesianTransform[0,3],0.379,delta=0.01)
        self.assertLess(nodes[0].cartesianTransform[0,0],0)
        self.assertAlmostEqual(nodes[0].cartesianBounds[0],-4.351,delta=0.01)
        #1
        self.assertEqual(nodes[1].cartesianTransform[0,3],0.0)
        self.assertEqual(nodes[1].cartesianTransform[0,0],-1)
        self.assertAlmostEqual(nodes[1].cartesianBounds[0],-5.69,delta=0.01)
        
        #with kwargs
        nodes=tl.e57xml_to_nodes(e57XmlPath=self.e57XmlPath,myattrib=1)
        self.assertEqual(nodes[0].myattrib,1)

        # with getResource 
        # nodes=tl.e57xml_to_nodes(e57XmlPath=self.e57XmlPath,getResource=True)
        # geometries=[n.resource for n in nodes]
        # self.assertEqual(len(geometries),2)

        # error when invalid extension
        self.assertRaises(ValueError,tl.e57xml_to_nodes,e57XmlPath=os.path.join(self.path,'PCD',"myXML.pcd") )

        # error when path doesn't exist
        self.assertRaises(ValueError,tl.e57xml_to_nodes,e57XmlPath=os.path.join(self.path,'PCD',"myXML.xml")    )


    def test_img_xml_to_nodes(self):

        self.assertEqual(len(tl.img_xml_to_nodes(self.xmlPath1,filterByFolder=False) ),86)
        self.assertEqual(len(tl.img_xml_to_nodes(self.xmlPath1,filterByFolder=True) ),3)
        nodes=tl.img_xml_to_nodes(self.xmlPath1,filterByFolder=True,getResource=True) 
        self.assertEqual(len(nodes),3)
        self.assertEqual(len([n.resource for n in nodes]),3)
        
        self.assertEqual(len(tl.img_xml_to_nodes(self.xmlPath3,filterByFolder=False) ),3123)
        self.assertEqual(len(tl.img_xml_to_nodes(self.xmlPath3,skip=10,filterByFolder=False) ),313)
                
        self.assertEqual(len(tl.img_xml_to_nodes(self.xmlPath4,filterByFolder=False) ),894)
        
    def test_e57header_to_nodes(self):

        #E571
        nodes=tl.e57header_to_nodes(e57Path=self.e57Path1)
        self.assertEqual(len(nodes),2)
        self.assertIsNone(nodes[0]._resource)
        #0
        self.assertAlmostEqual(nodes[0].cartesianTransform[0,3],0.510,delta=0.01)
        self.assertLess(nodes[0].cartesianTransform[0,0],0)
        self.assertAlmostEqual(nodes[0].cartesianBounds[0],-36.77,delta=0.01)
        #1
        self.assertAlmostEqual(nodes[1].cartesianTransform[0,3],4.524,delta=0.01)
        self.assertAlmostEqual(nodes[1].cartesianTransform[0,0],0.941,delta=0.01)
        self.assertAlmostEqual(nodes[1].cartesianBounds[0],-28.360,delta=0.01)
        
        #with kwargs
        nodes=tl.e57xml_to_nodes(e57XmlPath=self.e57XmlPath,myattrib=1)
        self.assertEqual(nodes[0].myattrib,1)

        # # with getResource 
        # nodes=tl.e57xml_to_nodes(e57Path=self.e57XmlPath,getResource=True)
        # geometries=[n.resource for n in nodes]
        # self.assertEqual(len(geometries),2)

        #E572
        tl.e57header_to_nodes(e57Path=self.e57Path2)
        self.assertAlmostEqual(nodes[0].cartesianTransform[0,3],0.379,delta=0.01)
        self.assertLess(nodes[0].cartesianTransform[0,0],0)
        self.assertAlmostEqual(nodes[0].cartesianBounds[0],-4.351,delta=0.01)

        # error when invalid extension
        self.assertRaises(ValueError,tl.e57header_to_nodes,e57Path=os.path.join(self.path,'PCD',"myXML.xml") )

        # error when path doesn't exist
        self.assertRaises(ValueError,tl.e57header_to_nodes,e57Path=os.path.join(self.path,'PCD',"myXML.e57")    )

    def test_ifc_to_nodes_errors(self):
        # error when invalid extension
        self.assertRaises(ValueError,tl.ifc_to_nodes,ifcPath=os.path.join(self.path,'IFC',"myXML.xml") )

        # error when path doesn't exist
        self.assertRaises(ValueError,tl.ifc_to_nodes,ifcPath=os.path.join(self.path,'IFC',"myXML.ifc")    )


    def test_ifc_to_nodes(self):
        #IFC1
        nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath1)
        self.assertEqual(len(nodes), 933)
        #IFC2
        #nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath2)
        #self.assertEqual(len(nodes), 0)
        #IFC3
        #nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath3)
        #self.assertEqual(len(nodes), 2301)
        #IFC4
        #nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath4)
        #self.assertEqual(len(nodes), 10873)

    def test_ifc_to_nodes_walls(self):
        #IFC1
        nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath1, classes='.IfcWallStandardCase',getResource=True)
        self.assertEqual(len(nodes), 309)
        geometries=[n.resource for n in nodes]
        self.assertEqual(len(geometries),309)
        
        #IFC2
        #nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath2, classes='.IfcWallStandardCase',getResource=True)
        #geometries=[n.resource for n in nodes]
        #self.assertEqual(len(nodes), 0)
        #IFC3
        #nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath3, classes='.IfcWallStandardCase',getResource=True)
        #geometries=[n.resource for n in nodes]
        #self.assertEqual(len(geometries), 340)
        #IFC4
        #nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath4, classes='.IfcWallStandardCase',getResource=True)
        #geometries=[n.resource for n in nodes]
        #self.assertEqual(len(geometries), 1603)

    def test_ifc_to_nodes_slabs(self):
        #IFC1
        nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath1, classes='.IfcSlab',getResource=True)
        self.assertEqual(len(nodes), 237)
        geometries=[n.resource for n in nodes]
        self.assertEqual(len(geometries),237)
        #IFC2
        #nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath2, classes='.IfcSlab',getResource=True)
        #geometries=[n.resource for n in nodes]
        #self.assertEqual(len(geometries), 0)
        #IFC3
        #nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath3, classes='.IfcSlab',getResource=True)
        #geometries=[n.resource for n in nodes]
        #self.assertEqual(len(geometries), 1150)
        #IFC4
        #nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath4, classes='.IfcSlab',getResource=True)
        #geometries=[n.resource for n in nodes]
        #self.assertEqual(len(geometries), 415)
    
    def test_ifc_to_nodes_windows_and_doors(self):
      
        #IFC2
        nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath2, classes='.IfcWindow | .ifcDoor',getResource=True)
        geometries=[n.resource for n in nodes]
        self.assertEqual(len(geometries), 0)
        #IFC3
        nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath3, classes='.IfcWindow | .ifcDoor',getResource=True)
        geometries=[n.resource for n in nodes]
        self.assertEqual(len(geometries), 0)
        #IFC4
        nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath4, classes='.IfcWindow | .ifcDoor',getResource=True)
        geometries=[n.resource for n in nodes]
        self.assertEqual(len(geometries), 863)

    def test_nodes_to_graph(self):
        nodes=tl.ifc_to_nodes(ifcPath=self.ifcPath1)
        graph=tl.nodes_to_graph(nodes)
        subjects=[s for s in graph.subjects(RDF.type)]
        self.assertEqual(len(nodes), len(subjects))

    def test_graph_to_nodes(self):
        graph=Graph().parse(self.resourceGraphPath)
        nodes=tl.graph_to_nodes(graph=graph)
        subjects=[s for s in graph.subjects(RDF.type)]
        self.assertEqual(len(nodes),len(subjects))

        #with getResource
        nodes=tl.graph_to_nodes(graph=graph,getResource=True)
        geometries=[n.resource for n in nodes]
        self.assertEqual(len(nodes),len(geometries))

    def test_graphpath_to_nodes(self):
        nodes=tl.graph_path_to_nodes(graphPath=self.resourceGraphPath)
        graph=Graph().parse(self.resourceGraphPath)
        subjects=[s for s in graph.subjects(RDF.type)]
        self.assertEqual(len(nodes),len(subjects))

        #with getResource
        nodes=tl.graph_path_to_nodes(graphPath=self.resourceGraphPath,getResource=True)
        geometries=[n.resource for n in nodes]
        self.assertEqual(len(nodes),len(geometries))

    def test_select_k_nearest_nodes(self):
        nodes=tl.graph_path_to_nodes(graphPath=self.bimGraphPath1,getResource=True)
        list,distances=tl.select_k_nearest_nodes(nodes[0],nodes)
        self.assertEqual(len(list),4)

        #error k<=0
        self.assertRaises(ValueError,tl.select_k_nearest_nodes,node=nodes[0],nodelist=nodes,k=-5 )

    def test_select_nodes_with_centers_in_radius(self):
        nodes=tl.graph_path_to_nodes(graphPath=self.bimGraphPath2,getResource=True)
        list,distances=tl.select_nodes_with_centers_in_radius(nodes[0],nodes,r=10)
        self.assertEqual(len(list),1)
        for d in distances:
            self.assertLess(d,10)

        #error r<=0
        self.assertRaises(ValueError,tl.select_nodes_with_centers_in_radius,nodes[0],nodes,r=0 )
        self.assertRaises(ValueError,tl.select_nodes_with_centers_in_radius,nodes[0],nodes,r=-5 )

    def test_select_nodes_with_centers_in_bounding_box(self): 
        nodes=tl.graph_path_to_nodes(graphPath=self.bimGraphPath3,getResource=True)
        list=tl.select_nodes_with_centers_in_bounding_box(nodes[0],nodes,u=5,v=5,w=5)
        self.assertEqual(len(list),1)

        # no nodes
        node=nodes[0]
        del nodes[0]
        list=tl.select_nodes_with_centers_in_bounding_box(node,nodes,u=0,v=0,w=0)
        self.assertIsNone(list)

    def test_select_nodes_with_intersecting_bounding_box(self): 
        nodes=tl.graph_path_to_nodes(graphPath=self.bimGraphPath4,getResource=True)
        list=tl.select_nodes_with_intersecting_bounding_box(nodes[0],nodes,u=5,v=5,w=5)
        self.assertGreater(len(list),0)

        # no nodes
        node=nodes[0]
        del nodes[0]
        list=tl.select_nodes_with_intersecting_bounding_box(node,nodes,u=-2,v=-2,w=-2)
        self.assertIsNone(list)

    def test_select_nodes_with_intersecting_resources(self):

        nodes = tl.graph_path_to_nodes(graphPath=self.resourceGraphPath,getResource=True)
        self.assertEqual(len(nodes),4)
        nodes.extend(tl.graph_path_to_nodes(graphPath=self.bimGraphPath3,getResource=True))
        self.assertEqual(len(nodes),8)

        list= tl.select_nodes_with_intersecting_resources(nodes[0],nodes)
        print(list)
        self.assertEqual(len(list),1)

    def test_get_mesh_representation(self):
        nodes=tl.graph_path_to_nodes(graphPath=self.resourceGraphPath,getResource=True)        
        for n in nodes:
            geometry=tl.get_mesh_representation(n)
            if(geometry is not None):
                self.assertTrue('TriangleMesh' in str(type(geometry)))


if __name__ == '__main__':
    unittest.main()
