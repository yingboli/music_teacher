from googleapiclient.discovery import build
import streamlit as st
import isodate

def get_channel_id(handle):
    """Get a Youtube channel's id from its handle 
    
    Parameters
    ----------
    handle: str
        Starts with @

    Returns
    -------
    Channel id: str

    Examples
    --------
    get_channel_id("@langlang")
    # returns UCkEZRZfqwPfv8JqQ3u1n2Ug
    """
    youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_DATA_API_KEY"])

    # Handles start with @, but the API search works best with just the name
    query = handle if handle.startswith('@') else f"@{handle}"
    
    request = youtube.search().list(
        q=query,
        type="channel",
        part="id",
        maxResults=1
    )
    response = request.execute()
    
    if response['items']:
        return response['items'][0]['id']['channelId']
    return "Not Found"


def get_all_video_ids(channel_id):
    """Get all video ids from a channel"""
    youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_DATA_API_KEY"])

    # Convert Channel ID (UC...) to Uploads Playlist ID (UU...)
    uploads_playlist_id = "UU" + channel_id[2:]
    
    video_ids = []
    next_page_token = None
    
    while True:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])
            
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
            
    return video_ids

def get_short_videos(channel_id, max_minutes=5):
    """Get video ids from a channel less than a certain duration


    Parameters
    ----------
    channel_id: str
    max_minutes: float

    Returns
    -------
    A list of dict, each has keys "id", "title", "duration"
    
    Examples
    --------
    channel_id = "UCkEZRZfqwPfv8JqQ3u1n2Ug" # Lang Lang's Channel
    videos = get_short_videos(channel_id, max_minutes=5)
    
    for v in videos:
        print(f"[{v['duration']}] {v['title']} - https://youtu.be/{v['id']}")
    """
    youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_DATA_API_KEY"])

    # 1. Get the "Uploads" playlist ID for the channel
    ch_request = youtube.channels().list(part="contentDetails", id=channel_id)
    ch_response = ch_request.execute()
    uploads_id = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    short_video_ids = []
    next_page_token = None
    max_seconds = max_minutes * 60

    while True:
        # 2. Get a batch of video IDs from the uploads playlist
        pl_request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page_token
        )
        pl_response = pl_request.execute()
        
        # Extract IDs for this batch
        batch_ids = [item['contentDetails']['videoId'] for item in pl_response['items']]
        
        # 3. Get the DURATIONS for this batch of IDs
        v_request = youtube.videos().list(
            part="contentDetails,snippet",
            id=",".join(batch_ids)
        )
        v_response = v_request.execute()
        
        for v_item in v_response['items']:
            duration_str = v_item['contentDetails']['duration']
            # Convert ISO 8601 (PT#M#S) to total seconds
            duration_seconds = isodate.parse_duration(duration_str).total_seconds()
            
            if duration_seconds < max_seconds:
                short_video_ids.append({
                    "id": v_item['id'],
                    "title": v_item['snippet']['title'],
                    "duration": duration_str
                })

        next_page_token = pl_response.get('nextPageToken')
        if not next_page_token:
            break
            
    return short_video_ids


def list_all_playlists(channel_id):
    """Get all playlists from channel

    Examples
    --------
    playlists = list_all_playlists("UCkEZRZfqwPfv8JqQ3u1n2Ug")
    for name, p_id in playlists.items():
        print(f"Playlist: {name} | ID: {p_id}")    
    """
    youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_DATA_API_KEY"])

    request = youtube.playlists().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50
    )
    response = request.execute()
    
    # Returns a dictionary of {Title: ID}
    return {item['snippet']['title']: item['id'] for item in response['items']}

def get_video_ids_from_playlist(playlist_id):
    """Get video ids from a playlist
    """
    youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_DATA_API_KEY"])

    video_ids = []
    next_page_token = None
    
    while True:
        request = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            # The video ID is located inside the contentDetails or snippet
            v_id = item['contentDetails']['videoId']
            video_ids.append(v_id)
            
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
            
    return video_ids

# The original Shorts URL
# shorts_url = "https://www.youtube.com/shorts/B7EZvAWDFPg"
# # Convert it to a standard watch URL
# video_url = shorts_url.replace("shorts/", "watch?v=")
# st.video(video_url)

