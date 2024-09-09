from aqt import mw


def convert_text_obj_to_plain_text(title_obj):
    plain_text = ""
    for text in title_obj:
        plain_text += text["plain_text"]
    return plain_text


def create_front_cardID_map(cardID_list):
    front_cardID_map = {}
    for cardID in cardID_list:
        front = mw.col.get_card(cardID).note()["Front"]

        front_cardID_map[front.strip()] = cardID
    return front_cardID_map


def create_or_modify_note_model(model_name):
    """
    Create a new note model or modify an existing one by adding the 'Last Edited Time' field.

    :param model_name: The name of the note model to create or modify.
    """
    col = mw.col
    mm = col.models  # Model manager to handle note models

    # Check if the model already exists
    model = mm.by_name(model_name)

    if not model:
        # If the model doesn't exist, create a new one
        model = mm.new(model_name)

        # Add basic fields like 'Front' and 'Back'
        mm.addField(model, mm.newField("Front"))
        mm.addField(model, mm.newField("Back"))
        mm.addField(model, mm.newField("Last Edited Time"))
        print(f"Created new model: {model_name}")

    # Check if the 'Last Edited Time' field already exists
    if "Last Edited Time" not in [field['name'] for field in model['flds']]:
        # Create and add the 'Last Edited Time' field
        last_edited_field = mm.newField("Last Edited Time")
        mm.addField(model, last_edited_field)
        print("Added 'Last Edited Time' field to the model.")



    if not model['tmpls']:
        model['tmpls'].append(
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}'
            }
        )
    else:
        # Update the card template with the desired question and answer formats
        templates = model['tmpls'][0]
        templates['qfmt'] = '{{Front}}'  # Set the question format (Front side)
        templates[
            'afmt'] = '{{FrontSide}}<hr id="answer">{{Back}}'  # Set the answer format to include 'Last Edited Time'

    # Save the updated template and model
    mm.save(model)

    return model