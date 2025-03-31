import json
import mysql.connector
from datetime import datetime

def create_tables(cursor):
    # Create videos table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        video_id VARCHAR(50) PRIMARY KEY,
        author VARCHAR(255),
        channel_id VARCHAR(50),
        channel_url VARCHAR(255),
        description TEXT,
        length INT,
        publish_date DATE,
        thumbnail_url VARCHAR(255),
        title VARCHAR(255),
        watch_url VARCHAR(255)
    )
    """)

    # Create shots table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shots (
        shot_id INT AUTO_INCREMENT PRIMARY KEY,
        video_id VARCHAR(50),
        shot_start INT,
        shot_end INT,
        shot_start_time FLOAT,
        shot_end_time FLOAT,
        FOREIGN KEY (video_id) REFERENCES videos(video_id)
    )
    """)

    # Create keyframes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS keyframes (
        keyframe_id INT AUTO_INCREMENT PRIMARY KEY,
        shot_id INT,
        keyframe_path VARCHAR(255),
        keyframe_idx INT,
        FOREIGN KEY (shot_id) REFERENCES shots(shot_id)
    )
    """)

def insert_data(cursor, data):
    # Insert video data
    for video_id, video_data in data.items():
        metadata = video_data['video_metadata']
        publish_date = datetime.strptime(metadata['publish_date'], '%d/%m/%Y').date()
        
        cursor.execute("""
        INSERT INTO videos (video_id, author, channel_id, channel_url, description, 
                          length, publish_date, thumbnail_url, title, watch_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            video_id,
            metadata['author'],
            metadata['channel_id'],
            metadata['channel_url'],
            metadata['description'],
            metadata['length'],
            publish_date,
            metadata['thumbnail_url'],
            metadata['title'],
            metadata['watch_url']
        ))

        # Insert shots data
        for shot_idx, shot_data in video_data['lst_shot'].items():
            cursor.execute("""
            INSERT INTO shots (video_id, shot_start, shot_end, shot_start_time, shot_end_time)
            VALUES (%s, %s, %s, %s, %s)
            """, (
                video_id,
                shot_data['shot_range'][0],
                shot_data['shot_range'][1],
                shot_data['shot_time'][0],
                shot_data['shot_time'][1]
            ))
            
            shot_id = cursor.lastrowid

            # Insert keyframes data
            for i in range(len(shot_data['lst_keyframe_paths'])):
                cursor.execute("""
                INSERT INTO keyframes (shot_id, keyframe_path, keyframe_idx)
                VALUES (%s, %s, %s)
                """, (
                    shot_id,
                    shot_data['lst_keyframe_paths'][i],
                    shot_data['lst_keyframe_idxs'][i]
                ))

def main():
    # Read JSON data
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Connect to MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database"
    )
    
    cursor = connection.cursor()
    
    try:
        # Create tables
        create_tables(cursor)
        
        # Insert data
        insert_data(cursor, data)
        
        # Commit changes
        connection.commit()
        print("Data successfully inserted into MySQL database")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main() 