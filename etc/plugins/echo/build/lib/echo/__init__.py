def convert(project, map, ins, tbl, dm, *args):
    print(project.project_name)
    print(map.id)
    print(dm.settings)
    print(ins, tbl, args)
    return f'echo: {args[0]}'
