import wikipedia
wikipedia.set_user_agent("TTUtilitiesBot/2.3 (contact: https://github.com/dgtproject)")
wikipedia.set_lang('es')
res = wikipedia.summary('doraemon', sentences=2)
with open('doraemon_test.txt', 'w', encoding='utf-8') as f:
    f.write(res)
