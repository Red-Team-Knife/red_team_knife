from controllers.feroxbuster import *
import utils.hyperlink_constants as hyperlink_constants
from flask import *
from current_scan import CurrentScan


feroxbuster_blueprint = Blueprint('feroxbuster', __name__)
sections = hyperlink_constants.SECTIONS
feroxbuster_controller = FeroxbusterController()


@feroxbuster_blueprint.route("/")
def inteface():
    out = feroxbuster_controller.run('kali.org', {TIME_LIMIT: '10s'})
    return render_template("test.html", out=out)