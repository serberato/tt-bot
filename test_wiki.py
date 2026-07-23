import wikipedia
import traceback
import sys

try:
    wikipedia.set_lang('es')
    print(wikipedia.summary('doraemon', sentences=10))
except Exception as e:
    traceback.print_exc(file=sys.stdout)
