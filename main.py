import threading
from app import app
import offers

# Function to run the Flask application
def run_flask_app():
    print("Starting Flask app")  # Debug statement
    app.run(debug=True, use_reloader=False)  # Disable the reloader

# Function to run the find_last_holiday task
def run_offers_task():
    print("Starting offers task")  # Debug statement
    offers.find_last_holiday()

# Main function to run the Flask app and the offers task concurrently
def main():
    print("Creating threads")  # Debug statement
    # Create a thread for running the Flask app
    flask_thread = threading.Thread(target=run_flask_app)
    # Create a thread for running the offers task
    offers_thread = threading.Thread(target=run_offers_task)
    # Start both threads
    flask_thread.start()
    offers_thread.start()
    # Wait for both threads to complete
    flask_thread.join()
    offers_thread.join()

# Entry point of the script
if __name__ == '__main__':
    print("Running main function")  # Debug statement
    main()