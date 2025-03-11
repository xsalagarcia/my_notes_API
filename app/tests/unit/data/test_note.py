import unittest

from sqlalchemy.orm.exc import DetachedInstanceError

import app.tests.unit.data
from app.data import restart_db_and_tables, note as data, category as category_data, tag as tag_data
from app.exceptions.database import DatabaseError
from app.models.category import Category
from app.models.note import Note
from app.models.tag import Tag


class TestCategory(unittest.TestCase):

    def setUp(self):
        restart_db_and_tables()
        self.cat1 = category_data.create_category(Category(name="Category 1"))
        self.cat2 = category_data.create_category(Category(name="Category 2"))
        #self.tags_cat1 = [tag_data.create_tag(Tag(name=f"tag {i}", category_id=self.cat1.id)) for i in range(5)]
        #self.tags_cat2 = [tag_data.create_tag(Tag(name=f"tag {i}", category_id=self.cat2.id)) for i in range(5)]

    def test_create_and_get_note(self):
        note1 = data.create_note(note=Note(name="note 1", abstract="my first note",
                                           is_public=True, category_id=self.cat1.id),
                                 tag_names=["tag 1 cat 1"])
        note2 = data.create_note(note=Note(name="note 2", abstract="my first note",
                                           is_public=True, category_id=self.cat1.id),
                                 tag_names=["tag 1 cat 1"])
        note3 = data.create_note(note=Note(name="note 3", abstract="my first note",
                                           is_public=True, category_id=self.cat1.id),
                                 tag_names=["tag 1 cat 1", "tag 2 cat 1"])
        note4 = data.create_note(note=Note(name="note 4", abstract="my first note",
                                           is_public=False, category_id=self.cat1.id),
                                 tag_names=["tag 2 cat 1"])
        note5 = data.create_note(note=Note(name="note 5", abstract="my first note",
                                           is_public=True, category_id=self.cat2.id),
                                 tag_names=["tag 1 cat 2"])

        notes = data.get_notes_by_cat(category_id=self.cat1.id, only_public=False)
        self.assertEqual(notes[0], note1)
        self.assertEqual(notes[0].tags[0], Tag(id=1, name="tag 1 cat 1", category_id=self.cat1.id))
        self.assertEqual(len(notes[0].tags), 1)
        self.assertEqual(notes[1], note2)
        self.assertEqual(notes[1].tags[0], Tag(id=1, name="tag 1 cat 1", category_id=self.cat1.id))
        self.assertEqual(notes[2], note3)
        self.assertEqual(notes[2].tags,
                         [Tag(id=1, name="tag 1 cat 1", category_id=self.cat1.id), Tag(id=2, name="tag 2 cat 1", category_id=self.cat1.id)])
        self.assertEqual(notes[3], note4)
        self.assertEqual(notes[3].tags,
                         [Tag(id=2, name="tag 2 cat 1", category_id=self.cat1.id)])
        self.assertEqual(len(notes), 4)
        notes = data.get_notes_by_cat(category_id=self.cat1.id)
        self.assertEqual(len(notes), 3)
        notes = data.get_notes_by_cat(category_id=self.cat2.id)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0], note5)
        self.assertEqual(notes[0].tags, [Tag(id=3, name="tag 1 cat 2", category_id=self.cat2.id)])
        notes = data.get_notes_by_cat(category_id=self.cat2.id, with_tags=False)
        with self.assertRaises(DetachedInstanceError) as e:
            print(notes[0].tags)

    def test_update_note_link_unlink(self):
        preexistent_tag = tag_data.create_tag(Tag(name="preexisting tag", category_id=self.cat1.id))
        note1 = data.create_note(note=Note(name="note 1", abstract="my first note",
                                           is_public=True, category_id=self.cat1.id),
                                 tag_names=["tag 1 cat 1"])

        old_name = data.update_note(Note(**note1.model_dump(exclude={"name"}), name="modified note 1"))
        self.assertEqual(note1.name, old_name)
        modified_note = data.get_notes_by_cat(category_id=self.cat1.id)[0]
        self.assertEqual(modified_note.name, "modified note 1")
        self.assertEqual(modified_note.tags[0].name, "tag 1 cat 1")

        data.unlink_tag_from_note(note_id=modified_note.id, tag_id=modified_note.tags[0].id)
        modified_note = data.get_notes_by_cat(category_id=self.cat1.id)[0]
        self.assertEqual(0, len(modified_note.tags))
        self.assertEqual(2, len(tag_data.get_tags_by_cat(self.cat1.id)))  # Tag is not removed

        data.link_tag_from_note(note_id=note1.id, tag_id=preexistent_tag.id)
        modified_note = data.get_notes_by_cat(category_id=self.cat1.id)[0]
        self.assertEqual(modified_note.tags[0].name, "preexisting tag")
        with self.assertRaises(DatabaseError) as e:
            data.link_tag_from_note(note_id=note1.id, tag_id=preexistent_tag.id)
        self.assertEqual(e.exception.suggested_http_code, 409)

        data.delete_note(note_id=modified_note.id)
        self.assertEqual(0, len(data.get_notes_by_cat(category_id=self.cat1.id)))
        self.assertEqual(2, len(tag_data.get_tags_by_cat(self.cat1.id)))  # Tag is not removed















        #note2 = data.create_note(note=Note(name="Another note", abstract="my first note",
        #                                   is_public=False, category_id=self.cat1.id),
        #                         tags=[Tag(**tag.model_dump()) for tag in [self.tags_cat1[2]]])
        #note3 = data.create_note(note=Note(name="note for cat 2", abstract="my first note",
        #                                   is_public=True, category_id=self.cat2.id),
        #                         tags=[Tag(**tag.model_dump()) for tag in self.tags_cat2[0:2]])
        ## This should raise an error because note category is not the same that tags categories.
        #with self.assertRaises(DatabaseError) as e:
        #    data.create_note(note=Note(name="note 4", abstract="my first note",
        #                               is_public=True, category_id=self.cat2.id),
        #                     tags=[Tag(**tag.model_dump()) for tag in self.tags_cat1[0:2]])
#
#notes = data.get_notes_by_cat(category_id=self.cat1.id)
#print(notes[0].tags)
