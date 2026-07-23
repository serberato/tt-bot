import wikipedia
import traceback
import sys

try:
    wikipedia.set_user_agent("TTUtilitiesBot/2.3 (https://github.com/dgtproject)")
    wikipedia.set_lang('es')
    print(wikipedia.summary('doraemon', sentences=2))
except Exception as e:
    traceback.print_exc(file=sys.stdout)
