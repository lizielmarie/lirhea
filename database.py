from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Replace this with your actual Supabase connection string
DATABASE_URL = 'postgresql://postgres.gjtafvojuzpnfbviejdy:y4NOLvNA4Erb3on6@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    print('Tables created successfully.')

def get_session():
    return SessionLocal()