"""Contains routes for getting Latin vocabulary."""
from flask import Blueprint, request, jsonify
import vocab_analysis

vocab_routes = Blueprint('vocab', __name__)

@vocab_routes.route('/')
def vocab_lookup():
    """Looks up vocabulary in a Latin text.
    Request Params:
        text: Latin text to look up vocabulary for.
        ignore_easy_vocab: If True, will not show vocabulary for easy words.
    """
    text = request.args.get("text")

    ignore_easy_vocab = None
    if request.args.get('ignore_easy_vocab') == "true":
        ignore_easy_vocab = True

    return jsonify({"data": vocab_analysis.lookup_text(text, ignore_easy_vocab=ignore_easy_vocab)}), 200
