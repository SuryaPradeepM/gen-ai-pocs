import traceback
from pathlib import Path

try:
    from sqlalchemy import create_engine, inspect, text

    p = Path(__file__).parent.parent / "hr_data.db"
    print("Exists:", p.exists(), "Size:", p.stat().st_size if p.exists() else "NA")
    url = f"sqlite:///{p.as_posix()}"
    print("URL:", url)
    engine = create_engine(url, connect_args={"check_same_thread": False}, echo=False)
    insp = inspect(engine)
    print("inspector.get_table_names():", insp.get_table_names())
    with engine.connect() as conn:
        res = conn.execute(
            text('SELECT name, type FROM sqlite_master WHERE type IN ("table","view");')
        )
        rows = list(res)
        print("sqlite_master rows count:", len(rows))
        for r in rows:
            print(" ", r)
except Exception:
    traceback.print_exc()
