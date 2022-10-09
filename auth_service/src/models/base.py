import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper


class BaseModelClass:
    __hidden_fields__ = {'password'}

    def __repr__(self):
        order = [i for i in self.__class__.__dict__.keys() if not i.startswith('_')]
        local_attrs = [i for i in class_mapper(self.__class__).iterate_properties if
                       i.key not in self.__hidden_fields__]
        local_attrs.sort(key=lambda x: order.index(x.key))
        attrs_repr = [f'{i.key}={getattr(self, i.key, None)}' for i in local_attrs if
                      isinstance(i, sqlalchemy.orm.ColumnProperty)]

        return f'{self.__class__.__name__}({", ".join(attrs_repr)})'


Base = declarative_base(cls=BaseModelClass)
metadata = Base.metadata
metadata.naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

WYSIWYG_LENGTH = 32768
WYSIWYG_TITLE_LENGTH = 512
