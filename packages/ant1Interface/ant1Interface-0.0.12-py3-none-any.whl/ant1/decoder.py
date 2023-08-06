from bot.interface.interface_pb2 import (
    RemoteDecoderInput, 
    RemoteDecoderOutput,
    ModelServiceInput,
    ModelServiceOutput
)
from .util import parse_input, protoTojson
from .util import ModelContextParser, ProtoWrapper
import logging
from typing import Dict, List, Union


class DecoderParamsBuilder():
    def __init__(self, input_proto_type="RemoteDecoderInput"):
        """
        used to initialize a builder
        Args:
            input_proto_type (str, optional): _description_. Defaults to "RemoteDecoderInput".
            input_proto_type must be "RemoteDecoderInput" or "ModelServiceInput"
        ** Mention: 初始化必须放在process函数中，保证每次请求服务时，都会先初始化DecoderParamsBuilder；
        否则，模型输入输出无法及时更新同步
        """
        self.logger = logging.getLogger("common")
        self._input_proto = None
        if input_proto_type not in ("RemoteDecoderInput", "ModelServiceInput"):
            self.logger.exception("input proto type must be \"RemoteDecoderInput\" or \"ModelServiceInput\"")
        if input_proto_type == "RemoteDecoderInput":
            self._input_proto_type = RemoteDecoderInput
            self._output_proto_type = RemoteDecoderOutput
            self._output_proto = RemoteDecoderOutput()
        else:
            self._input_proto_type = ModelServiceInput
            self._output_proto_type = ModelServiceOutput
            self._output_proto = ModelServiceOutput()   
    
    def _parse_input(self, input_json: str):
        self._input_proto = parse_input(input_json, self._input_proto_type)
    
    def request_query(self, input_json: str) -> str:
        if self._input_proto is None:
            self._parse_input(input_json)
        # 从接口中提取用户当前轮提问.
        try:
            if self._input_proto_type == RemoteDecoderInput:
                query = "".join(self._input_proto.query)
                self.logger.info(f"From {self._input_proto} get_query: {query}")
            elif self._input_proto_type == ModelServiceInput:
                query = ModelContextParser.get_query(self._input_proto)
            return query
        except Exception as e:
            print(e)
            self.logger.exception(f'get_query fail, proto query: {self._input_proto}')
        return ''

    def request_raw_query(self, input_json: str) -> str:
        # 如果调用RemoteDecoderInput接口，返回的query和request_query一致, 不一定是用户原query
        # 如果调用modelServiceInput接口，返回的query是用户原query
        if self._input_proto is None:
            self._parse_input(input_json)
        try:
            if self._input_proto_type == RemoteDecoderInput:
                query = "".join(self._input_proto.query)
                self.logger.info(f"From {self._input_proto} get_query: {query}")
            elif self._input_proto_type == ModelServiceInput:
                query = ModelContextParser.get_raw_query(self._input_proto)
            return query
        except Exception as e:
            print(e)
            self.logger.exception(f'get_query fail, proto query: {self._input_proto}')
        return ''

    def request_dialog_history(self, input_json: str) -> List:
        # 返回历史对话轮：[Q]user_query, [R]bot response.
        if self._input_proto is None:
            self._parse_input(input_json)
        try:
            if self._input_proto_type == RemoteDecoderInput:
                return list(self._input_proto.history)
            else:
                return ModelContextParser.get_dialog_history(self._input_proto)
        except Exception as e:
            print(e)
            self.logger.exception(f"request history fail, proto history: {self._input_proto}")
        return []
    
    def request_expected_domain_intent(self, input_json: str) -> Dict:
        if self._input_proto is None:
            self._parse_input(input_json)
        try:
            if self._input_proto_type == RemoteDecoderInput:
                return {"domain": self._input_proto.expected_domain, "intent": self._input_proto.expected_intent}
            else:
                # TODO: ModelContext中的expected domain和intent
                self.logger.info("ModelServiceInput does not support expected domain and intent")
                return {"domain": "", "intent": ""}
        except Exception as e:
            print(e)
            self.logger.exception(f"fail to get expected domain and intent from {self._input_proto}")
        return {}
            
    def request_expected_slots(self, input_json: str) -> Dict:
        if self._input_proto is None:
            self._parse_input(input_json)
        try:
            if self._input_proto_type == RemoteDecoderInput:
                expected_slots = {}
                for slot_id in self._input_proto.expected_slots:
                    slot_classifier_config = self._input_proto.expected_slots[slot_id]
                    slot_dict = {}
                    slot_dict["slot_classifier"] = slot_classifier_config.slot_classifier
                    slot_dict["slot_candidates"] = slot_classifier_config.slot_candidates
                    slot_dict["params"] = dict(slot_classifier_config.params)
                    expected_slots[slot_id] = slot_dict
            else:
                expected_slots = ModelContextParser.get_expected_slots(self._input_proto)
        except Exception as e:
            expected_slots = {}
            print(e)
            self.logger.exception(f"fail to get expected slots from {self._input_proto}")  
        return expected_slots              
    
    def request_filled_slots(self, input_json: str) -> Dict:
        # 返回值：dict, key是slot key, value是Tuple[slot_id, slot_value]
        if self._input_proto is None:
            self._parse_input(input_json)
        try:
            # 两个协议的filled slots字段定义相似，不需要分开解析
            slots_dict = dict()
            slots_dict = ModelContextParser.get_filled_slots(self._input_proto)
        except Exception as e:
            print(e)
            self.logger.exception(f"fail to get filled slots from {self._input_proto}")
        return slots_dict
    
    def request_knowledge(self, input_json: str) -> Dict:
        if self._input_proto is None:
            self._parse_input(input_json)
        try:
            knowledge_dict = dict()
            if self._input_proto_type == RemoteDecoderInput:
                knowledge = self._input_proto.knowledge
                for key in knowledge:
                    id = knowledge[key].id
                    value = knowledge[key].value
                    knowledge_dict[key] = (id, value)
            else:
                knowledge_dict = ModelContextParser.get_knowledge(self._input_proto)   
        except Exception as e:
            print(e)
            self.logger.exception(f"fail to get knowledge from {self._input_proto}")
        return knowledge_dict
    
    def request_domain_result(self, input_json: str, component_id):
        if self._input_proto is None:
            self._parse_input(input_json)
        try:
            if self._input_proto_type == RemoteDecoderInput:
                raise ValueError("Can not support get domain result with remote decoder")
            else:
                domain_id, domain_confidence = ModelContextParser.get_domain_result(self._input_proto, component_id)
        except Exception as e:
            print(e)
            self.logger.exception(f"fail to get domain result from {self._input_proto}")
        return domain_id, domain_confidence
    
    def request_current_domain_intent(self, input_json):
        if self._input_proto is None:
            self._parse_input(input_json)
        try:
            if self._input_proto_type == RemoteDecoderInput:
                raise ValueError("Can not support get current intent with remote decoder, \
                                 refer to function request_expected_domain_intent")
            else:
                domain, intent = ModelContextParser.get_current_domain_intent(self._input_proto)
        except Exception as e:
            print(e)
            self.logger.exception(f"fail to get current domain from {self._input_proto}")
        return domain, intent
    
    def request_last_domain_decoder_result(self, input_json, component_id):
        if self._input_proto is None:
            self._parse_input(input_json)
        try:
            if self._input_proto_type == RemoteDecoderInput:
                raise ValueError("Can not support get last domain decoder result with remote decoder, \
                                 refer to function request_expected_domain_intent")
            else:
                domain, score = ModelContextParser.get_last_domain_decoder_result(self._input_proto, component_id)
        except Exception as e:
            print(e)
            self.logger.exception(f"fail to get current domain from {self._input_proto}")
        return domain, score
        
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
        if self._output_proto_type == RemoteDecoderOutput:
            entity_proto = ProtoWrapper.wrap_named_entity(entity)
            self._output_proto.entity.append(entity_proto)
        else:
            ModelContextParser.set_entity(entity, self._output_proto)
          
    def set_hyp_function(self, function: Union[str, dict], domain_confidence=1.0, intent_confidence=1.0):
        if self._output_proto_type == RemoteDecoderOutput:
            if not isinstance(function, str):
                self.logger.exception("RemoteDecoderOutput only supports function expressions, string type")
            hyp = self._output_proto.result.add()
            hyp.domain_confidence = domain_confidence
            hyp.intent_confidence = intent_confidence
            hyp.function = function
        else:
            ModelContextParser.set_hyp_function_expression(function, domain_confidence, 
                                                           intent_confidence, self._output_proto)
            
    def set_extra_params(self, params: Dict):
        if self._output_proto_type == RemoteDecoderOutput:
            if not isinstance(params, dict):
                raise ValueError(f"input params {params} is not dict")
            for k, v in params.items():
                self._output_proto.extra_params[k] = v
        else:
            ModelContextParser.set_extra_params(params, self._output_proto)
    
    def set_knowledge(self, knowledge_dict: Dict, is_json=False):
        if self._output_proto_type == RemoteDecoderOutput:
            knowledge = ProtoWrapper.wrap_knowledge(knowledge_dict, is_json)
            self._output_proto.knowledge.CopyFrom(knowledge)
        else:
            ModelContextParser.set_knowledge(knowledge_dict, is_json, self._output_proto)
    
    def set_user_sentiment(self, sentiment: str, score=1.0):
        if not sentiment:
            self.logger.info("sentiment is empty")
            return -1
        if self._output_proto_type == RemoteDecoderOutput:
            user_sentiment = ProtoWrapper.wrap_user_sentiment(sentiment, score)
            self._output_proto.user_sentiment.CopyFrom(user_sentiment)
        else:
            ModelContextParser.set_user_sentiment(sentiment, score, self._output_proto)
            
    def set_hyp(
        self,
        intent, 
        domain,
        slots=[], 
        params={}, 
        hyp_knowledge={}, 
        knowledge_is_json=True,
        intent_confidence=1.0, 
        domain_confidence=1.0
    ):
        if not intent or not domain:
            self.logger.info("intent and domain must not be empty")
            return -1
        try:
            if self._output_proto_type == RemoteDecoderOutput:
                intent_hyp = self._output_proto.result.add()
                if not domain or not intent:
                    raise ValueError("domain and intent should not be empty")
                intent_hyp.domain = domain
                intent_hyp.intent = intent
                intent_hyp.domain_confidence = domain_confidence
                intent_hyp.intent_confidence = intent_confidence
                # wrap slot/stack_slot
                for slot in slots:
                    if "id" not in slot or "value" not in slot:
                        raise ValueError(f"input slot {slot} does not include id and value")
                    if isinstance(slot["value"], list):
                        slot_proto = intent_hyp.stack_slots.add()
                        slot_proto.values.extend(slot["value"])
                    elif isinstance(slot["value"], str):
                        slot_proto = intent_hyp.slots.add()
                        slot_proto.value = slot["value"]
                    else:
                        raise ValueError(f"value in slot can only be list or string")
                    slot_proto.id = slot["id"]
                    slot_proto.confidence = slot.get("confidence", 1.0)
                # wrap knowledge    
                if hyp_knowledge:
                    knowledge = ProtoWrapper.wrap_knowledge(hyp_knowledge, knowledge_is_json)
                    intent_hyp.knowledge.CopyFrom(knowledge)
                # set params
                if params:
                    for k, v in params.items():
                        intent_hyp.params[k] = v
            else:
                ModelContextParser.set_hyp(intent, domain, self._output_proto, slots, params, 
                                           hyp_knowledge, intent_confidence, domain_confidence)
        except Exception as e:
            print(e)
            self.logger.info("fail to set remote hypothesis")
            
    def set_domain_result(
        self,
        domain,
        domain_confidence=1.0
    ):
        if not domain:
            self.logger.info("intent and domain must not be empty")
            return -1  
        try:
            if self._output_proto_type == RemoteDecoderOutput:
                intent_hyp = self._output_proto.result.add()
                if not domain:
                    raise ValueError("domain should not be empty")
                intent_hyp.domain = domain
                intent_hyp.domain_confidence = domain_confidence
            else:
                ModelContextParser.set_domain_result(domain, self._output_proto, domain_confidence)
        except Exception as e:
            self.logger.info(e)
                
    def get_output(self):
        output_json = protoTojson(self._output_proto)
        return output_json
        