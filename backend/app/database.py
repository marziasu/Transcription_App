from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
from .config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Determine pool class based on environment
def get_pool_class():
    """Use NullPool for serverless, QueuePool for traditional hosting"""
    if settings.is_serverless:  # Add this to your config
        return NullPool
    return QueuePool

# Connection Pool Configuration
engine = create_engine(
    settings.database_url,
    poolclass=get_pool_class(),
    
    # Pool settings (ignored if NullPool)
    pool_size=10,                  
    max_overflow=20,               
    pool_timeout=30,               
    pool_recycle=3600,             
    pool_pre_ping=True,            
    
    # Connection arguments
    connect_args={
        "connect_timeout": 10,      # Connection timeout
        "options": "-c timezone=utc"  # Set timezone
    },
    
    # Performance settings
    echo=False,                     # SQL logging (set True for debugging)
    echo_pool=False,                # Pool logging
    future=True                     # Use SQLAlchemy 2.0 style
)

# Event listener for connection checkout (optional monitoring)
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log when new connection is created"""
    logger.info("New database connection established")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when connection is checked out from pool"""
    logger.debug("Connection checked out from pool")

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Prevent lazy loading issues
)

Base = declarative_base()

def get_db():
    """
    Dependency for getting database session.
    Connection is returned to pool when session closes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Returns connection to pool

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

def check_db_connection():
    """Health check for database connection"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def dispose_engine():
    """Cleanup database connections (call on shutdown)"""
    engine.dispose()
    logger.info("Database connection pool disposed")
