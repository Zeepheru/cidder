import psycopg


def table_exists(conn: psycopg.Connection, table_name: str) -> bool:
    """Check if a table exists in the database.

    Args:
        conn (psycopg.Connection): Postgres connection.
        table_name (str): Table name to check.

    Returns:
        bool: Whether the table exists.
    """

    query = """
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = %s
    );
    """
    with conn.cursor() as cur:
        cur.execute(query, (table_name,))
        return cur.fetchone()[0]
