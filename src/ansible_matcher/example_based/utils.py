from typing import Dict, Any, Type, Callable, List


def visit_dict(d_dict: Dict[str, Any], target: Type, target_func: Callable):
    queue = list((k, v, d_dict) for k, v in d_dict.items())
    visited = set()

    while queue:
        k, v, d = queue.pop(0)
        if isinstance(v, target):
            d[k] = target_func(v)
        elif isinstance(v, dict):
            if (id(k), id(d)) not in visited:
                queue.extend((_k, _v, v) for _k, _v in v.items())
        visited.add((id(k), id(d)))

    return d_dict


def merge_dicts(into_dict: Dict, from_dict: Dict):
    for k, v in from_dict.items():
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
            else:
                into_dict[k] = [into_dict[k]] + [v]
    return into_dict
