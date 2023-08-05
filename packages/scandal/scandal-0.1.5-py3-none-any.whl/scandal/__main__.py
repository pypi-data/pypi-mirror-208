from scandal import connect

if __name__ == "__main__":
    with connect(org="fulcrum", project="loyal-road-382017") as conn:
        conn.cursor().execute("SELECT 1")
