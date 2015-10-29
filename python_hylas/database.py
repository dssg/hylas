from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

district_table_map = {'vps': 'vancouver', 'wcpss': 'wake'}

def connect(settings):
    """
    Performs database connection using database settings from the environmental variable 'edu_db_string'.
    Connection URL is formatted as: postgresql://<username>:<password>@<host>/<database>
    Returns SQLAlchemy Engine instance.
    """
    try:
      engine = create_engine(URL(**settings))
      # Test database connection.
      connection = engine.connect()
      connection.close()
      return engine
    except Exception as e:
        e.args = ("Could not initialize database because: " + e.args[0],)
        raise e


def get_summary_features(settings, summary_hash, schema=None):
    schema = district_table_map[schema]
    engine = connect(settings)
    conn = engine.raw_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM {}.summary WHERE summary_hash='{}'".format(schema, summary_hash)
    cur.execute(sql)
    summary = cur.fetchone()
    if summary:
        sql = "SELECT * FROM {}.results WHERE summary_id='{}'".format(schema, summary_hash)
        results = cur.execute(sql)
        cur.close()
        conn.close()
        return results
    else:
        cur.close()
        conn.close()
        return False
