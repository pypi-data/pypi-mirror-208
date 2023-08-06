import logging
import os
import platform
import importlib.resources as resources
import jnius_config
from drb.core.path import ParsedPath
from drb.utils.plugins import get_entry_points


def __retrieve_classpath():
    """
    Retrieve all declared Java libraries via the entry point `drb.driver.java`
    in the Python environment.

    Returns:
        list: Absolute path list of declared Java libraries
    """
    jar_paths = []
    major, minor, patch = platform.python_version().split('.', maxsplit=3)
    for ep in get_entry_points('drb.driver.java'):
        ext = f'.{ep.name}'
        if int(minor) > 8:
            t = resources.files(ep.value)
            jars = map(lambda x: resources.as_file(t.joinpath(x)),
                       filter(lambda x: str(x).endswith(ext), t.iterdir()))
        else:
            jars = map(
                lambda x: resources.path(ep.value, x),
                filter(lambda x: x.endswith(ext), resources.contents(ep.value))
            )

        for path in jars:
            with path as p:
                jar_paths.append(str(p.absolute()))
    return jar_paths


def __initialize_jnius_classpath():
    lib_venv = os.path.join(os.getenv('VIRTUAL_ENV', ''), "javalib/*")
    lib_custom = os.getenv('CLASSPATH_ADDON', '')
    jnius_config.add_classpath(lib_venv)
    for jar_path in __retrieve_classpath():
        jnius_config.add_classpath(jar_path)
    for _CLASSPATH_ADDON_PATH in lib_custom.split(':'):
        jnius_config.add_classpath(_CLASSPATH_ADDON_PATH)


__initialize_jnius_classpath()


from jnius import autoclass  # noqa: E402
import jnius  # noqa: E402


StringTypeDrbClass = autoclass("fr.gael.drb.value.String")
SystemClass = autoclass("java.lang.System")
URLClass = autoclass("java.net.URL")
InputStream = autoclass("java.io.InputStream")
DrbFactory = autoclass("fr.gael.drb.DrbFactory")
URLNode = autoclass("fr.gael.drb.impl.URLNode")
DrbFactoryResolverJava = autoclass("fr.gael.drb.impl.DrbFactoryResolver")
DrbCortexMetadataResolver = autoclass(
    "fr.gael.drbx.cortex.DrbCortexMetadataResolver")
DrbCortexModel = autoclass("fr.gael.drbx.cortex.DrbCortexModel")
DrbNodeImpInputStream = autoclass(
    "fr.gael.drb.impl.interface_python.DrbNodeImpInputStream")
ListDrbNodeImpInputStream = autoclass(
    "fr.gael.drb.impl.interface_python.ListDrbNodeImpInputStream")
DrbNodeImpInputStreamCopy = autoclass(
    "fr.gael.drb.impl.interface_python.DrbNodeImpInputStreamCopy")
ByteArrayInputStream = autoclass("java.io.ByteArrayInputStream")
PythonByteList = autoclass("fr.gael.drb.impl.interface_python.PythonByteList")


class JavaCall:
    """
    A JavaCall make all call java, all java call must be here
    because 'jnius' must be initialize only one time in library.
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(JavaCall, cls).__new__(cls)
            cls.logger = logging.getLogger("java-call")

            cls.model = DrbCortexModel.getDefaultModel()
            DrbFactoryResolverJava.setMetadataResolver(
                DrbCortexMetadataResolver(cls.model))
        return cls.__instance

    @staticmethod
    def create_node_url(path):
        java_url = URLClass(path)
        return URLNode(java_url)

    @staticmethod
    def create_node_stream(path: ParsedPath, stream_java):
        """
        Create a java node DrbNodeImpInputStream.
        :param path: url used to pass it the java node
        :param stream_java: content of the node
        :returns: DrbNodeImpInputStream node in java
        """
        # stream_java.reset()
        java_url = URLClass(path)

        java_node = DrbNodeImpInputStream(java_url, stream_java)

        ListDrbNodeImpInputStream.referenceNode(java_node)

        return java_node

    @staticmethod
    def release_node_java(java_node):
        """
        Indicate we no more use the java object java_node
        this allows java garbage collector to freed the java object
        :param java_node: object java node to release
        """
        ListDrbNodeImpInputStream.unReferenceNode(java_node)

    # @staticmethod
    # def create_node_stream_copy(path, buffer_io):
    #     """create a java node DrbNodeImpInputStream.
    #         use only for test, because make a readall of
    #         buffer_io to create java stream
    #
    #          :param path: url used to pass it the java node
    #          :param buffer_io: content of the node
    #
    #          :returns: DrbNodeImpInputStream node in java
    #     """
    #     bytes_buff = buffer_io.readall()
    #     stream_java = ByteArrayInputStream(bytes_buff)
    #     stream_java.skip(0)
    #     java_url = URLClass(path)
    #     return DrbNodeImpInputStreamCopy(java_url, stream_java)

    @staticmethod
    def cast_value_to_string(java_value):
        java_value_string = jnius.cast("fr.gael.drb.value.String",
                                       java_value.convertTo(7))
        return java_value_string.toString()

    @staticmethod
    def cast_value_to_native_type(java_value, type=None):
        """
        Convert value or attributes java to similar type in python
        :param java_value: object java node to release
        :param type: force a type
        :returns: Value in python type
        """
        if type is None:
            type = java_value.getType()
        if type == 0:
            java_value_typed = jnius.cast("fr.gael.drb.value.Boolean",
                                          java_value)
            return java_value_typed.booleanValue()
        elif type == 1:
            java_value_typed = jnius.cast("fr.gael.drb.value.Byte",
                                          java_value)
            return java_value_typed.byteValue()
        elif type == 2:
            java_value_typed = jnius.cast("fr.gael.drb.value.Short",
                                          java_value)
            return java_value_typed.shortValue()
        elif type == 3 or type == 11:
            java_value_typed = jnius.cast("fr.gael.drb.value.Int",
                                          java_value)
            return java_value_typed.intValue()
        elif type == 4:
            java_value_typed = jnius.cast("fr.gael.drb.value.Long",
                                          java_value)
            return java_value_typed.longValue()
        elif type == 5:
            java_value_typed = jnius.cast("fr.gael.drb.value.Float",
                                          java_value)
            return java_value_typed.floatValue()
        elif type == 6:
            java_value_typed = jnius.cast("fr.gael.drb.value.Double",
                                          java_value)
            return java_value_typed.doubleValue()
        elif type == 7:
            java_value_typed = jnius.cast("fr.gael.drb.value.String",
                                          java_value)
            return java_value_typed.toString()
        elif type == 8:
            java_value_typed = jnius.cast("fr.gael.drb.value.DateTime",
                                          java_value)
            return java_value_typed.getTime()
        elif type == 9:
            java_value_string = jnius.cast("fr.gael.drb.value.String",
                                           java_value.convertTo(7))
            return int(java_value_string.toString())
        elif type == 10:
            array_python = []
            java_value_typed = jnius.cast(
                "fr.gael.drb.value.AbstractValueArray", java_value)
            for index in range(java_value_typed.getLength()):
                item = java_value_typed.getElement(index)
                array_python.append(item)
            return array_python
        # 11 binary int see 3...
        elif type == 12:
            java_value_typed = jnius.cast("fr.gael.drb.value.UnsignedByte",
                                          java_value)
            return java_value_typed.byteValue()
        elif type == 13:
            java_value_typed = jnius.cast("fr.gael.drb.value.UnsignedShort",
                                          java_value)
            return java_value_typed.shortValue()
        elif type == 14:
            java_value_typed = jnius.cast("fr.gael.drb.value.UnsignedInt",
                                          java_value)
            return java_value_typed.intValue()
        elif type == 15:
            java_value_typed = jnius.cast("fr.gael.drb.value.UnsignedLong",
                                          java_value)
            return java_value_typed.longValue()
        elif type == 16:
            java_value_typed = jnius.cast("fr.gael.drb.value.Duration",
                                          java_value)
            double = java_value_typed.convertTo(6)
            double = jnius.cast("fr.gael.drb.value.Double", double)
            return double.doubleValue()
        elif type == 17:
            java_value_typed = jnius.cast("fr.gael.drb.value.DayTimeDuration",
                                          java_value)
            double = java_value_typed.convertTo(6)
            double = jnius.cast("fr.gael.drb.value.Double", double)
            return double.doubleValue()
        elif type == 18:
            java_value_typed = jnius.cast(
                "fr.gael.drb.value.YearMonthDuration", java_value)
            double = java_value_typed.convertTo(6)
            double = jnius.cast("fr.gael.drb.value.Double",
                                double)
            return double.doubleValue()
        elif type == 26:
            java_value_typed = jnius.cast("fr.gael.drb.value.Decimal",
                                          java_value)
            return java_value_typed.doubleValue()
        elif type == 27:
            java_value_typed = jnius.cast("fr.gael.drb.value.Integer",
                                          java_value)
            return int(java_value_typed.toString())
        return JavaCall.cast_value_to_string(java_value)

    @staticmethod
    def get_auto_class(java_class):
        return autoclass(java_class)

    @staticmethod
    def cast_to_drb_node(node_java):
        node_drb = jnius.cast("fr.gael.drb.DrbNode",  node_java)
        return node_drb

    @staticmethod
    def cast_to_drb_node_impl(node_java):
        node_drb_impl = jnius.cast("fr.gael.drb.impl.DrbNodeImpl",  node_java)
        return node_drb_impl


class PythonStreamToJava(jnius.PythonJavaClass):
    """
    A Java Class derived from interface java
    allow to read a BytesIO python under a stream java like InputStream
    be careful to garbage collector of python and java
    java object are managed by java, even if we used it on python
    and in the other side python object are freed by garbage collector python
    even if they are used in JVM
    """
    __javainterfaces__ = \
        ['fr/gael/drb/impl/interface_python/StreamPythonInterface']

    def __init__(self, buffer_io):
        super(PythonStreamToJava, self).__init__()
        self.buffer_io = buffer_io
        self.pos = 0

    @jnius.java_method('()I')
    def read(self):
        byte_read = self.buffer_io.read(1)
        if len(byte_read) == 0:
            return -1
        int_read = int.from_bytes(byte_read, "big")
        return int_read

    @jnius.java_method('()V')
    def reset(self):
        self.buffer_io.seek(0)

    @jnius.java_method('(J)J')
    def skip(self, pos):
        self.buffer_io.seek(pos, os.SEEK_CUR)

    @jnius.java_method('()I')
    def readByte(self):
        byte_read = self.buffer_io.read(1)

        if len(byte_read) == 0:
            return -1
        return byte_read[0]

    @jnius.java_method(
        '(Lfr/gael/drb/impl/interface_python/PythonByteList;I)I')
    def readBuffer(self, python_buf, size_to_read):
        python_buf_var = python_buf

        byte_read = self.buffer_io.read(size_to_read)
        readed = len(byte_read)
        if readed <= 0:
            return -1

        # debug
        # print('readed ' + str(readed) + ": " + 'ask :' + str(size_to_read))

        python_buf_var.append_elements(byte_read, readed)

        # debug
        # print('read ' + str(readed) + ": " + str(size_to_read))

        return readed
