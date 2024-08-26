import os
from dotenv import load_dotenv

load_dotenv()

databsse_url="mysql://sane:sanemysql!2244@63.34.199.220/michu_dashBoard"
# SECRET_KEY="asdfghhtgbhhhyuiokmnbvcx"

# databsse_url="mysql://mysqlsane!4422@localhost/michu_dashBoard"
URL_DATABASE="mysql+pymysql://root:SH36essti@localhost:3306/michudashboard"

class Settings:
    DATABASE_URL: str = URL_DATABASE
settings = Settings()