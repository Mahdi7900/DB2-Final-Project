import pandas as pd
import psycopg2
from psycopg2 import sql
import csv


def connect_to_database():
    try:
        connection = psycopg2.connect(
            dbname="playStore",
            user="myuser",
            password="admin",
            host="localhost",
            port="5432"
        )
        print("Database connection successful.")
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None


def load_csv_to_database(csv_file, connection):
    if connection is None:
        print("No database connection available.")
        return

    try:
        df = pd.read_csv(csv_file)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM categories;")
        category_count = cursor.fetchone()[0]

        if category_count == 0:
            print("Inserting data into categories table...")
            unique_categories = df['Category'].drop_duplicates(
            ).dropna()
            for category in unique_categories:
                cursor.execute(
                    "INSERT INTO categories (category_name) VALUES (%s) ON CONFLICT DO NOTHING;",
                    (category,)
                )

        connection.commit()

        category_map = {}
        cursor.execute("SELECT category_id, category_name FROM categories;")
        for row in cursor.fetchall():
            category_map[row[1]] = row[0]

        print("Checking if developers table needs to be populated...")
        cursor.execute("SELECT COUNT(*) FROM developers;")
        developer_count = cursor.fetchone()[0]

        if developer_count == 0:
            print("Inserting data into developers table...")
            unique_developers = df[['Developer Id', 'Developer Website',
                                    'Developer Email']].drop_duplicates().dropna(how='all')
            for _, developer in unique_developers.iterrows():
                cursor.execute(
                    """
                    INSERT INTO developers (developer_name, developer_website, developer_email)
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;
                    """,
                    (
                        developer['Developer Id'],
                        developer['Developer Website'] if pd.notna(
                            developer['Developer Website']) else None,
                        developer['Developer Email'] if pd.notna(
                            developer['Developer Email']) else None
                    )
                )
        connection.commit()

        developer_map = {}
        cursor.execute("SELECT developer_id, developer_name FROM developers;")
        for row in cursor.fetchall():
            developer_map[row[1]] = row[0]

        df['category_id'] = df['Category'].map(category_map).astype(int)

        df['developer_id'] = df['Developer Id'].map(developer_map)
        df = df.dropna(subset=['developer_id'])

        df['Rating'] = pd.to_numeric(
            df['Rating'], errors='coerce').fillna(0).astype(float)

        df['Rating Count'] = pd.to_numeric(
            df['Rating Count'], errors='coerce').fillna(0).astype(int)

        df['Installs'] = df['Installs'].astype(str).str.replace(
            '+', '', regex=True).str.replace(',', '', regex=True)
        df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

        df['Minimum Installs'] = pd.to_numeric(
            df['Minimum Installs'], errors='coerce').fillna(0).astype(int)

        df['Maximum Installs'] = pd.to_numeric(
            df['Maximum Installs'], errors='coerce').fillna(0).astype(int)

        df['Free'] = df['Free'].apply(lambda x: True if str(
            x).strip().lower() == 'true' else False)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

        df['Size'] = df['Size'].astype(str).str.replace(
            'M', '', regex=True).str.replace('k', '', regex=True)
        df['Size'] = pd.to_numeric(
            df['Size'], errors='coerce').fillna(0).astype(int)

        df['Minimum Android'] = df['Minimum Android'].astype(str).str.replace(
            'Varies with device', '', regex=False)
        df['Minimum Android'] = df['Minimum Android'].apply(
            lambda x: x.split()[0] if 'and' in x.lower() else None)
        df['Minimum Android'] = pd.to_numeric(
            df['Minimum Android'], errors='coerce')
        df['Minimum Android'] = df['Minimum Android'].fillna(1)

        df['Released'] = pd.to_datetime(df['Released'], errors='coerce')
        df['Last Updated'] = pd.to_datetime(
            df['Last Updated'], errors='coerce')

        df['Ad Supported'] = df['Ad Supported'].apply(
            lambda x: True if str(x).strip().lower() == 'true' else False)
        df['In App Purchases'] = df['In App Purchases'].apply(
            lambda x: True if str(x).strip().lower() == 'true' else False)
        df['Editors Choice'] = df['Editors Choice'].apply(
            lambda x: True if str(x).strip().lower() == 'true' else False)
        df['Scraped Time'] = pd.to_datetime(
            df['Scraped Time'], errors='coerce')

        apps_data = df[
            ['App Name', 'category_id', 'Rating', 'Rating Count', 'Installs', 'Minimum Installs',
             'Maximum Installs', 'Free', 'Price', 'Currency', 'Size', 'Minimum Android',
             'developer_id', 'Released', 'Last Updated', 'Content Rating', 'Ad Supported',
             'In App Purchases', 'Editors Choice', 'Scraped Time']
        ]

        temp_csv = "temp_apps.csv"
        apps_data.to_csv(temp_csv, index=False, header=False,
                         encoding='utf-8', float_format='%.0f',
                         quoting=csv.QUOTE_ALL, escapechar="\\")

        with open(temp_csv, 'r', encoding='utf-8') as f:
            cursor.copy_expert(
                sql.SQL("""
                COPY apps (
                    app_name, category_id, rating, rating_count, installs, minimum_installs,
                    maximum_installs, is_free, price, currency, size, minimum_android_version,
                    developer_id, released, last_updated, content_rating, ad_supported,
                    in_app_purchases, editors_choice, scraped_time
                )
                FROM STDIN
                WITH (
                    FORMAT CSV,
                    DELIMITER ',',
                    QUOTE '"',
                    ESCAPE '"',
                    NULL ''
                );
            """),
                f
            )
        connection.commit()
        print("Data insertion completed successfully.")

    except Exception as e:
        print(f"Error loading data into the database: {e}")
        connection.rollback()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    csv_file = "cleaned_Playstore.csv"
    db_connection = connect_to_database()
    if db_connection:
        load_csv_to_database(csv_file, db_connection)
