import uuid

from pydantic import BaseModel

class ModelQueryConverter:
    __types = {
        'int'   : "integer",
        'float' : "float(24)",
        'str'   : "text",
        int     : "integer",
        float   : "float(24)",
        str     : "text",
        uuid.UUID  : 'uuid'
    }

    def __init__(self, table: str, model) -> None:
        self.table = table
        self.model = model
        self.internal_columns = {}

    def __all_columns(self) -> dict[str, str]:
        res = {}
        fs = self.model.model_fields
        for field in fs:
            tp = fs[field].annotation
            if isinstance(tp, str):
                tp_str = str(tp).split('|')[0].strip()
                # print('type string:', tp_str)
                tp = self.__types.get(tp_str, tp)

            res[field] = self.__types.get(tp, tp)
        
        for field in self.internal_columns:
            tp = self.internal_columns[field]
            res[field] = self.__types.get(tp, tp)

        return res

    def add_internal_columns(self, columns: dict) -> None:
        self.internal_columns.update(columns)

    def create_query(self) -> str:
        query = ''

        schema = self.table.split('.')[0]

        fields = []
        fs = self.__all_columns()
        for field in fs:
            tp = fs[field]
            fields.append(f'{field} {tp}')
        fields = ', '.join(fields)

        if '.' in self.table:
            query += f'CREATE SCHEMA IF NOT EXISTS {schema};'

        query += f"""
            DROP TABLE IF EXISTS {self.table};
            CREATE TABLE 
            {self.table}
            (
                {fields}
            );
        """

        # print(query)

        return query 
    
    def insert_query(self) -> str:
        field_count = len(self.model.model_fields)
        query = f"""
            INSERT INTO 
            {self.table}
            ({', '.join(self.model.model_fields.keys())}) VALUES
            ({', '.join(['%s'] * field_count)})
        """
        # print(query)
        return query
    
    def select_query(self, condition: str = None, return_internal = False) -> str:
        cond = ''
        if condition:
            cond = f"WHERE {condition}"

        fields = []
        if return_internal:
            fields = self.__all_columns().keys()
        else:
            fields = self.model.model_fields.keys()

        query = f"""
            SELECT {', '.join(fields)}
            FROM {self.table}
            {cond};
        """
        # print(query)
        return query
    
    def update_query(self, condition: str = None, field_subset: list = None) -> str:
        # pairs = []
        fields = self.model.model_fields.keys()
        # fields = model_object.dump().keys()
        pairs = [f'{field} = %s' for field in fields]

        if field_subset:
            field_subset = set(field_subset)
            fields = [ field for field in fields if field in field_subset ]
            

        cond = ''
        if condition:
            cond = f"WHERE {condition}"

        query = f"""
            UPDATE {self.table}
            SET
                {', '.join(pairs)}
            {cond}
        """
        return query

    def model2list(self, obj: BaseModel):
        def transform(val):
            if isinstance(val, uuid.UUID):
                return val.hex
            # if isinstance(val, str):
            #     return f"'{val}'"
            return val
        dump = obj.model_dump()
        # print('dump:', dump)
        dump = [transform(dump[d]) for d in dump]
        return dump


if __name__ == '__main__':
    class CarModel(BaseModel):
        year        : int
        make        : str
        model       : str

    car = CarModel(
        year  =  1900,
        make  = 'hmmm',
        model = 'Ford T'
    )

    mcq = ModelQueryConverter('schema1.table1', CarModel)
    mcq.add_internal_columns({
        'car_id': 'SERIAL PRIMARY KEY',
    })
    print(mcq.create_query())
    print(mcq.insert_query())
    print(mcq.select_query())
    print(mcq.update_query('car_id = 1'))
    print(mcq.select_query('year > 1990'))
    print(mcq.select_query('year > 1990', return_internal = True))