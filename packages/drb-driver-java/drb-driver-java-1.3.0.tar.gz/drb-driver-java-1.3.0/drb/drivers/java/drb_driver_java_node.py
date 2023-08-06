import io
from typing import Any, List

from deprecated.classic import deprecated
from drb.core import DrbNode
from drb.exceptions.core import DrbNotImplementationException, DrbException
from drb.core.path import ParsedPath
from drb.nodes.abstract_node import AbstractNode

from drb.drivers.java.drb_driver_java_call import JavaCall, InputStream, \
    PythonStreamToJava, DrbFactoryResolverJava
from drb.drivers.java.drbdriver_java_stream import JavaStream


class DrbJavaNode(AbstractNode):

    def __init__(self, parent: DrbNode, node_java):
        super().__init__()
        self.parent = parent
        self._children: List[DrbNode] = None
        self._node_java = node_java
        self._node_java_stream = None
        self.__stream_java = None
        self.__init_node()
        self._available_impl = [
            io.BytesIO
        ]

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, item):
        raise NotImplementedError

    def __init_node(self):
        self.name = self.node_java.getName()
        self.namespace_uri = self.node_java.getNamespaceURI()
        call = JavaCall()
        java_value = self.node_java.getValue()
        if java_value:
            value_python = call.cast_value_to_native_type(java_value)
            self.value = value_python
        list_attributes = self.node_java.getAttributes()
        if list_attributes is not None:
            number_atr = list_attributes.getLength()
            for index in range(number_atr):
                java_attr = list_attributes.item(index)
                call = JavaCall()
                # TODO manage different type of value instead only string...
                java_value = call.cast_value_to_native_type(
                    java_attr.getValue())
                self @= (java_attr.getName(), java_value)

    @property
    def node_java(self):
        return self._node_java

    @property
    @deprecated(version='2.1.0')
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            java_node = self.node_java
            if java_node is not None:
                number_children = self.node_java.getChildrenCount()

                for index in range(number_children):
                    child_node = self.node_java.getChildAt(index)
                    self._children.append(DrbJavaNode(self, child_node))
        return self._children

    def has_impl(self, impl: type) -> bool:
        if issubclass(io.BytesIO, impl):
            call = JavaCall()
            node_impl = call.cast_to_drb_node_impl(self.node_java)
            if node_impl.hasImpl(InputStream):
                return True
        return False

    def get_impl(self, impl: type, **kwargs) -> Any:
        if self.has_impl(impl):
            try:
                call = JavaCall()
                node_impl = call.cast_to_drb_node_impl(self.node_java)
                input_stream = node_impl.getImpl(InputStream)
                if input_stream is None:
                    return None
                byte_io = JavaStream(input_stream)
                return byte_io
            except Exception as error:
                raise DrbNotImplementationException(f'no {impl} '
                                                    f'implementation found')

        raise DrbNotImplementationException(f'no {impl} '
                                            f'implementation found')

    def close(self):
        if self._node_java:
            call = JavaCall()

            node_impl = call.cast_to_drb_node_impl(self.node_java)

            node_impl.close(False)
            self._node_java = None

        if self._node_java_stream is not None:
            call.release_node_java(self._node_java_stream)
            self._node_java_stream = None


class DrbJavaBaseNode(DrbJavaNode):
    call = JavaCall()

    def __init__(self, base_node: DrbNode):
        self.base_node = base_node

        super().__init__(parent=base_node.parent, node_java=None)

    @property
    def node_java(self):
        if self._node_java is None:
            call = JavaCall()

            path_url = ParsedPath(self.base_node.path.name)

            # we have to use BufferIO of base node
            if path_url.scheme is None \
                    or len(path_url.scheme) == 0:
                path_url.scheme = 'file'

            url_path = path_url.name

            # Get IO python
            if self.base_node.has_impl(io.RawIOBase):
                raw = self.base_node.get_impl(io.RawIOBase)
            else:
                raw = self.base_node.get_impl(io.BytesIO)

            raw.seek(0)
            self.__stream_java = PythonStreamToJava(raw)
            # print(str(stream_java.read()))

            self._node_java_stream = \
                call.create_node_stream(url_path, self.__stream_java)

            drb_node = call.cast_to_drb_node(self._node_java_stream)

            real_factory = DrbFactoryResolverJava.resolveImpl(drb_node)
            if real_factory:
                self._node_java = real_factory.open(drb_node)

        return self._node_java
