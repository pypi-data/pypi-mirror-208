# -*- coding: utf-8 -*-
from adabrain.common.interface.ant1.query_handler import QueryHandlerParamsBuilder
from adabrain.common.ms.plugin import PluginBase


class DemoPlugin(PluginBase):
    def __init__(self, param):
        super().__init__(param)
        self.__msg = ""
        self.__result = ""
        
    def process(self, params):
        self.builder = QueryHandlerParamsBuilder()
        '''
        query = self.builder.request_query(params)
        self.builder.set_fst_extended_query("FST_QUERY")
        '''
        self.__result = self.builder.get_output()
        print(self.__result)
        return 0

    def err_msg(self):
        return self.__msg

    def result(self):
        return self.__result