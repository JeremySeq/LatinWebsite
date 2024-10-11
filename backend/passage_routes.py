from flask import Blueprint, jsonify, request
import login
import db

passage_routes = Blueprint('passage_routes', __name__)

@passage_routes.route("/")
def get_all_passages():
    passages = db.Passage.query.all()
    result = []
    for passage in passages:
        result.append(passage.to_json())
    return jsonify(result), 200

@passage_routes.route("/", methods=["POST"])
@login.requires_login
def create_passage():

    user = login.getUserFromRequest(request)

    title = request.form.get("title")
    latin_text = request.form.get("latin")

    exists = db.Passage.query.filter_by(title=title).first() is not None

    if exists:
        print("Already exists")
        return 'Already exists', 200

    passage = db.Passage(title=title, latin_text=latin_text, submitted_by_user_id=user.id)
    print(f"{user.username} created passage {title}")
    db.db.session.add(passage)
    db.db.session.commit()
    return f"Created {passage.title}", 201

@passage_routes.route("/<passage>/delete", methods=["POST"])
def delete_passage(passage):
    passage = db.Passage.query.filter_by(title=passage).first()
    if passage is None:
        print("Does not exist")
        return 'Does not exist', 404

    db.db.session.delete(passage)
    db.db.session.commit()
    return f"Deleted {passage.title}", 200

@passage_routes.route("/<passage>")
def get_passage(passage):
    passage = db.Passage.query.filter_by(title=passage).first()
    if passage is None:
        return "Passage not found", 404

    return passage.to_json(), 200

@passage_routes.route("/<passage>/translations/<author>")
def get_passage_translation(passage, author):
    passage = db.Passage.query.filter_by(title=passage).first()

    if passage is None:
        return "Passage not found", 404

    translation = db.Translation.query.filter_by(passage_id=passage.id).first()
    
    if translation is None:
        return "No translation for this passage", 404
    
    return translation.to_json(), 200

@passage_routes.route("/<passage>/translations")
def get_all_passage_translations(passage):
    passage = db.Passage.query.filter_by(title=passage).first()

    if passage is None:
        return "Passage not found", 404

    translations = db.Translation.query.filter_by(passage_id=passage.id).all()
    
    if len(translations) == 0:
        return "No translations for this passage", 404
    
    return [translation.to_json() for translation in translations], 200

@passage_routes.route("/<passage>/create_translation", methods=["POST"])
@login.requires_login
def create_translation(passage):
    user = login.getUserFromRequest(request)
    
    passage = db.Passage.query.filter_by(title=passage).first()
    if passage is None:
        return 'Passage not found', 404
    
    translation_type = request.json["translation_type"]
    english_text = request.json["english_text"]

    if translation_type != "piece_by_piece" and translation_type != "full_translation":
        return 'Invalid translation type', 400
    
    if translation_type == "full_translation":
        translation = db.Translation(passage_id=passage.id, english_text=english_text, 
                                     submitted_by_user_id=user.id, is_approved_official=True, 
                                     translation_type=translation_type)
        db.db.session.add(translation)
        db.db.session.commit()
    else:
        
        translation = db.Translation(passage_id=passage.id, english_text=english_text, 
                                     submitted_by_user_id=user.id, is_approved_official=True, 
                                     translation_type=translation_type)
        
        db.db.session.add(translation)
        db.db.session.commit()

        parts = request.json["parts"]
        for part in parts:
            translation_part = db.TranslationPart(translation_id=translation.id, latin_section=part["latin"], english_section=part["english"])
            db.db.session.add(translation_part)

        
        db.db.session.commit()
        
    return '', 200

@passage_routes.route("/<passage>/delete_translation", methods=["POST"])
def delete_translation(passage):
    passage = db.Passage.query.filter_by(title=passage).first()
    if passage is None:
        return 'Passage not found', 404
    
    translation = db.Translation.query.filter_by(passage_id=passage.id).first()
    
    if translation is None:
        return "No translations for this passage", 404
    
    db.db.session.delete(translation)
    db.db.session.commit()