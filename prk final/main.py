from app.main import app


def run_message() -> None:
    print("Use 'python run.py api' to start the FastAPI server.")
    print("Use 'python run.py dashboard' to start the Streamlit dashboard.")


if __name__ == "__main__":
    run_message()
