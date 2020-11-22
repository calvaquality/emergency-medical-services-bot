# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

class HealthForm(FormAction):
    def name(self):
        return "health_form"
    @staticmethod
    def required_slots(tracker: "Tracker") -> List[Text]:
        if tracker.get_slot("confirm_exercise") == True:
            return ["confirm_exercise", "exercise", "sleep", "diet", "stress", "goal"]
        else:
            return ["confirm_exercise", "sleep", "diet", "stress", "goal"]

    async def submit(self, dispatcher: "CollectingDispatcher", tracker: "Tracker", domain: "DomainDict") -> List[
        EventType]:
        return []

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict[Text, Any]]]]:
        return {
            "confirm_exercise": [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
                self.from_intent(intent="inform", value=True),
            ],
            "sleep": [

            ]
        }


