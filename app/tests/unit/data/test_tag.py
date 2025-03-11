import unittest
import app.tests.unit.data  # sets IN_MEMORY_DB environment variable.
from app.data import restart_db_and_tables, tag as data, category as category_data
from app.models.category import Category
from app.models.tag import Tag


class TestTag(unittest.TestCase):
    def setUp(self):
        restart_db_and_tables()
        self.cat1 = category_data.create_category(Category(name="Category 1"))
        self.cat2 = category_data.create_category(Category(name="Category 2"))

    def test_create_get_update_delete_tag(self):
        created_tags_for_cat1 = [data.create_tag(Tag(name=f"tag {i}", category_id=self.cat1.id)) for i in range(5)]
        created_tags_for_cat2 = [data.create_tag(Tag(name=f"tag {i}", category_id=self.cat2.id)) for i in range(5)]
        self.assertEqual(len(created_tags_for_cat2), 5)
        self.assertEqual(len(created_tags_for_cat1), 5)

        recovered_tags_for_cat_1 = data.get_tags_by_cat(self.cat1.id)
        self.assertEqual(recovered_tags_for_cat_1, created_tags_for_cat1)
        recovered_tags_for_cat_2 = data.get_tags_by_cat(self.cat2.id)
        self.assertEqual(recovered_tags_for_cat_2, created_tags_for_cat2)
        self.assertNotEqual(recovered_tags_for_cat_1, created_tags_for_cat2)

        tag_to_modify = created_tags_for_cat1[0]
        tag_to_modify.name = "zModified tag"
        data.update_tag(tag_to_modify)
        recovered_tags_for_cat_1 = data.get_tags_by_cat(self.cat1.id)
        self.assertEqual(recovered_tags_for_cat_1[:-1], created_tags_for_cat1[1:])
        self.assertEqual(recovered_tags_for_cat_1[len(recovered_tags_for_cat_1) - 1].name, "zModified tag")

        data.delete_tag(tag_to_modify.id)
        recovered_tags_for_cat_1 = data.get_tags_by_cat(self.cat1.id)
        self.assertEqual(recovered_tags_for_cat_1, created_tags_for_cat1[1:])

        # Testing cascade for tag.category_id foreign key
        category_data.delete_category(id=self.cat1.id)
        recovered_tags_for_cat_1 = data.get_tags_by_cat(self.cat1.id)
        self.assertEqual(len(recovered_tags_for_cat_1), 0)
