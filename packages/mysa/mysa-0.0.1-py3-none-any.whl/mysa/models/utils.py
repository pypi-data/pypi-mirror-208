from sqlalchemy.orm import declared_attr


class Tablename:
    _table_suffix = "s"

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        name = cls.__name__.replace("Model", "")
        table_name = name[0].lower()
        for word in name[1:]:
            if word.isupper() and table_name[-1] != "_":
                word = "_" + word
            table_name += word.lower()
        return table_name + cls._table_suffix
