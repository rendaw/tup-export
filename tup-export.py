import argparse
import sqlite3
import os
import collections
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Outputs a dumb script to build a tup project.',
    )
    parser.add_argument(
        'output', 
        help='Output script filename. Use - to write to stdout.'
    )
    args = parser.parse_args()

    os.system('tup scan')
    db = sqlite3.connect('.tup/db')
    dbc = db.cursor()

    def get_path(nid):
        parts = []
        while True:
            result = dbc.execute(
                'SELECT dir, name FROM node WHERE id = :id', 
                {'id': nid},
            ).fetchone()
            if result is None:
                break
            ndir, nname = result
            parts.append(nname)
            nid = ndir
        return os.path.sep.join(reversed(parts))

    # Find all commands
    commands = {
            nid: {
            'command': command,
            'dir': ndir,
            'from': [],
            'to': [],
        } for nid, ndir, command in dbc.execute(
            'SELECT id, dir, name FROM node WHERE type = 1').fetchall()
    }

    # Find command links and dependencies
    starters = []
    for nid, command in commands.items():
        for (target_nid,) in dbc.execute(
                'SELECT to_id FROM normal_link WHERE from_id = :nid', 
                {'nid': nid}
                ).fetchall():
            for (target_nid2,) in dbc.execute(
                    'SELECT to_id FROM normal_link WHERE from_id = :nid', 
                    {'nid': target_nid}
                    ).fetchall():
                command['to'].append(target_nid2)
                commands[target_nid2]['from'].append(nid)
        if not command['to']:
            starters.append((nid, command))

    # Serialize link order using depth first walk
    ordered_commands = collections.OrderedDict()

    def order_command(nid, command):
        for nnid in command['from']:
            ncommand = commands.get(nnid)
            order_command(nnid, ncommand)
        ordered_commands[nid] = command

    for nid, command in starters:
        order_command(nid, command)

    # Write ordered commands to output file
    def write_commands(file):
        for nid, command in ordered_commands.items():
            file.write('(cd {} && '.format(get_path(command['dir'])))
            file.write(command['command'])
            file.write(')\n')

    if args.output == '-':
        write_commands(sys.stdout)
    else:
        with open(args.output, 'w') as file:
            write_commands(file)

if __name__ == '__main__':
    main()
