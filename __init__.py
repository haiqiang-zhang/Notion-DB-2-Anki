from cProfile import label

from aqt import mw
from aqt.qt import *
from aqt import gui_hooks
from aqt.operations import QueryOp
from .notion_connector import notion_db_query, export_notion_page_to_html, notion_update_sync_status
from .utils import create_front_cardID_map, create_or_modify_note_model
from datetime import datetime
from .view import start_sync_popup, close_sync_popup


def start_sync(col) -> None:
    model = create_or_modify_note_model("Basic (notion_sync)")
    deck_name = mw.addonManager.getConfig(__name__)["Synced Deck"]
    notion_api_key = mw.addonManager.getConfig(__name__)["Notion API Key"]
    notion_sync_status_field_name = mw.addonManager.getConfig(__name__)["Notion Sync Status Field Name"]
    # 获取当前的 collection 对象
    # col = mw.col

    # 获取这个 deck 的 ID
    deck_id = col.decks.id(deck_name)

    # 查询属于该 deck 的所有卡片的 ID
    card_ids = col.db.list(f"SELECT id FROM cards WHERE did = ?", deck_id)
    front_cardID_map = create_front_cardID_map(card_ids)
    notion_list = notion_db_query(5)

    # delete anki cards not in notion
    for front in front_cardID_map:
        if front not in [notion["front"] for notion in notion_list]:
            print("Deleting note: Front: ", front, "Card ID: ", front_cardID_map[front])
            card_id = front_cardID_map[front]
            col.remove_notes_by_card([card_id])


    for notion in notion_list:
        front = notion["front"]
        # created_time = notion["created_time"]
        last_edited_time = notion["last_edited_time"]

        # if the front is existed in Anki "Front" field and last_edited_time is newer than the anki db record, then update the "Back" field
        # else, add a new card
        if front in front_cardID_map:
            card_id = front_cardID_map[front]
            card = col.get_card(card_id)
            note = card.note()
            if datetime.fromisoformat(note["Last Edited Time"]) < last_edited_time:
                note["Back"] = export_notion_page_to_html(notion["back_id"], notion_api_key)

                response = notion_update_sync_status(notion_sync_status_field_name, notion["back_id"])
                note["Last Edited Time"] = datetime.strptime(response["last_edited_time"], '%Y-%m-%dT%H:%M:%S.%fZ').isoformat()
                print("Updating note: Front: ", note["Front"], "Back: ", note["Back"], "Last Edited Time: ",
                      note["Last Edited Time"])
                col.update_note(note)
        else:
            note = col.new_note(model)
            note["Front"] = front
            note["Back"] = export_notion_page_to_html(notion["back_id"], notion_api_key)

            response = notion_update_sync_status(notion_sync_status_field_name, notion["back_id"])
            note["Last Edited Time"] = datetime.strptime(response["last_edited_time"], '%Y-%m-%dT%H:%M:%S.%fZ').isoformat()
            print("Adding new note: Front: ", note["Front"], "Back: ", note["Back"], "Last Edited Time: ",
                  note["Last Edited Time"])
            col.add_note(note, deck_id)

    close_sync_popup()



def start_sync_ui() -> None:
    op = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda col: start_sync(col),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=lambda col: print("Synced with Notion"),
    )

    op.with_progress(label="Syncing with Notion").run_in_background()



gui_hooks.sync_will_start.append(start_sync_ui)