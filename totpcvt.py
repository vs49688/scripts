#!/usr/bin/env python3
##
# Feed this script a andOTP JSON Backup.
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

import subprocess

REGEX_LABEL = re.compile(r'^(.+) - (.+)$')

if len(sys.argv) != 3:
    print('Usage: {0} <name> <email>'.format(sys.argv[0]), file=sys.stderr)
    exit(2)

name = sys.argv[1]
email = sys.argv[2]

data = json.loads(sys.stdin.read())

urls = []

i = 0
for e in data:
    query = {
        'algorithm': e['algorithm'],
        'digits': int(e['digits']),
        'secret': e['secret']
    }

    if e['type'] != 'STEAM':
        query['period'] = int(e['period'])

    # andOTP puts a "-" in between the label and issuer
    m = re.match(REGEX_LABEL, e['label'])
    if m:
        label, issuer = m[1], m[2]
    else:
        label, issuer = e['label'], e['label']
    
    query['issuer'] = issuer

    parts = [
        'otpauth',
        e['type'].lower(),
        urllib.parse.quote(label),
        '',
        urllib.parse.urlencode(query),
        ''
    ]

    url = urllib.parse.urlunparse(parts)
    filename = 'qr_{0:0>2}.png'.format(i)
    subprocess.run(['qrencode', '-t', 'PNG', '-v', '10', '-o', filename, '--', url], check=True)
    urls.append((url, filename, label, issuer))
    #print('\\noindent\\includegraphics{{../qr_{0:0>2}.png}}'.format(i))
    i += 1


#print(urls)

print(r"""\documentclass[oneside]{article}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{parskip}
\usepackage{hyperref}
\usepackage{xurl}
\usepackage{fancyhdr}
\usepackage[style=default]{datetime2}
\usepackage{lastpage}

\pagestyle{fancy}

\fancyhf[HL]{\DTMnow}""")

print(r'\fancyhf[HC]{{Backup TOTP Codes -- {0} -- {1}}}'.format(name, email))


print(r"""
\fancyhf[HR]{Page \thepage\ of \pageref{LastPage}}
\fancyhf[FLCR]{}

\begin{document}""")

for i in range(len(urls)):

    # if i % 6 == 0 and i != 0:
    #     print()
    #     print(r'    \newpage')

    if i % 3 == 0:
        print()

    safeurl = urls[i][0].replace('%', '\\%')
    #safeurl = safeurl.replace('&', '\\&')
    #safeurl = safeurl.replace('_', '\\_')

    print(r'    \begin{minipage}[t]{0.33\textwidth}')
    print(r'        \centering')
    print(r'        \includegraphics[width=0.9\textwidth]{{{0}}}'.format(urls[i][1]))
    print()
    print(r'        {0} \\ {1}'.format(urls[i][2], urls[i][3]))
    print(r'')
    print(r'        \vspace{\baselineskip}')
    print(r'        \texttt{{\url{{{0}}}}}'.format(safeurl))
    print(r'    \end{minipage}', end='')
    
    if i % 2 == 0:
        print('%', end='')
    
    print()
        
print(r'\end{document}')
