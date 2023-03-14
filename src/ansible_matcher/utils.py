from typing import Dict, Any, Type, Callable, List, Union


def visit_dict(d_dict: Dict[str, Any], predicate: Callable, proc: Callable):
    queue = list((k, v, d_dict) for k, v in d_dict.items())
    visited = set()

    while queue:
        k, v, d = queue.pop(0)
        if predicate(v):
            d[k] = proc(v)
        elif isinstance(v, dict):
            if (id(k), id(d)) not in visited:
                queue.extend((_k, _v, v) for _k, _v in v.items())
        visited.add((id(k), id(d)))

    return d_dict


def merge_dicts(into_dict: Dict, from_dict: Dict):
    for k, v in from_dict.items():
        # that's a simple case, if key is not presented in dict - just write new value
        if k not in into_dict:
            into_dict[k] = v
        else:
            if isinstance(v, Dict):
                if not isinstance(into_dict[k], Dict):
                    into_dict[k] = v
                else:
                    merge_dicts(into_dict[k], v)
            elif isinstance(v, List):
                if isinstance(into_dict[k], List):
                    into_dict[k].extend(v)
                else:
                    into_dict[k] = [into_dict[k]] + v
            elif isinstance(into_dict[k], list):
                into_dict[k] = into_dict[k] + [v]
            else:
                into_dict[k] = v
    return into_dict


def listify(val: Any) -> List[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]
