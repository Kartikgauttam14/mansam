import unittest
from unittest.mock import patch
import server


class RagFlowTests(unittest.TestCase):
    def test_two_stage_retrieval_and_verified_product_links(self):
        product = server.CATALOG_PRODUCTS[0]
        product_id = str(product['id'])
        with patch.object(server, 'rag_completion', side_effect=[
            {'query': 'rose perfume', 'use_context': False, 'product_request': True},
            {'answer': 'Here is a fragrance from our catalogue.', 'productIds': [product_id]},
        ]) as model, patch.object(server, 'retrieve_products', return_value=[product]), \
                patch.object(server, 'retrieve_ssot_records', return_value=[]):
            result = server.rag_answer('Recommend a rose fragrance', 'en')
        self.assertEqual(model.call_count, 2)
        self.assertIn('product_evidence', model.call_args.args[0][-1]['content'])
        self.assertEqual(result['productIds'], [product_id])
        self.assertEqual(result['productLinks'][0]['url'], server.product_url(product))

    def test_policy_question_uses_workbook_and_keeps_history(self):
        with patch.object(server, 'rag_completion', side_effect=[
            {'query': 'delivery', 'use_context': False, 'product_request': False},
            {'answer': 'Please contact the boutique for confirmation.', 'productIds': []},
        ]) as model, patch.object(server, 'retrieve_ssot_records', return_value=[('Delivery', {'policy': 'Contact boutique'})]), \
                patch.object(server, 'retrieve_products') as products:
            result = server.rag_answer('Do you deliver?', 'en', conversation=[{'role': 'customer', 'text': 'I want rose'}])
        products.assert_not_called()
        self.assertIn('Contact boutique', model.call_args.args[0][-1]['content'])
        self.assertEqual(model.call_args.args[0][1]['content'], 'I want rose')
        self.assertEqual(result['intent'], 'rag_answer')

    def test_followup_includes_previous_product_even_without_search_results(self):
        product = server.CATALOG_PRODUCTS[0]
        with patch.object(server, 'rag_completion', side_effect=[
            {'query': 'price', 'use_context': True, 'product_request': True},
            {'answer': 'Product details.', 'productIds': [str(product['id'])]},
        ]), patch.object(server, 'retrieve_products', return_value=[]):
            result = server.rag_answer('How much is it?', 'en', [str(product['id'])])
        self.assertEqual(result['productIds'], [str(product['id'])])

    def test_unverified_product_id_is_rejected(self):
        with patch.object(server, 'rag_completion', side_effect=[
            {'query': 'rose', 'product_request': True},
            {'answer': 'Invented product', 'productIds': ['nonexistent']},
        ]):
            result = server.rag_answer('Recommend a perfume', 'en')
        self.assertEqual(result['intent'], 'rag_unavailable')
        self.assertEqual(result['productLinks'], [])

    def test_missing_token_and_invalid_model_output_do_not_invent_answers(self):
        with patch.object(server, 'HF_TOKEN', ''):
            self.assertEqual(server.rag_answer('rose', 'en')['intent'], 'rag_unavailable')
        with patch.object(server, 'rag_completion', return_value={'query': []}):
            self.assertEqual(server.rag_answer('مسك', 'ar')['language'], 'ar')


if __name__ == '__main__':
    unittest.main()
