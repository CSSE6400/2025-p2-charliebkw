from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    if request.args.get("completed") == "true":
        is_completed = True
    elif request.args.get("completed") == "false":
        is_completed = False
    else:
        is_completed = None

    if request.args.get("window"):
        window = int(request.args.get("window"))
    else:
        window = None
    

    todos = Todo.query.all()
    result = []
    for todo in todos:
        if todo.completed == is_completed or is_completed is None:
            if window is not None:
                deadline_at = todo.deadline_at
                window_days_from_today = datetime.datetime.today() + datetime.timedelta(days=window)
                return jsonify({"deadline": deadline_at, "window_days": window_days_from_today})
                if deadline_at < window_days_from_today:
                    result.append(todo.to_dict())
            else:
               result.append(todo.to_dict()) 
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    acceptable_fields = ["title", "description", "completed", "deadline_at"]

    for key in request.json:
        if key not in acceptable_fields:
            return jsonify({"error": "Unexpected value"}), 400

    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    
    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    acceptable_fields = ["title", "description", "completed", "deadline_at"]

    for key in request.json:
        if key not in acceptable_fields:
            return jsonify({"error": "Unexpected update value"}), 400
        
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    
    db.session.commit()

    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
    
