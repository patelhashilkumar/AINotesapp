from app import app, db, Note
from sqlalchemy import text

def migrate():
    with app.app_context():
        with db.engine.connect() as conn:
            # Check if order column exists
            result = conn.execute(text("PRAGMA table_info(note)"))
            columns = [row[1] for row in result]
            
            if 'order' not in columns:
                # Add order column
                conn.execute(text("ALTER TABLE note ADD COLUMN \"order\" INTEGER"))
                
                # Set initial order based on created_at
                conn.execute(text("""
                    UPDATE note 
                    SET "order" = (
                        SELECT COUNT(*) 
                        FROM note AS n2 
                        WHERE n2.created_at <= note.created_at
                    ) - 1
                """))
                
                conn.commit()
                print("Migration completed successfully!")
            else:
                print("Order column already exists.")

if __name__ == '__main__':
    migrate() 