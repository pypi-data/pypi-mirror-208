from jsonpath_ng.ext import parse

from gcscore.mod import TargetFieldQuery

__all__ = ['create_target_list']

INSTANCES_JSON_PATH = parse('$.Reservations[*].Instances[*]')


def create_target_list(raw_api_result: list[dict], queries: list[TargetFieldQuery]) -> list[dict]:
    """
    Create an AWS target list from the given API result
    :param raw_api_result:
    :param queries:
    :return: the target list
    """
    raw_instances = list(map(lambda m: m.value, INSTANCES_JSON_PATH.find(raw_api_result)))

    targets = []
    for raw_instance in raw_instances:
        targets.append({q.key: q.find(raw_instance) for q in queries})

    return targets
