from ..custom_exc import InvalidField, MissingKey

class SqlHelper:

    def __init__(self):
        self._prep_stmt = ""


    def format_input(self, v):
        if isinstance(v, str):
            return f'"{v}"'
        elif isinstance(v, int)\
            or isinstance(v, float):
            return v
        raise InvalidField(f'invalid datatype passed: {type(v)}')
    

    def validate_input(self, values, v):
        if isinstance(v, list) or isinstance(v, tuple):
            temp = []
            for x in v:
                temp.append(self.format_input(x))
            values.append(','.join(temp))
        else:
            values.append(self.format_input(v))

    '''
    Takes in a list of objects and converts them into a prepared statement dynamically
    For each object in the list, it must be checked against schema to prevent SQL injection
    '''
    def generate_insert(self, table: str, entries: list):
        values = []

        if not all(isinstance(x, dict) for x in entries):
            raise InvalidField('entries must be a list of dicts')
        
        col_headers = [x for x in entries[0]] # ordered keys

        for entry in entries:
            temp = ""
            for column in col_headers:
                if column not in entry:
                    raise MissingKey(f'missing key for sql parsing: {column}')
                temp += f'{self.format_input(entry[column])},'
            values.append(f"({temp[:-1]})")

        self._prep_stmt = f"INSERT INTO {table} ({','.join(col_headers)}) VALUES {','.join(values)}"
        return self
        
    '''
    Takes a prepared statement, and replaces dynamic parameters with %s
    Sets cls.prep_stmt and cls.values as a tuple for cursor execute
    '''
    def replace(self, sql_metadata, payload):
        values = []
        for kw in sql_metadata['sql_helper']:
            if kw not in payload:
                raise MissingKey(f'missing key for string replacement: {kw}')
            
            self.validate_input(values, payload[kw])
        self._prep_stmt = sql_metadata['prep_stmt'].format(*values)
        return self # allow chaining
    

    def query(self, cursor):
        cursor.execute(self._prep_stmt)




