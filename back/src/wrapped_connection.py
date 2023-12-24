import psycopg2

class WrappedConnection:
    def __init__(self, host: str, port: int, db: str, un: str, pw: str) -> None:
        self.host = host
        self.port = port
        self.db = db
        self.un = un
        self.pw = pw
        self.conn = None

    def connect(self):
        if self.conn:
            self.conn.close()

        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.db, 
            user=self.un, 
            password=self.pw
        )
        self.conn = conn

        for row in self.execute_and_fetch_all('SELECT VERSION() as v'):
            print('Connect successful!\nVersion:', row['v'])

    def execute(self, query: str) -> None:
        curs = self.conn.cursor()

        curs.execute(query)
        # res = curs.fetchall()
        self.conn.commit()
        curs.close()
        # return res

    def executemany(self, query: str, data: list|None = None):
        curs = self.conn.cursor()
        data = data if data else ['-']
        # print('-- wrapper:')
        # print('query:\n', query)
        # print('data:\n',  data)
        # print('--\n')
        curs.executemany(query, data)
        self.conn.commit()
        curs.close()

    def __transform_row(self, desc: list, row: list) -> dict:
        # for d in desc:
        #     print(d)
        return dict(zip([d.name for d in desc], row))

    def __transform_many(self, desc: list, results: list[list]) -> list[dict]:
        dres = []
        for row in results:
            dres.append(self.__transform_row(desc, row))
        return dres
    
    def execute_and_fetch_all(self, query: str) -> dict:
        curs = self.conn.cursor()

        curs.execute(query)
        # res = curs.fetchall()
        res = self.__transform_many(curs.description, curs.fetchall())
        self.conn.commit()
        curs.close()

        return res

    def close(self):
        self.conn.close()