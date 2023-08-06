import json
import logging
from google.protobuf.json_format import ParseDict, MessageToDict, MessageToJson
from bot.interface.model_context_pb2 import (
    NamedEntity, 
    IntentHyp, 
    Knowledge, 
    UserSentiment,
    ModelContext
)
from bot.interface.interface_pb2 import ModelServiceInput, ModelServiceOutput, RemoteDecoderInput
from bot.interface.slot_pb2 import Slot, Function
from typing import Dict, List, Union

logger = logging.getLogger("common")


def parse_params(params):
    '''将接口参数进行解析，将 body 中的 kv 提到上一级.

    背景：由于 Zark 不会将 content_type: application/json 请求的 body 进行解析，
    需要 app 自行处理，该 function 统一处理这种场景，减少各个 app 的代码冗余。
    参考链接：https://yuque.antfin-inc.com/zark/uev5ey/bnb04g#h4DR0
    '''
    if isinstance(params, str):
        return params
    body = params.get('body', '')
    if not body:
        return params
    try:
        params = dict()
        if isinstance(body, dict):
            params.update(body)
        elif isinstance(body, str):
            params.update(json.loads(body))
        else:
            logger.error(
                'Request params body invalid: {}'.format(body))
    except Exception:
        logger.exception(
            'Cannot parse request params body: {}'.format(params['body']))
    return params


def parse_input_dict(input_json: str):
    input = parse_params(input_json)
    if isinstance(input, str):
        input = json.loads(input)
    data = input["data"] if "data" in input else input
    if isinstance(data, str):
        data = json.loads(data)
    if not data:
        data = ""
        logger.info("input json is empty")
    return data

    
def parse_input(input_json: str, proto_type):
    input = parse_params(input_json)
    if isinstance(input, str):
        input = json.loads(input)
    data = input["data"] if "data" in input else input
    if isinstance(data, str):
        data = json.loads(data)
    if not data:
        raise ValueError("input json is empty")
    
    try:
        input_proto = ParseDict(data, proto_type())

        # 如果输入的是ModelContextJson也要先解析
        if proto_type == ModelServiceInput and input_proto.HasField("model_context_json"):
            model_context = json.loads(input_proto.model_context_json)
            model_context_proto = ParseDict(model_context, ModelContext())
            input_proto.model_context.CopyFrom(model_context_proto)
    except Exception as e:
        print(e)
        logger.info(f"fail to parse {data} into {proto_type}")
        input_proto = proto_type()
    return input_proto


def protoTojson(proto):
    proto_dict = MessageToDict(proto)
    proto_json = json.dumps(proto_dict, ensure_ascii=False)
    return proto_json


class ProtoWrapper():
    # 将用户输入的dict/list等格式封装成对应的proto
    def __init__(self):
        pass
    
    @classmethod
    def wrap_named_entity(cls, entity: Dict) -> NamedEntity:
        if not isinstance(entity, dict):
            raise ValueError(f"entity {entity} must be a dict")
        if "id" not in entity or "raw" not in entity:
            raise ValueError(f"entity must include id and raw")
        entity["confidence"] = entity.get("confidence", 1.0)
        entity_proto = ParseDict(entity, NamedEntity())
        return entity_proto
    
    @classmethod
    def wrap_hyp_function_expression(cls, function: str, domain_confidence=1.0, intent_confidence=1.0) -> IntentHyp:
        if not function:
            raise ValueError(f"{function} is empty, Please set function")
        intent_hyp = IntentHyp()
        intent_hyp.domain_confidence = domain_confidence
        intent_hyp.intent_confidence = intent_confidence
        intent_hyp.function_expression = function
        return intent_hyp
    
    @classmethod
    def wrap_knowledge(cls, knowledge_dict: dict, is_json=False) -> Knowledge:
        # knowledge_dict is format like {"GROUP_KEY1": {"INFO_ID1":{"id": "ID1", "value": "Value1"}}}
        knowledge = Knowledge()
        try:
            if not isinstance(knowledge_dict, dict):
                raise ValueError("input knowledge_dict must be dict")
            for group_key in knowledge_dict:
                group_info = knowledge_dict[group_key]
                for info_id in group_info:
                    info_item = group_info[info_id]
                    info_item_proto = Knowledge.InfoItem()
                    if is_json:
                        info_item_proto.id = info_id
                        info_item_proto.value = info_item
                        info_item_proto.is_json = True
                    else:
                        if ("life_cycle" in info_item and info_item["life_cycle"] == "LIMITED_TURNS"
                                and "life_cycle_turns" not in info_item):
                            raise ValueError("when life_cycle set as limited turns, \
                                you have to specify life cycle turns")
                        info_item_proto = ParseDict(info_item, Knowledge.InfoItem())
                        info_item_proto.is_json = False
                    knowledge.groups[group_key].infos[info_id].CopyFrom(info_item_proto)               
        except Exception as e:
            print(e)
            logger.info("Input knowledge dict must be in the format \
                        like {\"G1\": {\"INFO_ID1\": {\"id\": \"ID1\",\"value\": \"Value1\"}}}")
        return knowledge

    @classmethod
    def wrap_user_sentiment(cls, sentiment: str, score=1.0) -> UserSentiment:
        user_sentiment = UserSentiment()
        user_sentiment.sentiment = sentiment
        user_sentiment.score = score
        return user_sentiment
    
    @classmethod
    def wrap_slot(cls, slot: Dict) -> Slot:
        slot_proto = Slot()
        try:
            slot["confidence"] = slot.get("confidence", 1.0)
            slot_proto = ParseDict(slot, Slot())
        except Exception as e:
            print(e)
        return slot_proto

    @classmethod
    def wrap_function(cls, function: Dict, domain_confidence, intent_confidence) -> IntentHyp:
        if not function:
            raise ValueError(f"{function} is empty, Please set function")
        intent_hyp = IntentHyp()
        intent_hyp.domain_confidence = domain_confidence
        intent_hyp.intent_confidence = intent_confidence
        function_proto = ParseDict(function, Function())
        intent_hyp.function = function_proto
        return intent_hyp
            

class ModelContextParser():
    kQueryHistoryPrefix = '[Q]'
    kResponseHistoryPrefix = '[R]'
    
    def __init__(self):
        pass

    @classmethod
    def get_query(cls, input_proto: ModelServiceInput) -> str:
        # 从接口中提取用户当前轮提问.
        try:
            
            query = input_proto.model_context.user_input.text_input[-1]
            logger.info(f'From {input_proto} get_query: {query}')
            return query
        except Exception as e:
            print(e)
        return ''
    
    @classmethod
    def get_raw_query(cls, input_proto: ModelServiceInput) -> str:
        # 获取未处理的用户原问题
        try:
            query = input_proto.query
            logger.info(f'From {input_proto} get_query: {query}')
            return query
        except Exception as e:
            print(e)
        return ''
    
    @classmethod
    def get_params(cls, input_proto: ModelServiceInput) -> Dict:
        try:
            params = input_proto.model_context.user_input.params
            params = dict(params)
        except Exception as e:
            print(e)
            params = {}
        return params

    @classmethod
    def get_extra_params(cls, input_proto: ModelServiceInput) -> Dict:
        try:
            extra_params = dict(input_proto.params)
        except Exception as e:
            print(e)
            extra_params = {}
        return extra_params   
    
    @classmethod
    def get_dialog_history(cls, input_proto: ModelServiceInput) -> List:
        dialog_history_list = []
        try:
            dialog_history = input_proto.model_context.dialog_history
            for his in dialog_history:
                if his.HasField("user_input"):
                    dialog_history_list.append(cls.kQueryHistoryPrefix + his.user_input.text_input[0])
                if his.HasField("bot_reply"):
                    dialog_history_list.append(cls.kResponseHistoryPrefix + his.bot_reply.reply)
        except Exception as e:
            print(e)
        return dialog_history_list
            
    @classmethod
    def get_intent_history(cls, input_proto: ModelServiceInput) -> List:
        history = []
        try:
            intent_history = input_proto.model_context.intent_history.intent_info
            for int in intent_history:
                history.append({"intent_id": int.intent_id, "domain_id": int.domain_id})
        except Exception as e:
            print(e)
        return history
    
    @classmethod 
    def get_filled_slots(cls, input_proto: Union[ModelServiceInput, RemoteDecoderInput]) -> Dict:
        slots_dict = dict()
        try:
            filled_slots = input_proto.filled_slots
            for slot_key in filled_slots:
                id = filled_slots[slot_key].id
                value = filled_slots[slot_key].value
                slots_dict[slot_key] = (id, value)
        except Exception as e:
            print(e)
        return slots_dict
    
    @classmethod
    def get_knowledge(cls, input_proto: ModelServiceInput) -> Dict:
        # 返回dict: Dict[Knowledge:Dict[Group_key: Dict[id, value]]]
        knowledge_dict = dict()
        try:
            knowledge = input_proto.model_context.knowledge
            print("knowledge group")
            print(knowledge.groups)
            for key in knowledge.groups:
                group_info = knowledge.groups[key]
                group_dict = dict()
                for group_key in group_info.infos:
                    info_item = group_info.infos[group_key]
                    if info_item.is_json:
                        info_item = json.loads(info_item.value)
                        info_id_value = (info_item["id"], info_item["value"])
                    else:
                        info_id_value = (info_item.id, info_item.value)
                    group_dict[group_key] = info_id_value
                knowledge_dict[key] = group_dict
        except Exception as e:
            print(e)
        return knowledge_dict

    @classmethod
    def get_input_method(cls, input_proto: ModelServiceInput) -> str:
        input_method = ""
        print(f"model context: {input_proto.model_context}")
        try:
            input_method = input_proto.model_context.user_input.input_method
        except Exception as e:
            print(e)
        return input_method
        
    @classmethod
    def get_expected_slots(cls, input_proto: ModelServiceInput) -> Dict:
        expected_slots = {}
        try:
            expected_slots_proto = input_proto.model_context.dialog_state.expected_slots
            for slot_id in expected_slots_proto:
                slot_classifier_config = expected_slots_proto[slot_id]
                slot_dict = {}
                slot_dict["slot_classifier"] = slot_classifier_config.slot_classifier
                slot_dict["slot_candidates"] = slot_classifier_config.slot_candidates
                slot_dict["params"] = dict(slot_classifier_config.params)
                expected_slots[slot_id] = slot_dict
        except Exception as e:
            print(e)
        return expected_slots
    
    @classmethod
    def get_domain_result(cls, input_proto: ModelServiceInput, component_id: str):
        try:
            domain_id = ""
            domain_confidence = 0
            hyps = input_proto.model_context.user_input.domain_result.hyps
            for hyp in hyps:
                if hyp.intent_component_id == component_id:
                    domain_id = hyp.domain_id
                    domain_confidence = hyp.domain_confidence
        except Exception as e:
            print(e)
            logger.exception(f"fail to extract domain result from {input_proto}")
            domain_id = ""
            domain_confidence = 0
        return domain_id, domain_confidence
        
    @classmethod
    def get_expected_slots(cls, input_proto: ModelServiceInput) -> Dict:
        expected_slots = {}
        try:
            expected_slots_proto = input_proto.model_context.dialog_state.expected_slots
            for slot_id in expected_slots_proto:
                slot_classifier_config = expected_slots_proto[slot_id]
                slot_dict = {}
                slot_dict["slot_classifier"] = slot_classifier_config.slot_classifier
                slot_dict["slot_candidates"] = slot_classifier_config.slot_candidates
                slot_dict["params"] = dict(slot_classifier_config.params)
                expected_slots[slot_id] = slot_dict
        except Exception as e:
            print(e)
        return expected_slots
    
    @classmethod
    def set_entity(cls, entity: Dict, output_proto: ModelServiceOutput):
        try:
            entity_proto = ProtoWrapper.wrap_named_entity(entity)
            output_proto.model_context.decoder_result.entities.entity.append(entity_proto)
        except Exception as e:
            print(e)
            logger.exception(f"fail to insert {entity} into {output_proto}") 
            
    @classmethod
    def set_knowledge(cls, knowledge_dict: Dict, is_json: bool, output_proto: ModelServiceOutput):
        try:
            knowledge_proto = ProtoWrapper.wrap_knowledge(knowledge_dict, is_json)
            output_proto.model_context.knowledge.CopyFrom(knowledge_proto)
        except Exception as e:
            print(e)
            logger.exception(f"fail to insert {knowledge_dict} into {output_proto}")
            
    @classmethod
    def set_hyp_function_expression(
        cls, 
        function: str, 
        domain_confidence: float, 
        intent_confidence: float, 
        output_proto: ModelServiceOutput
    ):
        try:
            intent_hyp = ProtoWrapper.wrap_hyp_function_expression(function, domain_confidence, intent_confidence)
            output_proto.model_context.decoder_result.hyps.append(intent_hyp)
        except Exception as e:
            print(e)
            logger.exception(f"fail to add {function} into {output_proto}")
    
    @classmethod
    def set_hyp_function(
        cls, 
        function: dict, 
        domain_confidence: float, 
        intent_confidence: float, 
        output_proto: ModelServiceOutput
    ):
        try:
            intent_hyp = ProtoWrapper.wrap_function(function, domain_confidence, intent_confidence)
            output_proto.model_context.decoder_result.hyps.append(intent_hyp)
        except Exception as e:
            print(e)
            logger.exception(f"fail to add {function} into {output_proto}")
    
    @classmethod
    def set_extra_params(cls, params: Dict, output_proto: ModelServiceOutput):
        try:
            if not isinstance(params, dict):
                raise ValueError(f"input params {params} is not dict")
            for k, v in params.items():
                output_proto.params[k] = v
        except Exception as e:
            print(e)
            logger.exception(f"fail to add {params} into {output_proto}")
            
    @classmethod
    def set_fst_extended_query(cls, extend_query, output_proto):
        try:
            if extend_query:
                output_proto.model_context.user_input.fst_extended_query.append(extend_query)
            else:
                logger.info("extend_query is empty, fail to set fst extended query")
        except Exception as e:
            print(e)
            logger.exception(f"fail to add {extend_query} info {output_proto}")
            
    @classmethod
    def set_user_sentiment(cls, sentiment, score, output_proto):
        try:
            if sentiment:
                user_sentiment = ProtoWrapper.wrap_user_sentiment(sentiment, score)
                output_proto.model_context.decoder_result.user_sentiment.CopyFrom(user_sentiment)
            else:
                logger.info("sentiment is empty")
        except Exception as e:
            print(e)
            logger.exception(f"fail to add {sentiment} into {output_proto}")
    
    @classmethod
    def set_hyp(
        cls, 
        intent, 
        domain,
        output_proto, 
        slots=[], 
        params={}, 
        hyp_knowledge={}, 
        knowledge_is_json = True,
        intent_confidence=1.0, 
        domain_confidence=1.0
    ):
        try:
            intent_hyp = IntentHyp()
            if not domain or not intent:
                raise ValueError("domain and intent should not be empty")
            intent_hyp.domain_id = domain
            intent_hyp.intent_id = intent
            intent_hyp.domain_confidence = domain_confidence
            intent_hyp.intent_confidence = intent_confidence
            # wrap slots
            if len(slots) > 0:
                for slot in slots:
                    slot_proto = ProtoWrapper.wrap_slot(slot)
                    intent_hyp.slots.append(slot_proto)
            # wrap knowledge
            if hyp_knowledge:
                knowledge = ProtoWrapper.wrap_knowledge(hyp_knowledge, knowledge_is_json)
                intent_hyp.knowledge.CopyFrom(knowledge)
            # set params
            if params:
                for k, v in params.items():
                    intent_hyp.params[k] = v
            output_proto.model_context.decoder_result.hyps.append(intent_hyp)
        except Exception as e:
            print(e)
            logger.info("fail to set decoder result")
            
    @classmethod
    def set_user_input_params(cls, params, output_proto):
        try:
            if params:
                for k, v in params.items():
                    output_proto.model_context.user_input.params[k] = v
        except Exception as e:
            print(e)
            logger.info("fail to set params to user input")
    
    @classmethod
    def set_domain_result(cls, domain, output_proto, domain_confidence=1.0):
        try:
            if not domain:
                raise ValueError(f"domain should not be empty")
            intent_hyp = IntentHyp()
            intent_hyp.domain_id = domain
            intent_hyp.domain_confidence = domain_confidence
            output_proto.model_context.decoder_result.hyps.append(intent_hyp)
        except Exception as e:
            logger.info(e)
            
