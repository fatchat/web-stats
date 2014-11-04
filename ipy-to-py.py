import json
import sys

f=open(sys.argv[1],'r')
contents=''.join(f.readlines())
data=json.loads(contents)
for ws in data['worksheets']:
	for cell in ws['cells']:
		for line in cell['input']:
			print(line.strip('\n'))