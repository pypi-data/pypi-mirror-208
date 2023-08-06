import os


# Set it before import JavaCall to indicate that classpath must be adapted
# for test
# Set it before import JavaCall to indicate that classpath must be adapted
# for test
_CLASSPATH_ADDON = os.getenv('CLASSPATH_ADDON')
_HERE = os.path.dirname(__file__)
_HERE = os.pathsep.join([os.path.join(_HERE, "..")])

_PATH_TEST = os.pathsep.join([os.path.join(_HERE, "tests/files/*")])
if _CLASSPATH_ADDON is None:
    os.environ['CLASSPATH_ADDON'] = _PATH_TEST
else:
    os.environ['CLASSPATH_ADDON'] = _PATH_TEST + ":" + _CLASSPATH_ADDON
from drb.drivers.java.drb_driver_java_factory import DrbJavaFactory

import unittest  # noqa: E402
from io import BytesIO, RawIOBase  # noqa: E402
from drb.drivers.file import DrbFileFactory  # noqa: E402
from pathlib import Path  # noqa: E402
from drb.exceptions.core import DrbException  # noqa: E402
from drb.drivers.java import DrbJavaBaseNode  # noqa: E402
from drb.drivers.java.drb_driver_java_call import JavaCall, PythonStreamToJava, \
    DrbFactoryResolverJava  # noqa: E402

# TODO : All test ares skipped due to env_java to set in package


class TestDrbJavaNode(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    path_file_tar = current_path / "files" / "test.tar"
    path_file_xml = current_path / "files" / "simple.xml"
    path_file_xml = current_path / "files" / "MTD_TL.xml"
    path_file_sdf = current_path / "files" / "ceos.dat"

    # @unittest.skip
    def test_create_java_base_node(self):
        self.node_file = DrbFileFactory().create(self.path_file_tar)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)

    @unittest.skip
    def test_create_java_node_sdf(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_sdf)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)

        node_sdf = node_base_java

        self.assertIsNotNone(node_sdf)

        for index_child in range(len(node_sdf)):
            item = node_sdf[index_child]

        self.assertEqual(node_sdf['recordSequenceNumber',
                                  'http://www.gael.fr/schemas/ceos'].name,
                         'recordSequenceNumber')
        self.assertEqual(node_sdf['recordSequenceNumber',
                                  'http://www.gael.fr/schemas/ceos'].value,
                         16777216)
        self.assertEqual(node_sdf['secondRecordSubTypeCode',
                                  'http://www.gael.fr/schemas/ceos'].value,
                         18)

        has_impl = node_sdf['recordSequenceNumber',
                            'http://www.gael.fr/schemas/ceos']\
            .has_impl(BytesIO)

    # @unittest.skip
    def test_create_java_node_children(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_tar)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)

        node_tar = node_base_java

        self.assertEqual(len(node_tar), 1)

        self.assertEqual(node_tar[0].name, 'test')

        self.assertEqual(node_tar[0]['a'].name, 'a')

        self.assertEqual(node_tar[0]['a']['aaa.txt'].name, 'aaa.txt')

        self.assertEqual(len(node_tar[0]['a']), 1)
        self.assertEqual(len(node_tar[0]['xml']), 2)

    # @unittest.skip
    def test_create_get_value_none(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_tar)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)

        node_tar = node_base_java

        self.assertEqual(node_tar[0].name, 'test')
        self.assertIsNone(node_tar[0].value)

    # @unittest.skip
    def test_create_get_attributes(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_tar)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)

        node_tar = node_base_java

        self.assertEqual(node_tar.get_attribute('directory', None), False)

        with self.assertRaises(DrbException):
            node_tar.get_attribute('test', None)

        list_attributes = node_tar.attributes

    # @unittest.skip
    def test_node_stream_impl(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_tar)
        self.node_file.path.scheme = 'file'

        url_path = self.node_file.path.name

        call = JavaCall()

        raw = self.node_file.get_impl(RawIOBase)

        stream_java = PythonStreamToJava(raw)
        node_java = call.create_node_stream(url_path, stream_java)

        drb_node = call.cast_to_drb_node(node_java)

        # url_node = call.create_node_url(url_path)
        # drb_node_for_resolve = call.cast_to_drb_node(url_node)

        real_factory = DrbFactoryResolverJava.resolveImpl(drb_node)

        node_java = real_factory.open(drb_node)

    # @unittest.skip
    def test_java_node_has_child(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_xml)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)
        node_xml = node_base_java

        self.assertTrue(node_xml.has_child())
        self.assertTrue(node_xml[0].has_child())

    # @unittest.skip
    def test_java_node_path(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_xml)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)
        node_xml = node_base_java

        self.assertEqual(node_xml.path.name,
                         str(self.path_file_xml) + '/' + 'MTD_TL.xml')
        self.assertEqual(str(node_xml[0].path.name),
                         str(self.path_file_xml) + '/MTD_TL.xml/' + node_xml[0].name)

    # @unittest.skip
    def test_java_node_parent(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_xml)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)
        node_xml = node_base_java

        self.assertEqual(node_xml.parent, self.node_file.parent)
        node_base_java.close()

    # @unittest.skip
    def test_java_node_close(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_xml)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)
        node_xml = node_base_java

        self.assertEqual(node_xml.parent, self.node_file.parent)

        node_child = node_xml[0]

        node_xml.close()
        node_base_java.close()

    # @unittest.skip
    def test_input_value_java_node(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_xml)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)
        node_xml = node_base_java

        child_not_empty = node_xml[0][0][0]
        if self.path_file_xml.name.startswith('simple'):
            self.assertEqual(child_not_empty.value, 'Belgian Waffles')
        else:
            self.assertEqual(child_not_empty.value,
                             'S2B_OPER_MSI_L1C_TL_VGS4_20210913T120150'
                             '_A023615_T30UWU_N03.01')

        node_xml.close()
        node_base_java.close()

    # @unittest.skip
    def test_drb_Factory(self):
        

        call = JavaCall()

        url_node = call.create_node_url('file://' + str(self.path_file_tar))
        drb_node = call.cast_to_drb_node(url_node)

        real_factory = DrbFactoryResolverJava.resolveImpl(drb_node)

        node = real_factory.open(drb_node)

    # @unittest.skip
    def test_JavaStream_read(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_tar)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)
        node_tar = node_base_java
        child_first = node_tar[0]

        child_not_empty = child_first['not-empty.file']

        impl = child_not_empty.get_impl(BytesIO)
        self.assertIsNotNone(impl)

        bytes_arr = impl.read()
        byte_ret = bytearray(bytes_arr)

        while len(bytes_arr) > 0:
            bytes_arr = impl.read()
            if len(bytes_arr) > 0:
                byte_ret.append(bytes_arr)

        self.assertEqual(byte_ret, bytearray(b'NOT-emptY\n'))

        child_xml = node_tar[0]['xml']['a_xml']
        impl.close()
        impl = child_xml.get_impl(BytesIO)

        bytes_arr = impl.read()
        byte_ret = bytearray(bytes_arr)

        bytes_arr = impl.read()
        if len(bytes_arr) > 0:
            byte_ret.append(bytes_arr)
        self.assertEqual(byte_ret,
                         bytearray(b'\n<xml1>\n   <x>\n      '
                                   b'XML1!!\n   </x>\n</xml1>\n'))
        self.assertEqual(byte_ret.decode("utf-8"),
                         '\n<xml1>\n   <x>\n      '
                         'XML1!!\n   </x>\n</xml1>\n')

        impl.close()
        node_tar.close()
        node_base_java.close()

    # @unittest.skip
    def test_JavaStream_seek(self):
        self.node_file = DrbFileFactory().create(self.path_file_tar)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)
        node_tar = node_base_java

        
        child_xml = node_tar[0]['xml']['a_xml']

        impl = child_xml.get_impl(BytesIO)

        self.assertTrue(impl.readable())
        impl.read(4)
        impl.seek(11)
        bytes_arr = impl.read1(3)
        self.assertEqual(bytes_arr, bytearray(b'<x>'))
        impl.seek(21)
        bytes_arr = impl.read(5)

        self.assertEqual(bytes_arr, bytearray(b'XML1!'))

        impl.close()

        node_tar.close()
        node_base_java.close()

    # @unittest.skip
    def test_JavaStream_tel(self):
        self.node_file = DrbFileFactory().create(self.path_file_tar)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)
        node_tar = node_base_java

        
        child_xml = node_tar[0]['xml']['a_xml']

        impl = child_xml.get_impl(BytesIO)
        impl.read(4)
        impl.read1(3)

        self.assertEqual(impl.tell(), 7)

        impl.close()

        node_tar.close()
        node_base_java.close()

    # @unittest.skip
    def test_JavaStream_readinto(self):
        

        self.node_file = DrbFileFactory().create(self.path_file_tar)

        node_base_java = DrbJavaFactory()._create(self.node_file)

        self.assertIsInstance(node_base_java, DrbJavaBaseNode)
        node_tar = node_base_java

        child_not_empty = node_tar[0]['not-empty.file']
        self.assertIsNotNone(child_not_empty)

        # impl = node_tar.get_impl(BytesIO)
        #
        # impl.seek(0)
        # bytes_arr = impl.read()

        impl = child_not_empty.get_impl(BytesIO)
        self.assertIsNotNone(impl)

        impl.seek(0)

        buffer = bytearray(10)
        impl.readinto(buffer)

        self.assertEqual(buffer, bytearray(b'NOT-emptY\n'))

        child_xml = node_tar[0]['xml']['a_xml']
        impl = child_xml.get_impl(BytesIO)
        impl.seek(0)

        buffer = bytearray(14)
        impl.readinto1(buffer)
        self.assertEqual(buffer, bytearray(b'\n<xml1>\n   <x>'))
        self.assertEqual(buffer.decode("utf-8"), '\n<xml1>\n   <x>')

        node_tar.close()
        node_base_java.close()
