from dbgear.models.datasources.base import BaseDataSource


class DataSource(BaseDataSource):
    """
    Example DataSource class that extends BaseDataSource.
    This class should implement the load method and any other necessary methods.
    """
    def __init__(self, **kwargs):
        print("Initializing Example DataSource with kwargs:", kwargs)

    def load(self):
        print("Loading data from example data source.")

    @property
    def filename(self) -> str:
        return "example_data_source.yaml"

    @property
    def data(self):
        yield {
            'key': 'example',
            'value': 'example_value',
            'update_date': 'NOW()',
            'update_user': 'SYSTEM'
        }
        yield {
            'key': 'another_example',
            'value': 'another_value',
            'update_date': 'NOW()',
            'update_user': 'SYSTEM'
        }
