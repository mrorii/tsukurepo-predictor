#!/usr/bin/env python

import jptokenizer
import json
TOKENIZER = jptokenizer.JPSimpleTokenizer()
recipe = json.loads(open('cookpad.json').readline().strip())
