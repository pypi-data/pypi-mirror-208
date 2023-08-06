from flask import jsonify, request, Flask
from CirclesVacanciesScrapers.monster_com_scraper import MonsterComScraper
from CirclesVacanciesScrapers.indeed_com_scraper import IndeedComScraper
from dotenv import load_dotenv
from CirclesLocalLoggerPython.LoggerServiceSingleton import locallgr
load_dotenv()
app = Flask(__name__)
locallgr.log("starting my rest_api")


@app.route("/api", methods=["POST", "GET"])
def api():
    output = request.get_json()
    position = str(output.get("position", ""))
    location = str(output.get("location", ""))
    n = int(output.get("num of jobs", 0))
    source = str(output.get("source", ""))

    if not location or not position or not n or not source:
        return jsonify({'Error': 'Invalid parameters'})

    if source == "monster":
        scraper = MonsterComScraper(position=position, location=location)
    elif source == "indeed":
        scraper = IndeedComScraper(position=position, location=location)
    else:
        return jsonify({'Error': 'Invalid source'})

    scraper.page_scraping(n)
    return jsonify({'Message': 'Done Scraping!'})


if __name__ == '__main__':
    app.run(debug=True, port=3000)
