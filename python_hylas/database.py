from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL


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
    engine = connect(settings)
    conn = engine.raw_connection()
    sql = "SELECT * FROM {}.summary WHERE summary_hash='{}'".format(schema, summary_hash)
    summary = conn.execute(sql)
    if summary:
        sql = "SELECT * FROM {}.results WHERE summary_id='{}'".format(schema, summary_hash)
        results = conn.execute(sql)
        return results
    else:
        return False