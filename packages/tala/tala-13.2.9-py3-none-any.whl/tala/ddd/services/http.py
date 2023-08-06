import json
from datetime import timedelta

from requests.exceptions import RequestException
from requests_cache import CachedSession

from tala.ddd.services.abstract_service_wrapper import AbstractServiceWrapper
from tala.model.service_invocation import PROTOCOL_VERSION
from tala.model.service_query_result import QueryResultFromService
from tala.model.service_action_outcome import SuccessfulServiceAction, FailedServiceAction

CURRENT_VERSION = "1.1"
DEPRECATED_PROTOCOL_VERSIONS = ["1.0"]
SUPPORTED_PROTOCOL_VERSIONS = DEPRECATED_PROTOCOL_VERSIONS + [CURRENT_VERSION]


class HttpServiceInvocationException(Exception):
    pass


class HttpServiceClient(AbstractServiceWrapper):
    def __init__(self, logger, endpoint, name, http_formatter):
        super(HttpServiceClient, self).__init__()
        self._logger = logger
        self._endpoint = endpoint
        self._name = name
        self._http_formatter = http_formatter
        self._session = CachedSession(
            allowable_methods=('GET', 'POST'),
            backend=('sqlite'),
            ignored_parameters=["context"],
            filter_fn=self._filter_cache_by_request_type,
            expire_after=timedelta(minutes=1)
        )

    def _filter_cache_by_request_type(self, response):
        request_type = json.loads(response.request.body)["request"]["type"]
        return True if request_type in ["query", "validator"] else False

    def _post(self, data, headers):
        self._logger.info(
            f"Calling service '{self._name}' on '{self._endpoint}' with headers {headers} and data {data}"
        )
        try:
            response = self._session.post(self._endpoint, data=json.dumps(data), headers=headers, timeout=2)
            self._validate_response(response)
            return response
        except RequestException as exception:
            self._logger.exception("RequestException encountered.")
            raise HttpServiceInvocationException(str(exception))

    def _validate_response(self, response):
        def validate_http_status(response):
            response.raise_for_status()

        def validate_status(response):
            actual_status = response["status"]
            expected_statuses = ["success", "fail", "error"]
            if actual_status not in expected_statuses:
                raise HttpServiceInvocationException(
                    f"Expected 'status' to be one of {expected_statuses} but got {actual_status}"
                )
            if actual_status == "error":
                message = response["message"]
                raise HttpServiceInvocationException(
                    f"Expected service to succeed but it had an error with message: '{message}'."
                )

        def validate_version(response):
            actual_version = response["data"]["version"]
            if actual_version not in SUPPORTED_PROTOCOL_VERSIONS:
                raise HttpServiceInvocationException(
                    f"Expected one of the supported versions {SUPPORTED_PROTOCOL_VERSIONS} but got '{actual_version}'"
                )

        validate_http_status(response)
        payload = json.loads(response.text)
        validate_status(payload)
        validate_version(payload)

    def recognize_entity(self, *args, **kwargs):
        try:
            return self._recognize_entity(*args, **kwargs)
        except ValueError as exception:
            self._logger.exception("Expected JSON to be valid but it wasn't.")
            raise HttpServiceInvocationException(str(exception))
        except KeyError as error:
            self._logger.exception("Expected response to conform to protocol but it didn't.")
            raise HttpServiceInvocationException(str(error))

    def _recognize_entity(self, string, session, context):
        response = self._post(
            data={
                "version": PROTOCOL_VERSION,
                "session": session,
                "request": {
                    "type": "entity_recognizer",
                    "entity_recognizer": self._name,
                    "utterance": string,
                },
                "context": {
                    "active_ddd": context.active_ddd,
                    "facts": self._http_formatter.facts_to_json_object(context.facts, session),
                    "invocation_id": context.invocation_id
                }
            },
            headers={"Content-type": "application/json"}
        )

        response = json.loads(response.text)
        self._assert_successful(response)
        return self._process_entity_results(response["data"]["result"])

    def _process_entity_results(self, entity_dicts):
        return [self._process_entity_dict(entity_dict) for entity_dict in entity_dicts]

    def _process_entity_dict(self, entity_dict):
        return {
            "grammar_entry": entity_dict["grammar_entry"],
            "sort": entity_dict["sort"],
            "name": entity_dict["value"]
        }

    def perform(self, action, parameters, session, context):
        def get_outcome_from_response(response):
            status = response["status"]
            if status == "success":
                return SuccessfulServiceAction()
            elif status == "fail":
                return FailedServiceAction(response["data"]["reason"])
            else:
                raise HttpServiceInvocationException(
                    "Expected 'success' or 'fail' as response status but got {status}."
                )

        response = self._post(
            data={
                "version": PROTOCOL_VERSION,
                "session": session,
                "request": {
                    "type": "request",
                    "name": action,
                    "parameters": self._parameter_bindings_to_json_dict(parameters, session)
                },
                "context": {
                    "active_ddd": context.active_ddd,
                    "facts": self._http_formatter.facts_to_json_object(context.facts, session),
                    "invocation_id": context.invocation_id
                }
            },
            headers={"Content-type": "application/json"}
        )

        response = json.loads(response.text)
        return get_outcome_from_response(response)

    def query(self, question, parameters, min_results, max_results, session, context):
        response = self._post(
            data={
                "version": PROTOCOL_VERSION,
                "session": session,
                "request": {
                    "type": "query",
                    "name": question.get_predicate().get_name(),
                    "parameters": self._parameter_bindings_to_json_dict(parameters, session),
                    "min_results": min_results,
                    "max_results": max_results
                },
                "context": {
                    "active_ddd": context.active_ddd,
                    "facts": self._http_formatter.facts_to_json_object(context.facts, session),
                    "invocation_id": context.invocation_id
                }
            },
            headers={"Content-type": "application/json"}
        )

        response = json.loads(response.text)
        self._assert_successful(response)
        result_dicts = response["data"]["result"]
        return [
            QueryResultFromService(result_dict["value"], result_dict["confidence"], result_dict["grammar_entry"])
            for result_dict in result_dicts
        ]

    def validate(self, validator_name, parameters, session, context):
        response = self._post(
            data={
                "version": PROTOCOL_VERSION,
                "session": session,
                "request": {
                    "type": "validator",
                    "name": self._name,
                    "parameters": self._parameter_bindings_to_json_dict(parameters, session)
                },
                "context": {
                    "active_ddd": context.active_ddd,
                    "facts": self._http_formatter.facts_to_json_object(context.facts, session),
                    "invocation_id": context.invocation_id
                }
            },
            headers={"Content-type": "application/json"}
        )

        response = json.loads(response.text)
        self._assert_successful(response)
        return response["data"]["is_valid"]

    @staticmethod
    def _assert_successful(response):
        actual_status = response["status"]
        expected_status = "success"
        if not actual_status == expected_status:
            raise HttpServiceInvocationException(f"Expected status '{expected_status}' but got '{actual_status}'.")

    def _parameter_bindings_to_json_dict(self, bindings, session):
        def binding_to_json(binding):
            if binding.is_multiple_instance_binding:
                return [
                    self._http_formatter.fact_to_json_object(proposition, session)
                    for proposition in binding.propositions
                ]
            else:
                return self._http_formatter.fact_to_json_object(binding.proposition, session)

        return {binding.parameter.name: binding_to_json(binding) for binding in bindings}
