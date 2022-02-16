#!/usr/bin/env python3
##
# Feed this script a andOTP JSON Backup.
#
# https://github.com/vs49688/scripts/
# Zane van Iperen <zane@zanevaniperen.com>
#
# SPDX-License-Identifier: CC0-1.0
#
# * Make sure all arguments are LaTeX compatible
# * `qrencode` needs to be installed
# * Compile the resulting .tex file with pdflatex/xelatex
#
# Usage: totpcvt.py <name> <email>
##

import json
import sys
import urllib.parse
import re
from collections import namedtuple
import subprocess
import os.path


class Entry(object):
    __slots__ = [
        'filename',
        'issuer',
        'label',
        'username',
        'algorithm',
        'digits',
        'secret',
        'type',
        'period',  # TOTP only, optional, default 30
        'counter', # HOTP only
    ]

    def build_url(self) -> str:
        query = {
            'secret': ee.secret,
            'issuer': ee.issuer
        }

        if ee.algorithm != 'SHA1':
            query['algorithm'] = ee.algorithm

        if ee.digits != 6:
            query['digits'] = ee.digits

        if ee.period and ee.period != 30:
            query['period'] = ee.period

        if ee.counter:
            query['counter'] = ee.counter

        return urllib.parse.urlunparse((
            'otpauth',
            '',
            urllib.parse.quote(os.path.join('//', ee.type.lower(), f'{ee.issuer}:{ee.label}')),
            '',
            urllib.parse.urlencode(query),
            ''
        ))


REGEX_LABEL = re.compile(r'^(?:(.+):)?(.+)$')

if len(sys.argv) != 3:
    print('Usage: {0} <name> <email>'.format(sys.argv[0]), file=sys.stderr)
    exit(2)

name = sys.argv[1]
email = sys.argv[2]

data = json.loads(sys.stdin.read())

urls = []

# Quickly check this before doing anything
for e in data:
    if 'issuer' in e:
        continue

    print('issuer not found in backup, please upgrade your andOTP and re-export', file=sys.stderr)
    exit(1)

i = 0
for e in data:

    ee = Entry()
    ee.algorithm = e['algorithm']
    ee.digits = int(e['digits'])
    ee.secret = e['secret']
    ee.label = e['label']
    ee.issuer = e['issuer']
    ee.type = e['type']
    ee.period = ''

    # These won't actually import correctly, but the user
    # should be able to decode it and add it manually
    if ee.type == 'TOTP':
        ee.period = int(e['period'])
        ee.counter = None
    elif ee.type == 'HOTP':
        ee.period = None
        ee.counter = int(e['counter'])
    elif ee.type == 'STEAM':
        ee.period = None
        ee.counter = None
    else:
        raise Exception(f'unknown type {ee.type}')

    m = re.match(REGEX_LABEL, ee.label)
    if not m:
        raise Exception(f'invalid label {ee.label}')

    ee.filename = 'qr_{0:0>2}.png'.format(i)
    ee.username = m[2]

    subprocess.run(['qrencode', '-t', 'PNG', '-v', '10', '-o', ee.filename, '--', ee.build_url()], check=True)
    urls.append(ee)
    #print('\\noindent\\includegraphics{{../qr_{0:0>2}.png}}'.format(i))
    i += 1


#print(urls)

print(rf"""
\documentclass[oneside]{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{parskip}}
\usepackage{{hyperref}}
\usepackage{{xurl}}
\usepackage{{fancyhdr}}
\usepackage[style=default]{{datetime2}}
\usepackage{{lastpage}}

\pagestyle{{fancy}}

\lhead{{Backup MFA Codes}}
\chead{{{name}}}
\rhead{{{email}}}

\lfoot{{Generated at \DTMnow}}
\cfoot{{}}
\rfoot{{Page \thepage\ of \pageref{{LastPage}}}}

\begin{{document}}
""")

for i in range(len(urls)):

    # if i % 6 == 0 and i != 0:
    #     print()
    #     print(r'    \newpage')

    if i % 2 == 0:
        print()

    secret = urls[i].secret
    sec = ' '.join([secret[i:i+4] for i in range(0, len(secret), 4)])

    typestring = f'{urls[i].type} -- {urls[i].algorithm} -- {urls[i].digits}'
    if urls[i].period:
        typestring = typestring + f' -- {urls[i].period}'

    print(r'    \begin{minipage}[t]{0.5\textwidth}')
    print(r'        \centering')
    print(r'        \includegraphics[width=0.9\textwidth]{{{0}}}'.format(urls[i].filename))
    print(fr"""
        \begin{{tabular}}{{p{{0.2\linewidth}}p{{0.7\linewidth}}}}
            Username  & \texttt{{{urls[i].username}}} \\
            Issuer    & {urls[i].issuer} \\
            Type      & {typestring} \\
            Secret    & \texttt{{{sec}}} \\
        \end{{tabular}}
""")
    print(r'        \vspace{\baselineskip}')
    print(r'    \end{minipage}', end='')
    
    if i % 2 == 0:
        print('%', end='')
    
    print()
        
print(r'\end{document}')
