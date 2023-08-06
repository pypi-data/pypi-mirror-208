# JavaNode driver
The drb-driver-java python module aims to wrap Java version of DRB model. It is
able to navigates among java nodes content.

See [documentation]() for details.
# Library usage 
**Java** (JDK) must be present in the system and the `JAVA_HOME` environment
variable must be set.

## Installation
Installing this library with execute the following in a terminal
```shell
pip install drb-driver-java
```

## Configuration
### Automatic
The classpath is initialized retrieving Java libraries using a specific entry
point `drb.driver.java` where:
 - name: represent the Java library package extension (e.g. jar)
 - value: represent the package where Java libraries are stocked

The following example will retrieve all `jar` files resources from the Python
package `my.package.classpath`:
```python
from setuptools import setup

setup(
    entry_points={
        'drb.driver.java': 'jar = my.package.classpath'
    },
    # Other setuptools.setup parameters
)
```

### Manual
To add custom Java libraries to the JVM classpath, please configure
``CLASSPATH_ADDON`` environment variable. It contains absolute path of
additional Java libraries
```shell
export CLASSPATH_ADDON=$CLASSPATH_ADDON:/path/to/my/custom/java/lib
```

## Java Factory and Java Node
The module implements the basic factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.driver`.<br/>
The driver name is `java`.<br/>
The factory class `DrbJavaFactory` is encoded into `drb.drivers.factory`

The java factory creates a JavaNode from an existing java content. It uses a base node to access the content data using a streamed implementation from the base node.

The base node can be a DrbFileNode, DrbHttpNode, DrbTarNode or any other nodes able to provide streamed (`BufferedIOBase`, `RawIOBase`, `IO`) java content.
## limitations
The current version does not manage child modification and insertion. JavaNode is currently read only.
## Using this module
To include this module into your project, the `drb-driver-java` module shall be referenced into `requirements.txt` file, or the following pip line can be run:
```commandline
pip install drb-driver-java
```
Set eventually environment variable ``CLASSPATH_ADDON`` and ``JAVA_HOME``

[documentation]: https://drb-python.gitlab.io/impl/java