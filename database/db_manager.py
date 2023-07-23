from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc


class DBManager:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def __enter__(self):
        self.session = self.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if not exc_type:
                self.session.commit()
            else:
                self.session.rollback()
                raise exc_type

        except Exception as e:
            print("Error while committing/rolling back the session: ", e)
            self.session.rollback()
            return False

        self.session.close()
        return True

    def insert(self, model, records_data):
        try:
            if isinstance(records_data, dict):
                records_data = [records_data]

            new_objects = [model(**record_data) for record_data in records_data]
            self.session.add_all(new_objects)

        except Exception as e:
            raise Exception("INSERT ERROR") from e

        return new_objects

    def get(
        self, model, columns=[], conditions=[],
        order_by=None, descending=False, limit=None
    ):
        try:
            query = self.session.query(*[getattr(model, column) for column in columns] or [model])
            query = query.filter(*[conditions])

            if order_by:
                if isinstance(order_by, str):
                    order_by = [order_by]

                order_columns = [getattr(model, col) for col in order_by]

                if descending:
                    order_columns = [desc(col) for col in order_columns]

                query = query.order_by(*order_columns)

            if limit:
                query = query.limit(limit)

            rows = query.all()

        except Exception as e:
            raise Exception("SELECT ERROR") from e

        return rows

    def update(self, model, updates, conditions=[]):
        try:
            query = self.session.query(model).filter(*[conditions])
            affected_rows_count = query.update(updates)

        except Exception as e:
            raise Exception("UPDATE ERROR") from e

        return affected_rows_count

    def delete(self, model, conditions=[]):
        try:
            query = self.session.query(model).filter(*[conditions])
            deleted_rows_count = query.delete()

        except Exception as e:
            raise Exception("DELETE ERROR") from e

        return deleted_rows_count


def main():
    pass


if __name__ == '__main__':
    main()
