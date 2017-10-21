import json

import tools
from schema import SchemaManager
from sfexport import SFExporter
from sfimport import SFImporter
import argparse


def debug(o):
    s = json.dumps(o, sort_keys=True, indent=4, separators=(',', ': '))
    print(s)


def load_file_items(filename):
    with open(filename, 'r') as f:
        line_list = f.readlines()
        stripped_list = [line.strip() for line in line_list if len(line) > 0]
        return stripped_list


def make_arg_list(args_list):
    processed_args = []
    for arg in args_list:
        if len(arg) == 0:
            continue
        if arg.startswith('@'):
            processed_args.extend(load_file_items(arg[1:]))
        else:
            processed_args.append(arg)
    return processed_args


if __name__ == '__main__':
    parser = argparse.ArgumentParser(epilog='@file arguments designate a file containing actual arguments, one per line')
    parser.add_argument("--env", help="Environment/DB settings name", metavar="env_name", required=True)
    parser.add_argument("--sync", help="sync table updates", nargs="*", metavar="object|@file")
    parser.add_argument("--schema", help="load sobject schema and create tables", nargs="*", metavar="object|@file")
    parser.add_argument("--export", help="export full sobject data", nargs="+", metavar="object|@file")
    parser.add_argument("--load", help="load/import full table data, table must be empty", nargs="*", metavar="object|@file")
    parser.add_argument("--inspect", help="inspect objects", nargs="*", metavar="object|@file")
    parser.add_argument("--init", help="initialize configuration", nargs="*")
    parser.add_argument("--sample", help="only export a sample of data", nargs="*")
    args = parser.parse_args()

    envname = args.env

    #    env, dbmgr, sf = tools.setup_env(envname)
    context = tools.setup_env(envname)
    schema_mgr = SchemaManager(context)


    if args.init is not None:
        sobject_list = schema_mgr.inspect()
        sobjectconfig = []
        for sobject in sobject_list:
            name = sobject['name']
            node = { 'name': name, 'enabled':False, 'auto-drop-columns': True, 'auto-create-columns': True, 'sync-schedule': 'always' }
            sobjectconfig.append(node)
        configmap = {'configuration': { 'sobjects': sobjectconfig }}
        context.filemgr.save_config(configmap)
        print('config.json created')

    if args.inspect is not None:
        thelist = schema_mgr.inspect()
        for entry in thelist:
            print(entry['name'])


    if args.sync is not None:
        exp = SFExporter(context)
        if len(args.sync) > 0:
            final_args = make_arg_list(args.sync)
            exp.sync_tables(schema_mgr, final_args)
        else:
            exp.sync_tables(schema_mgr)

    if args.schema is not None:
        if len(args.schema) > 0:
            final_args = make_arg_list(args.schema)
            schema_mgr.exportSObject(final_args)
        else:
            schema_mgr.export_sobjects()

    if args.export is not None:
        exp = SFExporter(context)
        table_list = make_arg_list(args.export)
        for tablename in table_list:
            exp.export_copy(tablename, just_sample=args.sample is not None)

    if args.load and len(args.load) > 0:
        imp = SFImporter(context, schema_mgr)
        table_list = make_arg_list(args.load)
        for tablename in table_list:
            print('loading {}'.format(tablename))
            count = imp.bulk_load(tablename)
            print('loaded {} records'.format(count))

            # if args.updates and len(args.updates) > 0:
            #    exp = SFExporter()
            #    for tablename in args.updates:
            #        stamp = dbmgr.getMaxTimestamp(tablename)
            #        if not stamp is None:
            #            print('stamp=' + stamp)
            #        exp.export_copy(dbmgr, sf, tablename, timestamp=stamp)
