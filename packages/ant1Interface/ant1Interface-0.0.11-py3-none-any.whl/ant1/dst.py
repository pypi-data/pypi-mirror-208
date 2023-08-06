# coding=utf-8
# @Author: siye.lsy
# Copyright 2022 Ant Group Co., Ltd.
from bot.interface.interface_pb2 import (
    ModelServiceInput,
    ModelServiceOutput
)
from .util import parse_input, protoTojson
from .util import ModelContextParser
import logging
from typing import Dict, List


class DstParamsBuilder():
    def __init__(self, input_proto_type="ModelServiceInput"):
        """
        used to initialize a builder
        Args:
            input_proto_type (str, optional): _description_. Defaults to "ModelServiceInput".
            input_proto_type must be "ModelServiceInput"
        ** Mention: 初始化必须放在process函数中, 保证每次请求服务时, 都会先初始化 DstParamsBuilder,
        否则，模型输入输出无法及时更新同步
        """
        self.logger = logging.getLogger("common")
        if input_proto_type == "ModelServiceInput":
            self._input_proto_type = ModelServiceInput
            self._output_proto_type = ModelServiceOutput
            self._output_proto = ModelServiceOutput()
        else:
            self.logger.exception("input proto type must be \"ModelServiceInput\"")
        self._input_proto = None
    
    def _parse_input(self, input_json: str):
        self._input_proto = parse_input(input_json, self._input_proto_type)
    
    # 获取query（可能是处理后的）       
    def request_query(self, input_json: str) -> str:
        if self._input_proto is None:
            self._parse_input(input_json)
        # 从接口中提取用户当前轮提问.
        query = ModelContextParser.get_query(self._input_proto)
        return query

    # 获取用户输入原query(未处理的)
    def request_raw_query(self, input_json: str) -> str:
        if self._input_proto is None:
            self._parse_input(input_json)
        query = ModelContextParser.get_raw_query(self._input_proto)
        return query
    
    def request_knowledge(self, input_json: str) -> Dict:
        if self._input_proto is None:
            self._parse_input(input_json)
        knowledge_dict = ModelContextParser.get_knowledge(self._input_proto)
        return knowledge_dict
        
    def request_extra_params(self, input_json: str) -> Dict:
        if self._input_proto is None:
            self._parse_input(input_json)
        extra_params = ModelContextParser.get_extra_params(self._input_proto)
        return extra_params
        
    def set_entities(self, entities: List[Dict]):
        for ent in entities:
            self.set_entity(ent)
        
    def set_entity(self, entity: Dict):
        """
        Args:
            entity (Dict): entity is a dict, which must include 2 keys:
            "id", "raw", or maybe include "confidence" and "attr"
            example:
            case1: 
            entity = {"id": ID1, "raw": RAW1}
            case2:
            entity = {"id": ID2, "raw": RAW2, "confidence": 0.8}]
            case3:
            entity = {"id": ID1, "raw": RAW1, "attr": ["ATTR1", "ATTR2"]}
        """
        ModelContextParser.set_entity(entity, self._output_proto)
    
    def set_slots(self, domain: str, intent: str, slots: List[Dict]):
        # parsed or unparsed slots both allowed
        ModelContextParser.set_hyp(intent, domain, self._output_proto, slots)

    def set_knowledge(self, knowledge_dict: Dict, is_json=False):
        # knowledge_dict is format like {"GROUP_KEY1": {"INFO_ID1":{"id": "ID1", "value": "Value1"}}}
        ModelContextParser.set_knowledge(knowledge_dict, is_json, self._output_proto)
            
    def get_output(self):
        output_json = protoTojson(self._output_proto)
        return output_json
        