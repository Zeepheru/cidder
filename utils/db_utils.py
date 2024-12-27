import psycopg


def table_exists(conn: psycopg.Connection, table_name: str) -> bool:
    """Check if a table exists in the database."""
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