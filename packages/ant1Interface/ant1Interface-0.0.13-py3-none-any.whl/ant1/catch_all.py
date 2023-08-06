from .util import parse_params
import logging
import json


class CatchAllParamsBuilder():
    def __init__(self):
        self.logger = logging.getLogger("common")
        self.data = None
        self.output = {}

    def _parse_input(self, input_json):
        input = parse_params(input_json)
        if isinstance(input, str):
            input = json.loads(input)
        data = input["data"] if "data" in input else input
        if isinstance(data, str):
            data = json.loads(data)
        if not data:
            raise ValueError("input json is empty")
        self.data = data

    def request_query(self, input_json):
        if self.data is None:
            self._parse_input(input_json)
        query = self._get_query()
        return query

    def request_knowledge(self, input_json):
        if self.data is None:
            self._parse_input(input_json)
        knowledge = self._get_knowledge()
        return knowledge

    def request_history(self, input_json):
        if self.data is None:
            self._parse_input(input_json)
        history = self._get_history()
        return history

    def request_extra_info(self, input_json):
        if self.data is None:
            self._parse_input(input_json)
        extra_info = self._get_extra_info()
        return extra_info

    def request_id(self, input_json):
        if self.data is None:
            self._parse_input(input_json)
        id = self._get_id()
        return id

    def _get_knowledge(self) -> dict:
        """提取knowlege字段"""
        knowledge = self.data.get("knowledge", "{}")
        knowledge = json.loads(knowledge)
        return knowledge

    def _get_extra_info(self) -> dict:
        extra_info = {}
        extra_info["scene_code"] = (
            self.data.get("user_info", {}).get("values", {}).get("__reqEntry__", "")
        )
        extra_info["sp_no"] = (
            self.data.get("context_info", {})
            .get("filled_slots", {})
            .get("USER/INFO/SP_NO", "")
        )
        extra_info["prod_no"] = (
            self.data.get("context_info", {})
            .get("filled_slots", {})
            .get("USER/INFO/PROD_NO", "")
        )
        extra_info["prod_name"] = (
            self.data.get("context_info", {})
            .get("filled_slots", {})
            .get("USER/INFO/PROD_NAME", "")
        )
        extra_info["input_type"] = (
            self.data.get("context_info", {})
            .get("filled_slots", {})
            .get("USER/INFO/queryType", "")
        )
        return extra_info

    def _get_query(self) -> dict:
        """提取用户当前轮提问."""
        query = {}
        query["text"] = self.data.get("text", "")
        query["normed"] = self.data.get("normed", "")
        query["cleaned"] = self.data.get("cleaned", "")
        return query

    def _get_id(self) -> dict:
        """提取ID相关信息"""
        id = {}
        id["trace_id"] = (
            self.data.get("user_info", {}).get("values", {}).get("__traceId__", "")
        )
        id["session_id"] = self.data.get("context_id", "")
        id["search_id"] = self.data.get("search_id", "")
        id["user_id"] = self.data.get("nlu_feature", {}).get("userId", "")
        return id

    def _get_history(self) -> list:
        """提取用户的历史信息."""
        history_list = []
        turn = 1
        for utterance in self.data.get("nlu_feature", {}).get("history", []):
            if utterance.startswith("[Q]"):
                history_list.append(
                    {
                        "turn": turn,
                        "query": utterance.replace("[Q]", ""),
                        "intent": self.data.get("nlu_feature", {}).get(
                            "lastIntent", ""
                        ),
                    }
                )
                turn += 1
        return history_list

    def add_answer(self, answer):
        """设置输出中的answer字段"""
        if "answer" not in self.output:
            self.output["answer"] = [answer]
        else:
            self.ouput["answer"].append(answer)

    def get_output(self):
        """获取模型输出."""
        if not self._check_is_valid(self.output):
            raise ValueError("Output format is invalid!")
        return json.dumps({"response": self.output})

    def _check_is_valid(self, content):
        """检查输出格式"""
        # TODO: BOT也检查了，看看需要检查哪些东西
        if "answer" not in content:
            self.logger.info("Answer keys not found in content!")
            return False
        else:
            for ans in content["answer"]:
                for key in ["domain", "intent", "score"]:
                    if key not in ans:
                        self.logger.info(f"{key} keys not found in answer!")
                        return False
        if "ext_slot" in content:
            for key in content["ext_slot"].keys():
                if key in content:
                    self.logger.info("Duplicate keys found in content and ext_slot!")
                    return False
        return True
