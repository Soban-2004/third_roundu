import streamlit as st
import sqlite3

# Function to get candidates based on the position, along with their image file names
def get_candidates(position):
    conn = sqlite3.connect('voting.db')
    c = conn.cursor()
    c.execute("SELECT name, image FROM candidates WHERE position=?", (position,))
    candidates = c.fetchall()  # Returns a list of tuples (name, image)
    conn.close()
    return candidates

# Function to check if a voter has already voted
def has_voted(registration_number):
    conn = sqlite3.connect('voting.db')
    c = conn.cursor()
    c.execute("SELECT has_voted FROM voters WHERE registration_number=?", (registration_number,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Function to mark a voter as having voted
def mark_as_voted(registration_number):
    conn = sqlite3.connect('voting.db')
    c = conn.cursor()
    c.execute("UPDATE voters SET has_voted=1 WHERE registration_number=?", (registration_number,))
    conn.commit()
    conn.close()

# Function to add a voter if not already in database
def add_voter(registration_number):
    conn = sqlite3.connect('voting.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO voters (registration_number) VALUES (?)", (registration_number,))
    conn.commit()
    conn.close()

# Function to increment vote count for a candidate
def increment_vote_count(position, candidate_name):
    conn = sqlite3.connect('voting.db')
    c = conn.cursor()
    c.execute('''INSERT INTO votes (position, candidate_name, vote_count)
                 VALUES (?, ?, 1)
                 ON CONFLICT(position, candidate_name)
                 DO UPDATE SET vote_count = vote_count + 1''',
              (position, candidate_name))
    conn.commit()
    conn.close()

# Streamlit UI
st.title("College Election Voting")

# Manage navigation state
if "page" not in st.session_state:
    st.session_state.page = "registration"

# Registration page
if st.session_state.page == "registration":
    registration_number = st.text_input("Enter your registration number:")

    if st.button("Submit"):
        if registration_number:
            st.session_state.registration_number = registration_number  # Store the registration number in session state
            add_voter(registration_number)
            if has_voted(registration_number):
                st.warning("You have already voted.")
                st.session_state.page = "completed"
            else:
                st.success("Welcome! Proceed to vote.")
                st.session_state.page = "voting"
        else:
            st.error("Please enter your registration number.")

# Voting page
if st.session_state.page == "voting":
    choices = {}

    for position in ["President", "Vice President", "Secretary", "Joint Secretary"]:
        st.header(f"Vote for {position}")
        candidates = get_candidates(position)

        # Create a dictionary to store candidate names with corresponding image file paths
        candidate_images = {}
        for candidate_name, candidate_image in candidates:
            candidate_images[candidate_name] = candidate_image

        # Create a radio button with the candidate names as options
        selected_candidate = st.radio(f"Select a candidate for {position}:", list(candidate_images.keys()), key=f"{position.lower().replace(' ', '_')}_choice")
        choices[position] = selected_candidate

        # Display the selected candidate's image below the radio button
        if selected_candidate:
            st.image(candidate_images[selected_candidate], caption=selected_candidate, width=150, use_column_width=False)

    if st.button("Submit Vote"):
        if all(choices.values()):  # Check if all positions have a selected candidate
            for position, candidate_name in choices.items():
                increment_vote_count(position, candidate_name)
                
            mark_as_voted(st.session_state.registration_number)  # Use the stored registration number
            st.success("Thank you for voting!")
            st.session_state.page = "completed"
        else:
            st.error("Please select a candidate for each position.")

# Completion page
if st.session_state.page == "completed":
    if has_voted(st.session_state.registration_number):
        st.warning("You have already voted.")
    else:
        st.info("Voting process completed. Thank you for participating!")