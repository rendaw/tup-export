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
            'from': set([]),
            'to': set([]),
        } for nid, ndir, command in dbc.execute(
            'SELECT id, dir, name FROM node WHERE type = 1').fetchall()
    }
    output_dirs = set()

    # Find command outputs
    for nid, command in commands.items():
        for (oid,) in dbc.execute(
                'SELECT dir FROM normal_link JOIN node ON normal_link.to_id = node.id WHERE node.type = 4 AND normal_link.from_id = :nid', 
                {'nid': nid}
                ).fetchall():
            output_dirs.add(oid)

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
            ntype, = dbc.execute(
                'SELECT type FROM node WHERE id = :nid LIMIT 1', 
                {'nid': nnid},
            ).fetchone()
            if ntype == 1:
                out.append(nnid)
            else:
                out.extend(get_next_commands(nnid))
        return out

    starters = []
    for nid, command in commands.items():
        for target_nid in get_next_commands(nid):
            command['to'].add(target_nid)
            commands[target_nid]['from'].add(nid)
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
        file.write(
            '#! /usr/bin/env bash\n'
            'set -e\n'
            'set -x\n'
            'set -o pipefail\n'
        )

        # Create output directories
        for oid in output_dirs:
            file.write('mkdir -p {}\n'.format(get_path(oid)))

        # Commands
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
            file.write('{}  # nid {}'.format(command['command'], nid))
            file.write('\n')
            last_path = path

    if args.output == '-':
        write_commands(sys.stdout)
    else:
        with open(args.output, 'w') as file:
            write_commands(file)
        os.chmod(args.output, 0o755)

if __name__ == '__main__':
    main()
