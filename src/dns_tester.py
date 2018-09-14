#! /usr/local/bin/python3

import subprocess as sp


class FormatErrorException(Exception):
    def __init__(self, func_name: str):
        self.message = f'Return Format incorrect for function: {func_name}'


class PingNotSupportedException(Exception):
    def __init__(self, server: str):
        self.server = server
        self.message = f'Ping not supported for server: {server}'


delim = """==================================="""


def ping_eval(server: str, repeat: int = 10):
    cmd = f'ping -c {repeat} {server}'
    cmd = cmd.split()
    res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    if res.stdout:
        lines = res.stdout.decode('utf-8').split('\n')
        line = lines[-2]
        if line.startswith('round-trip'):
            return tuple(line.split()[-2].split('/'))
        elif line.startswith(str(repeat)):
            raise PingNotSupportedException(server)
        else:
            raise FormatErrorException('ping_eval: not start with round trip')
    else:
        raise FormatErrorException('ping_eval: ping command returned error')


def nslookup_eval(hostname: str, dns: str):
    cmd = f'nslookup {hostname} {dns}'
    cmd = cmd.split()
    res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    if res.stdout:
        lines = res.stdout.decode('utf-8').split('\n')
        line = lines[-3]
        if line.startswith('Address:'):
            return True
        else:
            return False
    else:
        raise FormatErrorException('nslookup_eval: nslookup command returned error')


def evaluate_dns(dns: str, sites: [str] = None):
    print(delim)
    repeat = 10
    minv, avgv, maxv, stddev = None, None, None, None

    try:
        print(f'Evaluating dns server with ping: {dns}, repeating {repeat} times')
        minv, avgv, maxv, stddev = ping_eval(dns, repeat)
        print(f'\tMin/Avg/Max/Stddev = {minv}/{avgv}/{maxv}/{stddev}')
    except PingNotSupportedException as e:
        print(f'\tPing not supported for server: {e.server}')
        print('\tUnable to test rtt')

    if sites is None:
        sites = ['google.com']
    found = True
    for s in sites:
        if not nslookup_eval(s, dns):
            found = False
            print("\t" + s + " not found")
    print(f'\tAll sites found: {found}')
    return avgv, stddev, found


def find_idx(lst, cmp_func):
    if not lst:
        return None
    idx_list = [0]
    item = lst[0]
    for i in range(len(lst[1:])):
        res = cmp_func(lst[i + 1], item)
        if res > 0:
            idx_list.clear()
            idx_list.append(i + 1)
            item = lst[i + 1]
        elif res == 0:
            idx_list.append(i + 1)
    return idx_list


def mfind_none(a, b):
    if a is None and b is None:
        return 0
    if a is None and b is not None:
        return 1
    if a is not None and b is None:
        return -1
    return 0


def mfind_min(a, b):
    if a is None and b is None:
        return 0
    if a is None and b is not None:
        return -1
    if a is not None and b is None:
        return 1
    return b - a


def mfind_fastest_avg(a, b):
    a = a[0]
    b = b[0]
    if a is None and b is None:
        return 0
    if a is None and b is not None:
        return -1
    if a is not None and b is None:
        return 1
    return float(b) - float(a)


def mfind_most_stable(a, b):
    a = a[1]
    b = b[1]
    if a is None and b is None:
        return 0
    if a is None and b is not None:
        return -1
    if a is not None and b is None:
        return 1
    return float(b) - float(a)


def mfind_all_found(a, b):
    a = a[2]
    b = b[2]
    if a is None and b is None:
        return 0
    if a is None and b is not None:
        return -1
    if a is not None and b is None:
        return 1

    if a and b:
        return 0
    if a and not b:
        return 1
    if not a and b:
        return -1
    if not a and not b:
        return 0


def mavg_all_none(lst: list):
    for i in lst:
        if i[0] is not None:
            return False
    return True


def mstddev_all_none(lst: list):
    for i in lst:
        if i[1] is not None:
            return False
    return True


if __name__ == '__main__':
    import argparse as arg

    parser = arg.ArgumentParser()
    parser.add_argument('dns',
                        help='Text file containing dns servers. Empty lines and lines start with # are ignored.')
    parser.add_argument('sites',
                        help='Text file containing sites to be tested. Empty lines and lines start with # are ignored.')

    args = parser.parse_args()

    if args.dns and args.sites:
        dns_list = []
        sites_list = []
        with open(args.dns, 'r') as dns, open(args.sites, 'r') as sites:
            for line in dns.readlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    dns_list.append(line)
            for line in sites.readlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    sites_list.append(line)

        eval_results = []
        for dns in dns_list:
            eval_results.append(evaluate_dns(dns, sites_list))

        print(delim)
        if not mavg_all_none(eval_results):
            items = find_idx(eval_results, mfind_fastest_avg)
            for i in items:
                print(dns_list[i], end=', ')
            print('\n\tare the fastest servers in average')
            print()

            items = find_idx(eval_results, mfind_most_stable)
            for i in items:
                print(dns_list[i], end=', ')
            print('\n\tare the most stable servers')
            print()
        else:
            print('All servers are not supporting ping')
        print()
        items = find_idx(eval_results, mfind_all_found)
        for i in items:
            print(dns_list[i], end=', ')
        print('\n\tare the most complete servers')


    # lst = [1, 2, 3, 4, None, None]
    # from random import shuffle
    # shuffle(lst)
    # # lst = [4, None, 2, None, 1, 3]
    # print(lst)
    # # print(find_idx(lst, mfind_none))
    # print(find_idx(lst, mfind_min))
