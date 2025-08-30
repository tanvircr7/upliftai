from dotenv import load_dotenv
from .crew import build_crew

def main():
    load_dotenv()
    result = build_crew().kickoff()
    print(result)

if __name__ == "__main__":
    main()
