from django_tables2 import BooleanColumn, Column, Table


class ImportTemplateTable(Table):
    """Table to list import templates."""

    content_type = Column()
    name = Column()
    verbose_name = Column()
    has_header_row = BooleanColumn()
    has_index_col = BooleanColumn()

    class Meta:
        attrs = {"class": "highlight"}
