import re
from Levenshtein import distance

def clean(sx):
    s = sx.split('\n')[0]
    s = re.sub(r'[^\w\s]', '', s)
    return s.lower().replace('-', '').replace(' ', '').replace('_', '').replace('|', '').replace('.', '')


def same(ref, check, debug=False):
    if not isinstance(ref, str):
        return False
    if not isinstance(check, str):
        return False
    ref_len = len(clean(ref))
    check_len = len(clean(check))
    if check_len <= 1:
        return False
    if ref_len <= 1:
        return False
    if clean(check).startswith(clean(ref)):
        if debug:
            print('startswith')
        return True
    if clean(check).endswith(clean(ref)):
        if debug:
            print('endswith')
        return True
    if ref_len > 3 and check_len > 3:
        if clean(ref) in clean(check):
            if debug:
                print('ref in check')
            return True
        if clean(check) in clean(ref):
            if debug:
                print('check in ref')
            return True
        #if ref_len > 4 and distance(clean(ref), clean(check[:ref_len])) < 2:
        #    if debug:
        #        print('distance', clean(ref), clean(check[:ref_len]))
        #    return True
    return False

