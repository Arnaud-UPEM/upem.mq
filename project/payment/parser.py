from urllib.parse import urlparse, parse_qs

# pid=69,p=1001[70],p=1002[70,71],p=1003[70,71],p=1004[70,71],p=1005[70,71],p=1006[70,71],
# !v=1!pid=69!p=1002,70,71!p=1003,70,71!p=1004,70,71!p=1005,70,71!p=1001,70 

class ParseException (Exception):
    pass

def parse (raw):
    res = {
        'status': False
    }

    raw = raw.replace('!', '&')
    parsed = urlparse(raw)
    qs = parse_qs(parsed.query)

    if 'donation' in qs:
        res['donation'] = True

    if 'contribution' in qs:
        res['contribution'] = int(qs['contribution'][0])

    if ('donation' in qs) is not ('contribution' in qs):
        res['status'] = True

    return res


def _parse (raw):
    res = {
        'status': False
    }

    raw = raw.replace('!', '&')
    parsed = urlparse(raw)
    qs = parse_qs(parsed.query)

    # DEBUG
    # print (raw)
    # print (parsed)
    # print (qs)

    res['version'] = int(qs['v'][0])

    if res['version'] == 1:
        res.update(_parse_v1(qs))
        return res
        
    elif res['version'] == 2:
        res.update(_parse_v2(qs))
        return res
    else:
        return res

def _parse_v1 (qs):
    res = {
        'cart': [],
        'parent_id': 0
    }

    res['parent_id'] = int(qs['pid'][0])

    for p in qs['p']:
        x = p.split(',')
        if len(x) < 2:
            return res

        res['cart'].append({
            'product': int(x[0]),
            'children': [int(x[i]) for i in range(1, len(x))]
        })

    res['status'] = True
    return res

def _parse_v2 (qs):
    res = {
        'order_id': 0
    }

    res['order_id'] = int(qs['oid'][0])

    res['status'] = True
    return res


if __name__ == '__main__':
    raw = '?contribution=234234'
    print (parse(raw))

    raw = '?donation=1'
    print (parse(raw))

    raw = '?contribution=234234!donation=1'
    print (parse(raw))



    # raw = '?v=1!pid=69!p=1002,70,71!p=1003,70,71!p=1004,70,71!p=1005,70,71!p=1001,70'
    # print (_parse(raw))
    # raw = '?v=2!oid=1953'
    # print (_parse(raw))
