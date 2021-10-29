import bashlex
from bashlex import errors

from exception import ConvertException
from log import globalLog


if __name__ == '__main__':
    # with open('./dataset/phase_1.json.mined', 'r') as in_f:
    #     for line in in_f.readlines()[:10]:
    #         try:
    #             parsed = bashlex.parse(line)
    #             print(parsed)
    #         except Exception as PE:
    #             print(line)
    #             pass
    line = "ps aux | grep ps"
    res = bashlex.parse(line)
    print(res)
