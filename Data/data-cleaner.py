import pandas as pd


def load_data(file_path):
    try:
        chunk_size = 100000
        chunks = pd.read_csv(file_path, chunksize=chunk_size)
        return pd.concat(chunks, ignore_index=True)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def clean_data(df):
    if df is None:
        return None

    df.drop_duplicates(inplace=True)

    df.dropna(subset=['App Name', 'App Id', 'Category',
              'Rating', 'Installs'], inplace=True)

    df['Free'] = df['Free'].apply(lambda x: str(x).strip().lower() == 'true')

    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df.loc[df['Free'] == True, 'Price'] = 0

    df['Currency'] = df['Currency'].str.strip().str.upper()

    def parse_size(size):
        if isinstance(size, str) and size.lower() in ['varies with device']:
            return None
        size = str(size).replace('M', '').replace('k', '')
        try:
            return float(size) * 1000 if 'k' in size else float(size)
        except ValueError:
            return None
    df['Size'] = df['Size'].apply(parse_size)

    def parse_android_version(version):
        if pd.isnull(version) or not isinstance(version, str):
            return None
        return version.split()[0]
    df['Minimum Android'] = df['Minimum Android'].apply(parse_android_version)

    df['Released'] = pd.to_datetime(
        df['Released'], format='%b %d, %Y', errors='coerce')
    df['Last Updated'] = pd.to_datetime(
        df['Last Updated'], format='%b %d, %Y', errors='coerce')

    for col in ['Ad Supported', 'In App Purchases', 'Editors Choice']:
        df[col] = df[col].apply(lambda x: str(x).strip().lower() == 'true')

    df['Content Rating'] = df['Content Rating'].str.strip().str.lower()

    df['Rating Count'] = pd.to_numeric(df['Rating Count'], errors='coerce')
    df['Installs'] = df['Installs'].str.replace(
        '+', '', regex=True).str.replace(',', '', regex=True)
    df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

    df['Scraped Time'] = pd.to_datetime(df['Scraped Time'], errors='coerce')

    df.dropna(subset=['Rating', 'Installs', 'Minimum Android',
              'Released', 'Last Updated'], inplace=True)

    return df


def save_data(df, output_file):
    if df is None:
        print("No data to save.")
        return

    try:
        df.to_csv(output_file, index=False)
        print(f"Cleaned data saved to {output_file}")
    except Exception as e:
        print(f"Error saving data: {e}")


def process_csv(input_file, output_file):
    print("Loading data...")
    data = load_data(input_file)

    if data is not None:
        print("Cleaning data...")
        cleaned_data = clean_data(data)

        if cleaned_data is not None:
            print("Saving cleaned data...")
            save_data(cleaned_data, output_file)


if __name__ == "__main__":
    input_file = "Google-Playstore.csv"
    output_file = "cleaned_Playstore.csv"
    process_csv(input_file, output_file)
