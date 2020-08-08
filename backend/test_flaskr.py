import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question = {
            'question': 'New question',
            'answer': 'New answer',
            'category': 1,
            'difficulty': 1
        }
        
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))


    def test_404_categories_request_not_allowed(self):
        # res = self.client().get('/categories?page=2')
        res = self.client().get('/categories/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.')


    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
    
    def test_404_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.')

    def test_delete_question(self):
        question = Question(question='question', answer='answer', category=1, difficulty=1)
        question.insert()
        question_id = question.id
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        # recheck in the db the question has been deleted
        question_not_exsited = Question.query.get(question_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question_id'], question_id)
        self.assertEqual(question_not_exsited, None)

    def test_404_delete_question_id_not_found(self):
        res = self.client().delete('/questions/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.')
    
    def test_post_question(self):
        total_question_prev = len(Question.query.all())
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        total_question_curr = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully created!')
        self.assertEqual(total_question_prev + 1, total_question_curr)

    def test_400_post_question_missing_para(self):
        invalid_question = {
            # question is missing
            'answer': 'New answer',
            'category': 1,
            'difficulty': 1
        }
        res = self.client().post('/questions', json=invalid_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request.')

    def test_search_question(self):
        search = {'searchTerm': 'a'}
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
    
    def test_400_search_question_searchterm_empty(self):
        search = {'searchTerm': ''}
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request.')
    
    def test_select_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_select_category_id_not_found(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.')
    
    def test_next_question(self):
        quiz_data = {
            'previous_questions': [],
            'quiz_category': {'type': None, 'id': 1}
        }
        res = self.client().post('/quizzes', json=quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_next_question(self):
        quiz_data = {
            'previous_questions': [],
            'quiz_category': {'type': None, 'id': 1}
        }
        res = self.client().post('/quizzes', json=quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
    
    def test_404_next_question_quiz_category_invalid(self):
        quiz_data = {
            'previous_questions': [],
            'quiz_category': {'type': None, 'id': 1000}
        }
        res = self.client().post('/quizzes', json=quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.')
    
    def test_404_next_question_not_exist(self):
        category_id = 1
        selections = Question.query.filter_by(category=category_id).all()
        previous_questions = [question.id for question in selections]

        quiz_data = {
            'previous_questions': previous_questions,
            'quiz_category': {'type': None, 'id': category_id}
        }
        res = self.client().post('/quizzes', json=quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.')
        
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()