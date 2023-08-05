"""Provides a series of helpers to access the DAQ++ soap server."""
import sys
import traceback
import re
import json
import base64
try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            import xml.etree.ElementTree as etree
        except ImportError:
            print("Failed to import ElementTree")

from zeep import Client, Plugin, xsd


def get_service(client, translation):
    """Modify the service address in zeep.

    Args
    ----
        client (zeepClient): the zeep Client object
        translation (list): A pair with the value and its replacement

    Returns
    -------
        [service]: The client service

    """
    if translation:
        service_binding = client.service._binding.name
        service_address = client.service._binding_options['address']
        return client.create_service(
            service_binding,
            service_address.replace(*translation, 1))
    else:
        return client.service


class MyLoggingPlugin(Plugin):
    """Plugin to log debug information like the XML messages."""

    def ingress(self, envelope, http_headers, operation):
        """Called after data is received from server."""
        print(etree.tostring(envelope, pretty_print=True).decode("utf-8"))
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        """Called before data is sent to server."""
        print(etree.tostring(envelope, pretty_print=True).decode("utf-8"))
        return envelope, http_headers


class DAQppClient(object):
    """Create the SOAP client."""

    def __init__(self, ipaddr, port, debug=False):
        """Inititalization of the Client Object.

        Args:
        ----
            ipaddr (string): The IP address of the server
            port (int): The port of the server
            debug (bool, optional): If True runs the client in Debug mode.
                                    Defaults to False.

        """
        host = "http://{host}:{port}/daqpp".format(host=ipaddr, port=port)
        wsdl = "{host}?wsdl".format(host=host)
        translated = "{}:{}".format(ipaddr, port)
        plugin = None
        if debug:
            plugin = [MyLoggingPlugin()]

        self.client = Client(wsdl, plugins=plugin)
        self.client.set_ns_prefix("xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.client.set_ns_prefix("xsd", "http://www.w3.org/2001/XMLSchema")
        self.service = get_service(client=self.client,
                                   translation=(ipaddr, translated))
        self.factory = self.client.type_factory('http://localhost/daqpp/')

    def __getattr__(self, name):
        """Forward commands to the zeep service."""
        return getattr(self.service, name)

    def getAllModules(self):
        """Return a list with all the modules."""
        try:
            return [Module(mid, self) for mid in self.getModuleList(0)]
        except TypeError:
            return []


class SOAPtype(object):
    """Represents a SOAP type."""

    def __init__(self, server):
        """Object initialization.

        Args:
        ----
            server (DAQppClient): A DAQppClient instance wrongly called server.

        """
        self.server = server

    def element(self):
        """Return the SOAP element."""
        return None


class valueType(SOAPtype):
    """A valueType object.

    This is a generic type used in the DAQ++ soap implementation.
    The actual object is in the `item` attribute.

    Attributtes
    -----------
    type : str
        The type of the object
    item
        The actual value

    """

    type_list = {"short": (int, xsd.Short()),
                 "int": (int, xsd.Int()),
                 "long": (int, xsd.Long()),
                 "unsigned short": (int, xsd.UnsignedShort()),
                 "unsigned int": (int, xsd.UnsignedInt()),
                 "unsigned long": (int, xsd.UnsignedLong()),
                 "float": (float, xsd.Float()),
                 "double": (float, xsd.Double()),
                 "string": (str, xsd.String()),
                 "basic_string<char>": (str, xsd.String()),
                 "bool": (bool, xsd.Boolean())
                 }

    xsd_valueType = xsd.ComplexType(
        xsd.Sequence([
            xsd.Element('item',
                        xsd.Any,
                        min_occurs=1,
                        max_occurs='unbounded')
        ]),
        qname=etree.QName("{http://localhost/daqpp/}valueType"))

    def __init__(self, server, value, type):
        """Initializtion.

        Args:
        ----
            server (DAQppClient): The zeep client
            value ([type]): The value
            type ([type]): The type

        """
        super(valueType, self).__init__(server)

        cast, xsdType = valueType.type_list.get(type, (None, None))
        self.type = type

        # print("***\n", self.server.factory.ParameterValue.elements, "\n***")
        values = []
        if cast is None and type == "_object*":
            enc_inp = bytes(json.dumps(value), 'utf8')
            self.item = base64.b64encode(enc_inp)
            self.type = "xsd:string"
            xsdType = xsd.String()
            values.append(xsd.AnyObject(xsd.String(), self.item))

        elif self.type in ("string", "basic_string<char>"):
            self.item = cast(value)
            values.append(xsd.AnyObject(xsd.String(), self.item))

        else:
            try:
                is_array = (len(value) > 1)
            except TypeError:
                is_array = False

            if is_array:
                for val in value:
                    values.append(xsd.AnyObject(xsdType, val))

                self.item = [x for x in value]

            else:
                values.append(xsd.AnyObject(xsdType, value))
                self.item = value

        item_type = str(xsdType._default_qname).replace("{http://www.w3.org/2001/XMLSchema}", "xsd:")
        if (len(values) > 1):
            elem = etree.Element("item", attrib={'{http://www.w3.org/2001/XMLSchema-instance}type': "ns0:valueType"})
            for val in values:
                item = etree.SubElement(elem, "item",
                                        attrib={'{http://www.w3.org/2001/XMLSchema-instance}type': item_type})
                try:
                    item.text = val.value
                except TypeError:
                    item.text = str(val.value)

            self._elem = server.factory.valueType(elem)

        else:
            elem = etree.Element("item", attrib={'{http://www.w3.org/2001/XMLSchema-instance}type': item_type})
            try:
                elem.text = values[0].value
            except TypeError:
                elem.text = str(values[0].value).lower()

            self._elem = server.factory.valueType(elem)

        # self._elem = dict(self.server.factory.ParameterValue.elements)['value'](*values)
        # self._elem = server.factory.valueType(_value_1={"item":values})
        # self._elem = valueType.xsd_valueType(item=values, available_kwargs={})

    def element(self):
        """Return the XML element of the SOAP object."""
        return self._elem


class ParameterValue(SOAPtype):
    """Represents a Parameter value.

    Attributtes:
    -----------
    name
        The name of the parameter
    type
        The type of the parameter
    value
        The value of the parameter

    """

    vvector = re.compile("vector<(?P<type>\w+).*>")

    def __init__(self, server, name, value, type):
        """Initialization.

        Args:
        ----
            server (DAQppClient): the server
            name : The name of the parameter
            value : The value of the parameter
            type : The type

        """
        super(ParameterValue, self).__init__(server)
        self.name = name
        ss = ParameterValue.vvector.search(type)
        if ss:
            self.type = ss.group("type")
        else:
            self.type = type

        self.value = valueType(server, value, self.type)
        self._elem = self.server.factory.ParameterValue(name=self.name,
                                                        type=self.type,
                                                        value=self.value.element())

    def element(self):
        """Return the XML element of the SOAP object."""
        return self._elem


class SOAPParam(SOAPtype):
    """Represents a SOAP Parameter type.

    Attributes
    ----------
    daqid
        the  ID of the owner (DAQpp::Object)
    value : ParameterValue
        The value as a Parameter value

    """

    def __init__(self, server, daqid, name, value, type):
        """Initialization.

        Args:
        ----
            server (DAQppClient): The SOAP client
            daqid : The ID of the owner
            name : The name of the parameter
            value : The value
            type : The type

        """
        super(SOAPParam, self).__init__(server)

        self.daqid = daqid
        self.value = ParameterValue(server, name, value, type)
        self._elem = self.server.factory.Parameter(daqid=self.daqid,
                                                   value=self.value.element())

    def element(self):
        """Return the XML element of the SOAP object."""
        return self._elem


class Parameter(object):
    """A parsed Parameter.

    Attributes
    ----------
    name:
        the parameter name
    obj:
        the daqid of the parameter owner
    type:
        the type of the parameter
    value:
        the actual value

    """

    vvector = re.compile("vector<(?P<type>\w+).*>")

    def __init__(self, name, obj, server=None, input=None):
        """Initialization.

        Args:
        ----
            name (str): The name of the DAQ++ Parameter
            obj (str): The DAQid of the owner
            server (DAQppClient, optional): The soap client. Defaults to None.
            input (object, optional): An object, ussually a string, from where
                                      the parameter value can be build.
                                      Defaults to None.

        """
        self.name = name
        self.obj = obj
        self.server = server
        self.type = None
        self.is_vector = None
        self.value = None
        if self.server is not None:
            self.value = self.get_value()
        elif input:
            self.value = self.decode(input)

    def __str__(self):
        """Return a string representation."""
        return "Parameter %s@%s: %s" % (self.name, self.obj, self.value)

    def get_value(self):
        """Get the parameter value from the server."""
        if self.server is None:
            return None

        par = self.server.getParameter(
            parID={"holderID": self.obj, "parName": self.name})
        return self.decode(par)

    def set_value(self, value):
        """Set the parameter value in the server.

        Args:
        ----
        value: the new value

        """
        if self.server is None:
            return

        par_value = SOAPParam(self.server, self.obj,
                              self.name, value, self.type)

        self.server.setParameter(par_value.element())

    def decode(self, par):
        """Decode the parameter.

        Helper function to parse the Parameter as returned by the SOAP server.

        Args:
        ----
        par: the answer of the server

        """
        if not self.type:
            self.type = par.value.type
            if self.type.find("::string") >= 0 or self.type.find("basic_string<char>") >= 0:
                self.type = "string"

            self.is_vector = (self.type.find("vector<") >= 0)

        if self.is_vector:
            return par.value.value['_value_1'][0]['_value_1']

        else:
            try:
                if self.type == "_object*":
                    if len(par.value.value['_value_1']) == 0:
                        return par.value.value['_value_1']
                    else:
                        return json.loads(par.value.value['_value_1'][0])

                else:
                    if par.value.value is not None:
                        if len(par.value.value['_value_1']) == 0:
                            return par.value.value['_value_1']
                        else:
                            return par.value.value['_value_1'][0]
                    else:
                        return None

            except Exception:
                print("Exception in user code:")
                print('-' * 60)
                print('Parameter: ', par.value.name)
                traceback.print_exc(file=sys.stdout)
                print('-' * 60)
                return None


class Status(object):
    """The status of a DAQObject.

    Attributtes
    -----------
    They are created automatically from attr_list

    """

    attr_list = {'status': lambda x: x,
                 'nwritten': int,
                 'name': lambda x: x,
                 'daqid': lambda x: x,
                 'ntrigger': int,
                 'rate': float,
                 'nexpected': int,
                 'throughput': float,
                 'time': float,
                 'eff': float}

    def __init__(self, response):
        """Initialization from server message.

        Args:
        ----
        response: the response from the server.

        """
        for attr, cast in Status.attr_list.items():
            setattr(self, attr, cast(getattr(response, attr)))

    def __str__(self):
        """Create a string representation."""
        rate = self.rate
        rate_units = " Hz"
        thr_units = " Mb/s"

        if rate > 1.e6:
            rate /= 1.e6
            rate_units = "MHz"

        elif rate > 1000.0:
            rate /= 1000.
            rate_units = "kHz"

        if self.time > 0:
            throughput = self.throughput / self.time
        else:
            throughput = 0.0

        if throughput > 1048576.0:
            throughput /= 1048576.0
            thr_units = "Mb/s"
        elif throughput > 1024.0:
            throughput /= 1024.0
            thr_units = "kb/s"
        elif throughput > 1.0:
            thr_units = "b/s"
        else:
            throughput *= 1024
            thr_units = " mb/s"

        out = "Evts %7d time %6.1f rate %8.1f %s eff %5.1f - %7.1f %s" % \
            (self.ntrigger, self.time, rate, rate_units,
             self.eff, throughput, thr_units)

        return out


class DAQObject(object):
    """A DAQObject."""

    def __init__(self, name, server):
        """Initialization.

        Args:
        ----
            name ([type]): [description]
            server ([type]): [description]

        """
        self.server = server
        self.name = name
        self.parameters = {}

        par = server.getParameterNames(daqid=name)
        if par is not None:
            try:
                for name in par:
                    self.parameters[name] = Parameter(name, self.name, server)
            except AttributeError:
                pass

    def getStatus(self):
        """Get the status from the server.

        Returns
        -------
        the status of the DAQObject.

        """
        try:
            res = self.server.getStatus(daqid=self.name)
            return Status(res)
        except Exception as e:
            print(e)
            return None

    def getMonitorData(self):
        """Get the monitor data from the server.

        Returns
        -------
        The monitor data. It is up to the user to decode this.

        """
        rc = self.server.getMonitorData(daqid=self.name)
        return rc

    def resetMonitorData(self, flags=0):
        """Reset the monitor data in the server."""
        self.server.resetMonitorData(daqid=self.name, flags=flags)


class Module(DAQObject):
    """A Module"""

    def __init__(self, name, server):
        """Initialization.

        Args:
        ----
            name (str): The DAQid of the Module
            server (DAQppClient): the SOAP client

        """
        super(Module, self).__init__(name, server)

    def isLocal(self):
        """Teels if modulesis in local."""
        rc = self.server.isLocal(daqid=self.name)
        return rc

    def setLocal(self, state, runManager):
        """Sets the module in local or global.

        Args:
        ----
            state: if true sets the module in local. If false,
                   the module in set in global (main run manager).

        """
        rc = self.server.setLocal(daqid=self.name, state=state, runManager=runManager)
        return rc


class RunManager(DAQObject):
    """A RunManager."""

    def __init__(self, name, server):
        """Initialization.

        Args:
        ----
            name (str): The DAQid of the RunManager
            server (DAQppClient): the SOAP client

        """
        super(RunManager, self).__init__(name, server)

    def startRun(self):
        """Start a run for this RunManager."""
        self.server.StartRunManager(daqid=self.name)

    def stopRun(self):
        """Stop the run."""
        self.server.StopRunManager(daqid=self.name)

    def GetReady(self):
        """Send GetREady command."""
        self.server.GetReady(daqid=self.name)

    def Pause(self):
        """Send Pause command."""
        self.server.Pause(daqid=self.name)

    def Continue(self):
        """Send the Pause command."""
        self.server.Continue(daqid=self.name)

    def Reset(self):
        """Send the Reset command."""
        self.server.Reset(daqid=self.name)

    def setMaxEvents(self, max_events):
        """Sets the maximum number of events for the run.

        Args:
        ----
        max_events: the max. number of events.
                    If <=0, it willbe an infinite run.

        """
        self.server.setMaxEvents(maxEvents={"daqid": self.name,
                                            "nevts": max_events})

    def setRunDuration(self, duration):
        """Set the maximum Run duration.

        Args:
        ----
        duration:  the duration of the run in seconds.

        """
        self.server.setRunDuration(runDuration={"daqid": self.name,
                                                "duration": duration})

    def getModules(self):
        """Get the lis of modules."""
        modlist = {}
        try:
            for m in self.server.getRunManagerModules(daqid=self.name):
                modlist[m] = Module(m, self.server)
        except TypeError:
            pass

        return modlist


def parse_update(out):
    """Parse the output of the sendUpdate command.

    Args:
    ----
    out: the ouput of the sendUpdate command.

    Returns
    -------
    A tuple (status, parameters) where
        - status is a list of the most recent status changes and
        - parameters a list of the recently modified parameters

    """
    status = []
    parameters = []

    # Get the list of status
    sl = out.status
    if sl is None:
        # empty, do nothing
        pass
    elif isinstance(sl.status, list):
        for st in sl.status:
            status.append(Status(st))
    else:
        status.append(Status(sl.status))

    pl = out.parameters
    if pl is None:
        # empty, do nothing
        pass
    elif isinstance(pl.parameter, list):
        for par in pl.parameter:
            if par.daqid is None:
                continue

            parameters.append(Parameter(par.value.name, par.daqid, input=par))
    else:
        par = pl.parameter
        parameters.append(Parameter(par.value.name, par.daqid, input=par))

    return status, parameters


if __name__ == "__main__":
    S = DAQppClient("localhost", 50000)
    modules = S.getModuleList(0)
    print("Found the following modules:", modules)
    M = []
    for name in modules:
        print("name: ", name)
        m = DAQObject(name, S)
        print(m.parameters['pedestals'])
        M.append(m)
