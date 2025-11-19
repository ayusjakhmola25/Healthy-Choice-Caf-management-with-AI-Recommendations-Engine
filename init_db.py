import pandas as pd
from app import app, db, FoodItem

def init_database():
    # 1. CSV file read karein
    # Make sure filename wahi ho jo aapne upload kiya
    df = pd.read_csv('FoodItem_export_clean.csv')

    # 2. App context ke andar database create karein
    with app.app_context():
        db.create_all()  # Purana table hata kar naya banayega (agar exist karta hai)

        print("Database tables created.")

        # 3. Loop through CSV data and add to DB
        for index, row in df.iterrows():
            # Yahan check karein ki 'row' ke keys aapke CSV header se match karein
            new_item = FoodItem(
                name=row['name'],          # CSV column: name
                category=row['category'],  # CSV column: category
                price=int(row['price']),   # CSV column: price
                description=row['description'], # CSV column: description
                image_url=row['image_url'],    # CSV column: image_url
                rating=4.5  # Default rating since not in CSV
            )
            db.session.add(new_item)

        db.session.commit()
        print("Data imported successfully from CSV to Database!")

if __name__ == "__main__":
    init_database()
