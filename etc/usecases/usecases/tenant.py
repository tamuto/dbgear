from dbgear.models.mapping import Mapping


def retrieve(map: Mapping):
    print(f'in tenant: {map.name}')
    dbs = ['sample_testdb1', 'sample_testdb2']
    for db in dbs:
        cloned = map.model_copy(deep=True)
        cloned.tenant_name = db
        yield cloned
