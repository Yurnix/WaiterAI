from dotenv import load_dotenv
from db_queries import getCategories
load_dotenv()


def main():
    categories=getCategories()
    print(categories)

if __name__ == "__main__":
    main()