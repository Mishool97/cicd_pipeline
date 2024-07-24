import random
import time
import uuid
import json
from datetime import datetime, timedelta
import pandas as pd
import s3fs

start_time = time.time()

# Sample pages and referrers
pages = [
    "/home", "/about", "/products", "/products/item1", "/products/item2", "/contact", "/login", "/signup"
]

referrers = [
    "https://www.google.com", "https://www.facebook.com", "https://www.twitter.com",
    "https://www.linkedin.com", "https://www.reddit.com", "https://www.instagram.com",
    "https://www.example.com"
]

# Event types and details
event_types = {
    "page_view": lambda: {"scroll_depth": random.randint(0, 100)},
    "click": lambda: {"element_id": "button_" + str(random.randint(1, 10))},
    "form_submit": lambda: {"form_id": "form_" + str(random.randint(1, 5))}
}

# Generate random timestamps within a specified range
def generate_random_timestamp(start_date, end_date):
    if start_date > end_date:
        raise ValueError("start_date must be before end_date")
    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

# Generate a random event
def generate_random_event(user_id, session_id, session_start):
    
    timestamp = generate_random_timestamp(session_start, session_start + timedelta(minutes=random.randint(1, 30)))
    page_url = random.choice(pages)
    referrer_url = random.choice(referrers)
    event_type = random.choice(list(event_types.keys()))
    event_details = event_types[event_type]()
    
    return {
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "session_id": session_id,
        "page_url": page_url,
        "referrer_url": referrer_url,
        "event_type": event_type,
        "event_details": event_details
    }

# Simulate clickstream data
def simulate_clickstream_data(num_users, num_sessions_per_user, num_events_per_session):
    data = []
    start_date = datetime.now() - timedelta(days=30)  # Start generating data from 30 days ago
    end_date = datetime.now()
    
    for user_id in range(1, num_users + 1):
        for _ in range(num_sessions_per_user):
            session_id = str(uuid.uuid4())
            session_start = generate_random_timestamp(start_date, end_date)
            for _ in range(num_events_per_session):
                event = generate_random_event(user_id, session_id, session_start)
                data.append(event)
    return data

def main():
    # Parameters for simulation
    num_users = 1000  # Number of unique users
    num_sessions_per_user = 12  # Number of sessions per user
    num_events_per_session = 20  # Number of events per session

    # Generate clickstream data
    clickstream_data = simulate_clickstream_data(num_users, num_sessions_per_user, num_events_per_session)

    df = pd.DataFrame(clickstream_data)
    print(df.head())
    print('rows :', len(df))

    end_time = time.time()

    duration = round(end_time - start_time, 1)
    print(f"Duration: {duration} seconds")

    now = datetime.now()

    # Format the date and time for folder structure
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    hour = now.strftime("%H")
    minute = now.strftime("%M")

    # Define the folder structure

    file_path = f'{year}/{month}/{day}/{hour}/{minute}/clickstream_data.parquet'

    # S3 bucket and file path
    bucket_name = 'databricks-learning-clickstream'

    # Construct the S3 path
    s3_path = f's3://{bucket_name}/{file_path}'

    try :
        # Write DataFrame to Parquet file in S3
        df.to_parquet(s3_path, engine='pyarrow', compression='snappy')
        print(f"Data written to {s3_path}")

    except Exception as e:
        print(f"Error writing to S3: {e}")

if __name__ == "__main__":
    main()