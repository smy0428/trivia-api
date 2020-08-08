import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selections):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  return selections[start:end]


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  #CORS(app, resources={r'/*': {'origins': '*'}})
  CORS(app)

  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, PATCH, DELETE, OPTIONS')
    return response

  '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    if categories is None:
      abort(404)

    formatted_categories = {category.id: category.type for category in categories}
    return jsonify({
      'success': True,
      'categories': formatted_categories
    })

  '''
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''
  @app.route('/questions')
  def get_questions():
    selections = Question.query.order_by(Question.id).all()
    categories = Category.query.order_by(Category.id).all()
    questions = paginate_questions(request, selections)

    # None is self-tpye in python, ! = [], ! = ''
    # here questions could be [], have to be checked
    if len(questions) == 0 or categories is None:
      abort(404)
    
    formatted_questions = [question.format() for question in questions]
    formatted_categories = {category.id: category.type for category in categories}

    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(selections),
      'categories': formatted_categories
    })

  '''
  Create an endpoint to DELETE question using a question ID. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)

    # abort itslef rasie an exception
    # can not be in the try block 
    if question is None:
      abort(404)  
    try:  
      question.delete()
      return jsonify({
        'success': True,
        'question_id': question_id
      })
    except:
      abort(422)


  '''
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()
    question = body.get('question')
    answer = body.get('answer')
    difficulty = body.get('difficulty')
    category = body.get('category')

    if (question is None or 
        answer is None or 
        difficulty is None or 
        category is None):
        abort(400)

    try:
      new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
      new_question.insert()
      return jsonify({
        'success': True,
        'message': 'Question successfully created!'
    })

    except:
      abort(422)

  '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()
    search_term = body.get('searchTerm')

    if search_term:
      selections = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
      questions = paginate_questions(request, selections)
      formatted_questions = [question.format() for question in questions]

      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(selections),
      })
    else:
      abort(400)


  '''
  Create a GET endpoint to get questions based on category. 
  '''
  @app.route('/categories/<int:catetory_id>/questions', methods=['GET'])
  def select_categoty(catetory_id):
    category = Category.query.get(catetory_id)
    if category is None:
      abort(404)
    
    selections = Question.query.filter_by(category=catetory_id).all()
    questions = paginate_questions(request, selections)
    formatted_questions = [question.format() for question in questions]

    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(selections),
      'current_category': catetory_id
    })


  '''
  produce a random int in [left, right)
  '''
  def random_number(left, right):
    return int((right - left) * random.random() + left)
  

  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def next_question():
    try:
      body = request.get_json()
      previous_questions = body.get('previous_questions')
      quiz_category_id = body.get('quiz_category').get('id')
      
      if quiz_category_id == 0:
        selections = Question.query
      else:
        selections = Question.query.filter_by(category=quiz_category_id)

      questions = selections.filter(Question.id.notin_(previous_questions)).all()
    except:
      abort(422)
    if len(questions) == 0:
      abort(404)
    else:
      randam_index = random_number(0,len(questions))
      question = questions[randam_index]
      return jsonify({
        'success': True,
        'question': question.format()
      })


  '''
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request.'
    }), 400


  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found.'
    }), 404
  
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Request was unprocessable.'
    }), 422
  return app

    