from database.db_connection import engine, Base
from database.models import CleanedHealthcare

def init_db():
    print("Connecting to database and creating tables...")
    # This command looks at everything that inherits from 'Base' 
    # and creates the table if it doesn't exist.
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully!")

if __name__ == "__main__":
    init_db()