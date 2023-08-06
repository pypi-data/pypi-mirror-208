import copy
import os
from pathlib import Path
import shutil
import time
import unittest
import geomapi.tools.progresstools as pt
import geomapi.utils.geometryutils as gmu
import ifcopenshell
import open3d as o3d

################################## SETUP/TEARDOWN MODULE ######################

# def setUpModule():
#     #execute once before the module 
#     print('-----------------Setup Module----------------------')

# def tearDownModule():
#     #execute once after the module 
#     print('-----------------TearDown Module----------------------')

class TestProgressutils(unittest.TestCase):

 ################################## SETUP/TEARDOWN CLASS ######################
  
    @classmethod
    def setUpClass(cls):
        #execute once before all tests
        print('-----------------Setup Class----------------------')
        st = time.time()
        cls.path= Path.cwd() / "test" / "testfiles" 
        
        #POINTCLOUD3
        cls.pcdPath1=cls.path / 'PCD' / "academiestraat week 22 a 20.pcd"     
        cls.pcd= o3d.io.read_point_cloud(str(cls.pcdPath1)) 

        #IFC2
        cls.ifcPath2=cls.path / 'IFC' / "Academiestraat_parking.ifc" 
        ifc2 = ifcopenshell.open(str(cls.ifcPath2))   
        ifcSlab=ifc2.by_guid('2qZtnImXH6Tgdb58DjNlmF')
        ifcWall=ifc2.by_guid('06v1k9ENv8DhGMCvKUuLQV')
        ifcBeam=ifc2.by_guid('05Is7PfoXBjhBcbRTnzewz' )
        ifcColumn=ifc2.by_guid('23JN72MijBOfF91SkLzf3a')
        # ifcWindow=ifc.by_guid(cls.slabGlobalid) 
        # ifcDoor=ifc.by_guid(cls.slabGlobalid)

        #IMG 
        cls.xmlPath1=os.path.join(cls.path,'IMG','camera_position.xml')
        cls.xmlPath2=os.path.join(cls.path,'IMG','cameras_bridge.xml')
        cls.xmlPath3=os.path.join(cls.path,'IMG','cameras_paestum.xml')
        
        #MESH
        cls.slabMesh=gmu.ifc_to_mesh(ifcSlab)
        cls.wallMesh=gmu.ifc_to_mesh(ifcWall)
        cls.beamMesh=gmu.ifc_to_mesh(ifcBeam)
        cls.columnMesh=gmu.ifc_to_mesh(ifcColumn)
        
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

################################## SETUP/TEARDOWN ######################

    def setUp(self):
        #execute before every test
        self.startTime = time.time()   

    def tearDown(self):
        #execute after every test
        t = time.time() - self.startTime
        print('{:50s} {:5s} '.format(self._testMethodName,str(t)))

################################## FIXTURES ######################
    # # @pytest.fixture(scope='module')
    # # @pytest.fixture
    # def test_data(*args):
    #     here = os.path.split(__file__)[0]
    #     return os.path.join(here, "testfiles", *args)

    # @pytest.fixture
    # def e57Path1():
    #     return test_data("pointcloud.e57")

    # @pytest.fixture
    # def ifcData():
    #     ifcPath=os.path.join(os.getcwd(),"testfiles", "ifcfile.ifc")
    #     classes= '.IfcBeam | .IfcColumn | .IfcWall | .IfcSlab'
    #     ifc = ifcopenshell.open(ifcPath)   
    #     selector = Selector()
    #     dataList=[]
    #     for ifcElement in selector.parse(ifc, classes): 
    #         dataList.append(ifcElement)
    #     return dataList

################################## TEST FUNCTIONS ######################


    def test_determine_percentage_of_coverage(self):
        reference=self.pcd
        sources=[self.slabMesh,self.wallMesh,self.columnMesh,self.beamMesh]
        percentages=pt.determine_percentage_of_coverage(sources=sources,reference=reference)
        self.assertEqual(len(percentages), len(sources))
        self.assertLess(percentages[0],0.005)
        self.assertLess(percentages[1],0.001)
        self.assertLess(percentages[2],0.5)
        self.assertLess(percentages[3],0.001)
