from typing import Dict, Any, Callable, List


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
        elif isinstance(v, list):
            if (id(k), id(d)) not in visited:
                queue.extend((_k, _v, v) for _k, _v in enumerate(v))
        visited.add((id(k), id(d)))

    return d_dict


def merge_dicts(into_dict: Dict, from_dict: Dict, override: bool):
    for k, v in from_dict.items():
        if k not in into_dict or override:
            into_dict[k] = v
        else:
            # `v` value has higher precedence
            if isinstance(v, Dict):
                if isinstance(into_dict[k], Dict):
                    merge_dicts(into_dict[k], v, override)
                else:
                    into_dict[k] = v
            elif isinstance(v, List):
                if isinstance(into_dict[k], List):
                    into_dict[k].extend(v)
                else:
                    into_dict[k] = v
            else:
                into_dict[k] = v
    return into_dict


def listify(val: Any) -> List[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]
