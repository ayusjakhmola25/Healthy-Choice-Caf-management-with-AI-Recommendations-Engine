import pandas as pd
from app import app, db, FoodItem

def init_database():
    # 1. CSV file read karein
    # Make sure filename wahi ho jo aapne upload kiya
    df = pd.read_csv('FoodItem_export_clean.csv')

    # 2. App context ke andar database create karein
    with app.app_context():
        # Drop existing table to recreate with new schema
        db.drop_all()
        db.create_all()

        print("Database tables recreated.")

        # 3. Loop through CSV data and add to DB
        added_names = set()  # Track added item names to avoid duplicates
        for index, row in df.iterrows():
            # Check for duplicates by name
            item_name = row['name']
            if item_name in added_names:
                print(f"Skipping duplicate item: {item_name}")
                continue

            # Yahan check karein ki 'row' ke keys aapke CSV header se match karein
            # Map external URLs to local images (without /static/ prefix since url_for adds it)
            image_mapping = {
                'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400': 'images/indian.jpeg',
                'https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400': 'images/chaap1.jpeg',
                'https://images.unsplash.com/photo-1630383249896-424e482df921?w=400': 'images/healthy.jpeg',
                'https://images.unsplash.com/photo-1625937286074-9ca519d5d9df?w=400': 'images/healthy.jpeg',
                'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400': 'images/healthy.jpeg',
                'https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=400': 'images/healthy.jpeg',
                'https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400': 'images/healthy.jpeg',
                'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=400': 'images/chaap1.jpeg',
                'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400': 'images/pizza1.jpeg',
                'https://images.unsplash.com/photo-1626074353765-517a681e40be?w=400': 'images/indian.jpeg',
                'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400': 'images/indian.jpeg',
                'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400': 'images/healthy.jpeg',
                'https://images.unsplash.com/photo-1607920591413-4ec007e70023?w=400': 'images/cake1.jpeg',
                'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400': 'images/burger1.jpeg',
                'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400': 'images/burger1.jpeg',
                'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400': 'images/healthy.jpeg',
                'https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=400': 'images/cake1.jpeg'
            }

            local_image_url = image_mapping.get(row['image_url'], 'images/healthy.jpeg')  # Default fallback

            new_item = FoodItem(
                name=row['name'],          # CSV column: name
                category=row['category'],  # CSV column: category
                price=int(row['price']),   # CSV column: price
                description=row['description'], # CSV column: description
                image_url=local_image_url,    # Use local image path
                rating=4.5,  # Default rating since not in CSV
                protein=float(row['protein']) if pd.notna(row['protein']) else 0.0,
                carbs=float(row['carbs']) if pd.notna(row['carbs']) else 0.0,
                fats=float(row['fats']) if pd.notna(row['fats']) else 0.0,
                calories=int(row['calories']) if pd.notna(row['calories']) else 0
            )
            db.session.add(new_item)
            added_names.add(item_name)

        db.session.commit()
        print("Data imported successfully from CSV to Database!")

if __name__ == "__main__":
    init_database()
