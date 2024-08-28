import streamlit as st
import sqlite3

# Function to get vote counts for a specific position
def get_vote_counts(position):
    conn = sqlite3.connect('voting.db')
    c = conn.cursor()
    c.execute("SELECT candidate_name, vote_count FROM votes WHERE position=?", (position,))
    results = c.fetchall()
    conn.close()
    return results

# Streamlit UI for displaying results
st.title("Election Results")

for position in ["President", "Vice President", "Secretary", "Joint Secretary"]:
    st.subheader(f"Results for {position}")
    vote_counts = get_vote_counts(position)
    for candidate_name, vote_count in vote_counts:
        st.write(f"{candidate_name}: {vote_count} votes")
