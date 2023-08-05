import importlib
from functools import lru_cache
from typing import Any
from drb.core.node import DrbNode
from drb.utils.drb_python_script import exec_with_return
from drb.exceptions.core import DrbException
from drb.xquery import DrbXQuery
from drb.xquery.drb_xquery_utils import DrbQueryFuncUtil
import abc


class Extractor(abc.ABC):
    """
    An extractor represent a mechanism to retrieve a data from a DrbNode.
    """
    @abc.abstractmethod
    def extract(self, node: DrbNode, **kwargs) -> Any:
        """
        Extracts a data from a DrbNode using a specific mechanism associated to
        the extractor. Kwargs elements allowing to inject additional variables
        for the extraction.

        Parameters:
            node (DrbNode): working node to extract data

        Returns:
            Any - the extracted data

        Raises:
            DrbException: if an error occurred during the extraction
        """
        raise NotImplementedError


# TODO factorize class methods to be use in core and here without duplication
class PythonExtractor(Extractor):
    """
    Extracts a data via a Python script.
      - The script will be executed in a specific context containing the target
      DrbNode (``node``)
      - The script must return something (included: ``None``)

    Parameters:
        script (str): the Python script

    Example:
        .. block-code: python

           import datetime
           n = node['MTD_MSIL1C.xml']['Level-1C_User_Product']['General_Info']
           n = n['Product_Info']['PRODUCT_START_TIME']
           date = datetime.datetime.strptime(n.value, '%Y-%m-%dT%H:%M:%S.%fZ')
           return date

    """

    def __init__(self, script: str):
        super().__init__()
        ident = '  '
        code = ident + script.replace('\n', f'\n{ident}')
        self._script = f'def main():\n{code}\nmain()'

    @lru_cache(maxsize=15)
    def extract(self, node: DrbNode, **kwargs) -> Any:
        try:
            return exec_with_return(self._script, node, **kwargs)
        except Exception as ex:
            raise DrbException(
                'An error occurred during an Python extraction') from ex


class XQueryExtractor(Extractor):
    """
    Extracts a data via a XQuery.
    """
    def __init__(self, query: str):
        super().__init__()
        self._query = DrbXQuery(query)

    @lru_cache(maxsize=15)
    def extract(self, node: DrbNode, **kwargs) -> Any:
        value = self._query.execute(node, **kwargs)
        if len(value) == 0:
            return None
        if len(value) == 1:
            return DrbQueryFuncUtil.get_node(value)
        return [DrbQueryFuncUtil.get_node(e) for e in value]


class ConstantExtractor(Extractor):
    """
    Represent a constant, do not perform any extraction.
    """

    def __init__(self, value: Any):
        super().__init__()
        self._value = value

    def extract(self, node: DrbNode, **kwargs) -> Any:
        return self._value


class ScriptExtractor(Extractor):
    """
    Represent a method, to call, this method must take in
    argument a DrbNode.
    """

    def __init__(self, value: str):
        super().__init__()
        self._value = value

    def extract(self, node: DrbNode, **kwargs) -> Any:
        mod, method = self._value.split(':')
        try:
            module = importlib.import_module(mod)
            met = getattr(module, method)
        except (ModuleNotFoundError, AttributeError) as ex:
            raise DrbException(ex)
        return met(node)


__factories = {
        'python': PythonExtractor,
        'xquery': XQueryExtractor,
        'constant': ConstantExtractor,
        'script': ScriptExtractor
    }


def parse_extractor(data: dict):
    for key, value in data.items():
        if key != 'name':
            return __factories[key](value)
