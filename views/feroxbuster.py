from controllers.feroxbuster import *
import utils.hyperlink_constants as hyperlink_constants
from utils.dictionary import remove_empty_values
from flask import *
from current_scan import CurrentScan
import json, html


feroxbuster_blueprint = Blueprint("feroxbuster", __name__)
sections = hyperlink_constants.SECTIONS
feroxbuster_controller = FeroxbusterController()


@feroxbuster_blueprint.route("/", methods=["GET", "POST"])
def interface():
    if request.method == "POST":

        options = request.form.to_dict()

        target = options["target"]

        options.pop("target")

        return render_template(
            "feroxbuster/feroxbuster_results.html",
            sections=sections,
            target=target,
            options=json.dumps(options),
        )

    if CurrentScan.scan is not None:
        return render_template(
            "feroxbuster/feroxbuster_interface.html",
            sections=sections,
            target=CurrentScan.scan.host,
            BURP=BURP,
            BURP_REPLAY=BURP_REPLAY,
            SMART=SMART,
            THOROUGH=THOROUGH,
            PROXY=PROXY,
            REPLAY_PROXY=REPLAY_PROXY,
            REPLAY_CODE=REPLAY_CODE,
            USER_AGENT=USER_AGENT,
            RANDOM_USER_AGENT=RANDOM_USER_AGENT,
            EXTENSIONS=EXTENSIONS,
            METHODS=METHODS,
            DATA=DATA,
            HEADERS=HEADERS,
            COOKIES=COOKIES,
            QUERIES=QUERIES,
            SLASH=SLASH,
            DONT_SCAN_URLS=DONT_SCAN_URLS,
            FILTER_MAX_DIMENSIONS=FILTER_MAX_DIMENSIONS,
            FILTER_REGEXES=FILTER_REGEXES,
            FILTER_WORD_NUMBERS=FILTER_WORD_NUMBERS,
            FILTER_LINE_NUMBERS=FILTER_LINE_NUMBERS,
            FILTER_STATUS_CODES=FILTER_STATUS_CODES,
            ALLOW_STATUS_CODES=ALLOW_STATUS_CODES,
            REQUEST_TIMEOUT=REQUEST_TIMEOUT,
            AUTOMATIC_REDIRECT=AUTOMATIC_REDIRECT,
            INESCURE_DISABLE_TLS_CERTIFICATES=INESCURE_DISABLE_TLS_CERTIFICATES,
            SERVER_CERTIFICATES=SERVER_CERTIFICATES,
            CLIENT_CERTIFICATE=CLIENT_CERTIFICATE,
            CLIENT_KEY=CLIENT_KEY,
            THREADS=THREADS,
            DISABLE_RECURSION=DISABLE_RECURSION,
            RECURSION_DEPTH=RECURSION_DEPTH,
            FORCE_RECURSION=FORCE_RECURSION,
            DONT_EXTRACT_LINKS=DONT_EXTRACT_LINKS,
            CONCURRENT_SCAN_LIMIT=CONCURRENT_SCAN_LIMIT,
            RATE_LIMIT=RATE_LIMIT,
            WORDLIST_PATH=WORDLIST_PATH,
            AUTO_TUNE=AUTO_TUNE,
            AUTO_BAIL=AUTO_BAIL,
            DISABLE_WILDCARD_FILTERING=DISABLE_WILDCARD_FILTERING,
            REMEMBER_EXTENSION=REMEMBER_EXTENSION,
            ASK_FOR_ALTERNATIVE_EXTENSIONS=ASK_FOR_ALTERNATIVE_EXTENSIONS,
            ADD_CRITICAL_WORDS=ADD_CRITICAL_WORDS,
            IGNORE_EXTENSIONS=IGNORE_EXTENSIONS,
            TIME_LIMIT=TIME_LIMIT,
        )

    return render_template(
        "feroxbuster/feroxbuster_interface.html",
        sections=sections,
        BURP=BURP,
        BURP_REPLAY=BURP_REPLAY,
        SMART=SMART,
        THOROUGH=THOROUGH,
        PROXY=PROXY,
        REPLAY_PROXY=REPLAY_PROXY,
        REPLAY_CODE=REPLAY_CODE,
        USER_AGENT=USER_AGENT,
        RANDOM_USER_AGENT=RANDOM_USER_AGENT,
        EXTENSIONS=EXTENSIONS,
        METHODS=METHODS,
        DATA=DATA,
        HEADERS=HEADERS,
        COOKIES=COOKIES,
        QUERIES=QUERIES,
        SLASH=SLASH,
        DONT_SCAN_URLS=DONT_SCAN_URLS,
        FILTER_MAX_DIMENSIONS=FILTER_MAX_DIMENSIONS,
        FILTER_REGEXES=FILTER_REGEXES,
        FILTER_WORD_NUMBERS=FILTER_WORD_NUMBERS,
        FILTER_LINE_NUMBERS=FILTER_LINE_NUMBERS,
        FILTER_STATUS_CODES=FILTER_STATUS_CODES,
        ALLOW_STATUS_CODES=ALLOW_STATUS_CODES,
        REQUEST_TIMEOUT=REQUEST_TIMEOUT,
        AUTOMATIC_REDIRECT=AUTOMATIC_REDIRECT,
        INESCURE_DISABLE_TLS_CERTIFICATES=INESCURE_DISABLE_TLS_CERTIFICATES,
        SERVER_CERTIFICATES=SERVER_CERTIFICATES,
        CLIENT_CERTIFICATE=CLIENT_CERTIFICATE,
        CLIENT_KEY=CLIENT_KEY,
        THREADS=THREADS,
        DISABLE_RECURSION=DISABLE_RECURSION,
        RECURSION_DEPTH=RECURSION_DEPTH,
        FORCE_RECURSION=FORCE_RECURSION,
        DONT_EXTRACT_LINKS=DONT_EXTRACT_LINKS,
        CONCURRENT_SCAN_LIMIT=CONCURRENT_SCAN_LIMIT,
        RATE_LIMIT=RATE_LIMIT,
        WORDLIST_PATH=WORDLIST_PATH,
        AUTO_TUNE=AUTO_TUNE,
        AUTO_BAIL=AUTO_BAIL,
        DISABLE_WILDCARD_FILTERING=DISABLE_WILDCARD_FILTERING,
        REMEMBER_EXTENSION=REMEMBER_EXTENSION,
        ASK_FOR_ALTERNATIVE_EXTENSIONS=ASK_FOR_ALTERNATIVE_EXTENSIONS,
        ADD_CRITICAL_WORDS=ADD_CRITICAL_WORDS,
        IGNORE_EXTENSIONS=IGNORE_EXTENSIONS,
        TIME_LIMIT=TIME_LIMIT,
    )


@feroxbuster_blueprint.route("/results", methods=["POST"])
def results():

    target = request.json["target"]

    form = html.unescape(request.json["options"])

    options = remove_empty_values(json.loads(form))
    print(options)
    html_scan_result = feroxbuster_controller.run(target, options)
    return jsonify(html_scan_result)


@feroxbuster_blueprint.route("/save_results", methods=["POST"])
def save_results():
    if CurrentScan.scan is not None:
        CurrentScan.scan.save_scan("feroxbuster", feroxbuster_controller.last_scan_result)
        return "<p>Results successfully saved.</p>"
    return "<p>No scan started.</p>"
