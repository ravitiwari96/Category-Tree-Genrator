# =======================unit test for generater_category.py========================

# import unittest
# from unittest.mock import patch, MagicMock
# import re

# import  generater_category  as gct

# class TestCategoryTreeGenerator(unittest.TestCase):

#     def test_extract_json_from_text_valid(self):
#         text = '''
#         {
#             "positive": ["dresses", "tops"],
#             "negative": ["men", "kids"]
#         }
#         '''
#         expected = {"positive": ["dresses", "tops"], "negative": ["men", "kids"]}
#         result = gct.extract_json_from_text(text)
#         self.assertEqual(result, expected)

#     def test_extract_json_from_text_invalid(self):
#         text = "No JSON here"
#         with self.assertRaises(ValueError):
#             gct.extract_json_from_text(text)

#     @patch("google.generativeai.GenerativeModel.generate_content")
#     def test_get_extracted_keywords(self, mock_generate):
#         mock_response = MagicMock()
#         mock_response.text = '''
#         {
#             "positive": ["jeans", "shirts"],
#             "negative": ["children", "men"]
#         }
#         '''
#         mock_generate.return_value = mock_response
#         model_patch = patch("google.generativeai.GenerativeModel")
#         with model_patch as mock_model_class:
#             mock_model_class.return_value.generate_content.return_value = mock_response
#             result = gct.get_extracted_keywords("Show jeans and shirts, avoid children and men")
#             self.assertEqual(result["positive"], ["jeans", "shirts"])
#             self.assertEqual(result["negative"], ["children", "men"])

#     def test_build_category_prompt_with_negatives(self):
#         positive = ["jeans", "shoes"]
#         negative = ["kids"]
#         prompt = gct.build_category_prompt(positive, negative)
#         self.assertIn("Positive keywords", prompt)
#         self.assertIn("Exclude anything related", prompt)

#     def test_build_category_prompt_only_positive(self):
#         positive = ["tops", "skirts"]
#         prompt = gct.build_category_prompt(positive)
#         self.assertIn("Only include categories", prompt)

#     def test_clean_csv_removes_negative_keywords(self):
#         csv = """Category ID,Parent ID,Category Name
#                 1,0,Women
#                 2,1,Men
#                 3,1,Kids
#                 4,1,Jeans"""
#         cleaned = gct.clean_csv(csv, "Men,Kids")
#         self.assertNotIn("Men", cleaned)
#         self.assertNotIn("Kids", cleaned)
#         self.assertIn("Women", cleaned)
#         self.assertIn("Jeans", cleaned)

#     def test_save_csv_file_creates_file(self):
#         content = "Category ID,Parent ID,Category Name\n1,0,Women"
#         filename = gct.save_csv_file(content)
#         with open(filename, "r", encoding="utf-8") as f:
#             data = f.read()
#         self.assertEqual(data, content)

# if __name__ == "__main__":
#     unittest.main()



import unittest
from unittest.mock import patch, MagicMock
import os
import generater_category as gct

class TestCategoryTreeGenerator(unittest.TestCase):

    # --- extract_json_from_text ---
    def test_extract_json_from_text_valid(self):
        text = '''
        {
            "positive": ["Mobiles", "Laptops"],
            "negative": ["Refurbished", "Used"]
        }
        '''
        expected = {"positive": ["Mobiles", "Laptops"], "negative": ["Refurbished", "Used"]}
        result = gct.extract_json_from_text(text)
        self.assertEqual(result, expected)

    def test_extract_json_from_text_invalid(self):
        text = "Invalid JSON"
        with self.assertRaises(ValueError):
            gct.extract_json_from_text(text)

    def test_extract_json_from_text_malformed_json(self):
        text = '''
        {
            "positive": ["Mobiles",
            "negative": ["Kids"]
        }
        '''
        with self.assertRaises(ValueError):
            gct.extract_json_from_text(text)

    # --- get_extracted_keywords ---
    @patch("google.generativeai.GenerativeModel.generate_content")
    def test_get_extracted_keywords(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "positive": ["Cameras", "Accessories"],
            "negative": ["Refurbished", "Kids"]
        }
        '''
        mock_generate.return_value = mock_response
        model_patch = patch("google.generativeai.GenerativeModel")
        with model_patch as mock_model_class:
            mock_model_class.return_value.generate_content.return_value = mock_response
            result = gct.get_extracted_keywords("Show Cameras and Accessories, avoid Refurbished and Kids")
            self.assertEqual(result["positive"], ["Cameras", "Accessories"])
            self.assertEqual(result["negative"], ["Refurbished", "Kids"])

    # --- build_category_prompt ---
    def test_build_category_prompt_with_negatives(self):
        positive = ["Electronics", "Laptops"]
        negative = ["Used"]
        prompt = gct.build_category_prompt(positive, negative)
        self.assertIn("Positive keywords", prompt)
        self.assertIn("Exclude anything related", prompt)

    def test_build_category_prompt_only_positive(self):
        positive = ["Mobiles", "Accessories"]
        prompt = gct.build_category_prompt(positive)
        self.assertIn("Only include categories", prompt)

    # --- clean_csv ---
    def test_clean_csv_removes_negative_keywords(self):
        csv = """Category ID,Parent ID,Category Name
1,0,Electronics
2,1,Used
3,1,Refurbished
4,1,Mobiles"""
        cleaned = gct.clean_csv(csv, "Used,Refurbished")
        self.assertNotIn("Used", cleaned)
        self.assertNotIn("Refurbished", cleaned)
        self.assertIn("Electronics", cleaned)
        self.assertIn("Mobiles", cleaned)

    def test_clean_csv_case_insensitive_filtering(self):
        csv = """Category ID,Parent ID,Category Name
1,0,Electronics
2,1,refurbished
3,1,Laptops"""
        cleaned = gct.clean_csv(csv, "Refurbished")
        self.assertNotIn("refurbished", cleaned.lower())
        self.assertIn("Laptops", cleaned)

    def test_clean_csv_all_rows_removed(self):
        csv = """Category ID,Parent ID,Category Name
1,0,Used
2,1,Refurbished"""
        cleaned = gct.clean_csv(csv, "Used,Refurbished")
        self.assertEqual(cleaned.strip(), "Category ID,Parent ID,Category Name")

    # --- save_csv_file ---
    def test_save_csv_file_creates_file(self):
        content = "Category ID,Parent ID,Category Name\n1,0,Electronics"
        filename = gct.save_csv_file(content)
        self.assertTrue(os.path.exists(filename))
        with open(filename, "r", encoding="utf-8") as f:
            data = f.read()
        self.assertEqual(data, content)
        os.remove(filename)

    def test_save_csv_file_has_valid_uuid_name(self):
        content = "Category ID,Parent ID,Category Name\n1,0,Cameras"
        filename = gct.save_csv_file(content)
        self.assertRegex(filename, r"^category_tree_[a-f0-9\-]{36}\.csv$")
        os.remove(filename)


if __name__ == "__main__":
    unittest.main()
