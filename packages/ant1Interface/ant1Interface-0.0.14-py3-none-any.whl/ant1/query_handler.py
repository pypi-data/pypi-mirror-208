from bot.interface.interface_pb2 import ModelServiceInput, ModelServiceOutput
from .util import parse_input, parse_input_dict, ModelContextParser, protoTojson
import logging
from typing import Dict, Union, List


class QueryHandlerParamsBuilder():
    def __init__(self):
        """
        ** Mention: 初始化必须放在process函数中，保证每次请求服务时，都会先初始化QueryHandlerParamsBuilder；
        否则，模型输入输出无法及时更新同步
        """
        self._input_proto = None
        self._output_proto = ModelServiceOutput()
        self._input_proto_type = ModelServiceInput
        self._output_proto_type = ModelServiceOutput
        self.logger = logging.getLogger("common")
    
    def _parse_input(self, input_json: Union[str, dict]):
        self._input_proto = parse_input(input_json, self._input_proto_type)
    
    def get_input_dict(self, input_json: Union[str, dict]):
        return parse_input_dict(input_json)
    
    # 获取query（可能是处理后的）
    def request_query(self, input_json: str) -> str:
        if self._input_proto is None:
            self._parse_input(input_json)
        query = ModelContextParser.get_query(self._input_proto)
        return query
    
    # 获取用户输入原query(未处理的)
    def request_raw_query(self, input_json: str) -> str:
        if self._input_proto is None:
            self._parse_input(input_json)
        query = ModelContextParser.get_raw_query(self._input_proto)
        return query

    def request_input_method(self, input_json: str) -> str:
        if self._input_proto is None:
            self._parse_input(input_json)
        input_method = ModelContextParser.get_input_method(self._input_proto)
        return input_method
           
    def request_params(self, input_json: str) -> Dict:
        if self._input_proto is None:
            self._parse_input(input_json)
        params = ModelContextParser.get_params(self._input_proto)
        return params
    
    def request_extra_params(self, input_json: str) -> Dict:
        if self._input_proto is None:
            self._parse_input(input_json)
        extra_params = ModelContextParser.get_extra_params(self._input_proto)
        return extra_params
    
    def request_dialog_history(self, input_json: str) -> List:
        # 返回历史对话轮：[Q]user_query, [R]bot response.
        if self._input_proto is None:
            self._parse_input(input_json)
        return ModelContextParser.get_dialog_history(self._input_proto)
    
    def set_fst_extended_query(self, extend_query=""):
        ModelContextParser.set_fst_extended_query(extend_query, self._output_proto)
        
    def set_params(self, params={}):
        ModelContextParser.set_extra_params(params, self._output_proto)
    
    def set_user_input_params(self, params={}):
        ModelContextParser.set_user_input_params(params, self._output_proto)
            
    def get_output(self):
        output_json = protoTojson(self._output_proto)
        return output_json
    