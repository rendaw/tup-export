import argparse
import sqlite3
import os
import collections
import sys
import re

def main():
    parser = argparse.ArgumentParser(
        description='Outputs a dumb script to build a tup project.',
    )
    parser.add_argument(
        'output', 
        help='Output script filename. Use - to write to stdout.'
    )
    parser.add_argument(
        '-n', 
        '--noscan', 
        help='Don\'t scan before generating.',
        action='store_true',
    )
    args = parser.parse_args()

    if not args.noscan:
        os.system('tup scan')

    db = sqlite3.connect('.tup/db')
    dbc = db.cursor()

    # Find all commands
    commands = {
            nid: {
            'command': re.sub(r'^\^c\^ ', '', command),
            'dir': ndir,
            'from': [],
            'to': [],
        } for nid, ndir, command in dbc.execute(
            'SELECT id, dir, name FROM node WHERE type = 1').fetchall()
    }

    # Find command links and dependencies
    def get_next_commands(nid):
        stage = [
            target_nid for (target_nid,) in dbc.execute(
                'SELECT to_id FROM normal_link WHERE from_id = :nid', 
                {'nid': nid}
            ).fetchall()
        ]
        out = []
        for nnid in stage:
            for ntype in dbc.execute(
                    'SELECT type FROM node WHERE id = :nid', 
                    {'nid': nid},
                    ):
                if ntype == 1:
                    out.append(nnid)
                else:
                    out.extend(get_next_commands(nnid))
        return out

    starters = []
    for nid, command in commands.items():
        for target_nid in get_next_commands(nid):
            command['to'].append(target_nid)
            commands[target_nid]['from'].append(nid)
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

    def write_commands(file):
        last_path = None
        for nid, command in ordered_commands.items():
            path = get_path(command['dir'])
            if path != last_path:
                if last_path != None:
                    file.write('cd \'{}\'\n'.format(os.path.relpath('.', last_path)))
                file.write('cd \'{}\'\n'.format(path))
            for groupname in set(
                    re.findall(r'%<([^>]+)>', command['command'])):
                gid, = dbc.execute(
                    'SELECT id FROM node WHERE name = :name',
                    {'name': '<{}>'.format(groupname)}
                ).fetchone()
                members = []
                for mid, in dbc.execute(
                        'SELECT from_id FROM normal_link JOIN node ON node.id = normal_link.from_id WHERE to_id = :nid AND node.type = 4',
                        {'nid': gid},
                        ).fetchall():
                    members.append('\'{}\''.format(
                        os.path.normpath(
                            os.path.join(
                                os.path.relpath('.', path), 
                                get_path(mid)
                            )
                        )
                    ))
                command['command'] = re.sub(
                    r'%<{}>'.format(groupname), 
                    ' '.join(members),
                    command['command'],
                )
            file.write(command['command'])
            file.write('\n')
            last_path = path

    if args.output == '-':
        write_commands(sys.stdout)
    else:
        with open(args.output, 'w') as file:
            write_commands(file)

if __name__ == '__main__':
    main()
