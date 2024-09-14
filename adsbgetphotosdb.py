import requests
import sqlite3
import time
import io

def create_database():
    conn = sqlite3.connect('aircraft_images.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS images
    (hex TEXT PRIMARY KEY, image BLOB)
    ''')
    conn.commit()
    return conn

		
def get_hex_values():
    try:
        url = "https://hexdb.io/radar/data/aircraft.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        return [aircraft.get("hex") for aircraft in data.get("aircraft", [])]		
    except requests.exceptions.Timeout:
        print(f"The request to {url} timed out after 10 seconds.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while requesting {url}: {e}")
    return []	
		
		

def get_image_url(hex_value):
    try:
        url = f"https://hexdb.io/hex-image-thumb?hex={hex_value}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.text.strip()
    except requests.exceptions.Timeout:
        print(f"The request to {url} timed out after 10 seconds.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while requesting {url}: {e}")
    return None

		


def download_and_store_image(conn, url, hex_value):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        image_data = response.content
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO images (hex, image) VALUES (?, ?)", (hex_value, image_data))
        conn.commit()
        print(f"Downloaded and stored image for hex {hex_value}")		
        return		
    except requests.exceptions.Timeout:
        print(f"The request to {url} timed out after 10 seconds.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while requesting {url}: {e}")
    return 		
		


def image_exists_in_db(conn, hex_value):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM images WHERE hex = ?", (hex_value,))
    return cursor.fetchone() is not None

def main():
    conn = create_database()
    hex_values = get_hex_values()
    start_time = time.time()
    time_limit = 200
    for hex_value in hex_values:

        if time.time() - start_time > time_limit:
            print("Loop time limit. Exiting loop.")
        break
	    
        if image_exists_in_db(conn, hex_value):
            print(f"Image for hex {hex_value} already exists in database. Skipping.")
            continue
        
        image_url = get_image_url(hex_value)
        if image_url:
            download_and_store_image(conn, image_url, hex_value)
            time.sleep(4)  # Wait for 4 seconds before the next request
    
    conn.close()

if __name__ == "__main__":
    main()
