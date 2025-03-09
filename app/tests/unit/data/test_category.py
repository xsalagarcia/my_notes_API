import unittest
import app.tests.unit.data
from app.data import restart_db_and_tables, category as data
from app.exceptions.database import DatabaseError
from app.models.category import Category


class TestCategory(unittest.TestCase):

    def setUp(self):
        restart_db_and_tables()

    def test_create_get_update_delete_category(self):
        created_cats = [data.create_category(category=Category(name=f"Category {i}")) for i in range(5)]
        for i, category in enumerate(created_cats):
            self.assertEqual(f"Category {i}", category.name)
            self.assertEqual(i+1, category.id)
        self.assertEqual(5, len(created_cats))

        data.update_category(Category(id=1, name="Modified category"))
        recovered_cats = data.get_categories()
        self.assertEqual(recovered_cats[-1].name, "Modified category")  # The last, ordered by name.
        for created_cat, recovered_cat in zip(created_cats[1:], recovered_cats[:-1]):  # The others are equal
            self.assertEqual(created_cat, recovered_cat)

        with self.assertRaises(DatabaseError) as e:
            data.update_category(Category(id=400, name="Non existing cat"))
        self.assertEqual(e.exception.suggested_http_code, 404)

        with self.assertRaises(DatabaseError) as e:
            data.update_category(Category(id=2, name="Category 3"))
        self.assertEqual(e.exception.suggested_http_code, 409)


        data.delete_category(1)
        recovered_cats = data.get_categories()
        self.assertEqual(len(recovered_cats), 4)
        for created_cat, recovered_cat in zip(created_cats[1:], recovered_cats):  # The others are equal
            self.assertEqual(created_cat, recovered_cat)

        # Same name is not possible
        with self.assertRaises(DatabaseError) as e:
            data.create_category(category=Category(name="Category 2"))
        self.assertEqual(e.exception.suggested_http_code, 409)
