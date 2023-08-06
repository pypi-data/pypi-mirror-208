import pprint
import pandas
from lxml import etree
from flowtask.exceptions import ComponentError
from .abstract import DtComponent


pp = pprint.PrettyPrinter(indent=2)


class XMLtoPandas(DtComponent):
    """
    XMLtoPandas.

    Transform an XML list structure to Pandas
    """

    async def start(self, **kwargs):
        """
        start.

            Get if directory exists
        """
        if self.previous:
            if not isinstance(self.input, list):
                raise ComponentError(
                    f'XMLtoPandas requires a List as input, get {type(self.input)}'
                )
            try:
                if not etree.iselement(self.input[0]):
                    raise ComponentError(
                        'Invalid XML tree'
                    )
            except Exception as exc:
                raise ComponentError(
                    f'Error validating XML tree, error: {exc}'
                ) from exc
            #if is valid:
            self.data = self.input
        else:
            raise ComponentError('Requires an *OpenXML* previous component')

    async def close(self):
        """
        close.

            close method
        """

    def make_dataframe(self, name, data, **kwargs):
        df = None
        params = {}
        if kwargs:
            params = {**params, **kwargs}
        try:
            df = pandas.DataFrame(
                data=data,
                **params
            )
            index = df.index
            index.name = name
            return df
        except ValueError as err:
            raise ComponentError(
                f"Error Parsing Column, error: {err}", status=403
            ) from err
        except Exception as err:
            raise ComponentError(
                "Generic Error on Data: error: {err}", status=501
            ) from err

    def get_childs(self, element, id, parent:dict, name:str=None):
        odata = {}
        dr = {}
        for other in element.iterchildren():
            if name is not None:
                k = name
            else:
                k = other.tag.split('}')[1] if '}' in other.tag else other.tag
            oid = ''
            dr = {}
            if not k in odata.keys():
                odata[k] = []
            for a in other.attrib:
                if a == 'id':
                    nw = '{}{}'.format(k, a.capitalize())
                    oid = nw
                else:
                    nw = a
                dr[nw] = other.attrib[a]
                if hasattr(self, 'add_previous'):
                    if id:
                        dr[id] = parent[id]
                # also we can add other columns too
                if hasattr(self, "add_parent"):
                    for col in self.add_parent:
                        if col in parent:
                            dr[col] = parent[col]
            # can we make recursive?
            # recursive: true
            if hasattr(self, 'recursive') and self.recursive:
                if list(other):
                    #print(list(other))
                    self.get_childs(other, oid, dr)
            else:
                if hasattr(self, 'process_child') and self.process_child:
                    child = other.find(self.process_child)
                    if child is not None:
                        if list(child):
                            # every child gets this name
                            self.get_childs(child, oid, parent=dr, name=self.process_child)
            odata[k].append(dr)
        # have all children on the structure
        result = []
        for key,item in odata.items():
            if key in self._result:
                result = self._result[key]
            self._result[key] = result + item

    async def run(self):
        """
        run.

            Transform the XML list into a Pandas Dataframe
        """
        self._result = {}
        oresult = []
        if self.data:
            for item in self.data:
                if hasattr(self, 'childs') and self.childs is True:
                    # elements to build List come from child elements
                    key = ''
                    data = []
                    for element in item.iterchildren():
                        # Remove namespace prefix
                        key = element.tag.split('}')[1] if '}' in element.tag else element.tag
                        d = {}
                        _id = ''
                        for att in element.attrib:
                            if att == 'id':
                                name = '{}{}'.format(key, att.capitalize())
                                _id = name
                            else:
                                name = att
                            d[name] = element.attrib[att]
                        # recursive: true
                        if hasattr(self, 'recursive'):
                            if list(element):
                                self.get_childs(element, _id, parent=d)
                        # processing categories
                        data.append(d)
                    # append to result
                    self._result[key] = data
                else:
                    # need to process all items one by one
                    key = item.tag.split('}')[1] if '}' in item.tag else item.tag
                    data = {}
                    _id = ''
                    for att in item.attrib:
                        if att == 'id':
                            name = '{}{}'.format(key, att.capitalize())
                            _id = name
                        else:
                            name = att
                        data[name] = item.attrib[att]
                    if hasattr(self, 'recursive'):
                        if list(item):
                            self.get_childs(item, _id, parent=data)
                    else:
                        # item has childs, but I need to recurse
                        if hasattr(self, 'process_child'):
                            child = item.find(self.process_child)
                            if list(child):
                                # every child gets this name
                                self.get_childs(child, _id, parent=data, name=self.process_child)
                    oresult.append(data)
            # check oresult
            if oresult:
                self._result[key] = oresult
            # result full?
            if self._result:
                _iter = []
                for key,item in self._result.items():
                    df = self.make_dataframe(key, item)
                    if isinstance(df, pandas.DataFrame):
                        if not df.empty:
                            _iter.append(df)
                        else:
                            continue
                    else:
                        print(
                            f'Empty Dataframe for -{key}-'
                        )
                        continue
                self._result = _iter
                return self._result
            else:
                self._result = []
                return False
        else:
            # nothing
            return False
