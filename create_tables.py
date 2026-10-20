import sys

import entities
from config.database import Base, engine

def main() -> None:
    if "--reset" in sys.argv:
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")
 
    Base.metadata.create_all(bind=engine)
    print("Tables created:", ", ".join(Base.metadata.tables))

if __name__ == "__main__":
    main()
