import sys; lines = open('config.ini').readlines(); out = [l for l in lines if '<<<<<<<' not in l and '=======' not in l and '>>>>>>>' not in l]; open('config.ini', 'w').writelines(out)
