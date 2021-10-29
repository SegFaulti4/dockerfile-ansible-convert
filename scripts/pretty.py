import sys
import json

with open(sys.argv[1], 'r') as i_f:
    with open(sys.argv[1] + '.json', 'w', newline='') as o_f:
        o_f.write('[' + json.dumps(json.loads(i_f.readline()), indent=4, sort_keys=True))
        for line in i_f.readlines():
            o_f.write(',\n' + json.dumps(json.loads(line), indent=4, sort_keys=True))
        o_f.write(']')
