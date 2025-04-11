from flask import Flask, render_template, request, jsonify, redirect, url_for
from src.models.git_repo_bot import GitRepoBot
import os
from git import Repo, GitCommandError

app = Flask(__name__)

# Initialize the bot at startup with a default repository path

@app.route('/')
def index():
    return render_template('landing.html')  # Your new landing page

@app.route('/chat')
def chat():
    return render_template('index.html')  # Your existing chat interface

@app.route('/setup_repo', methods=['POST'])
def setup_repo():
    repo_url = request.json.get('repo_url')
    target_directory = request.json.get('target_directory')
    
    if not repo_url:
        return jsonify({"status": "error", "message": "Repository URL is required"})
    
    # Use the provided target directory or the default one
    if not target_directory:
        # Get platform-appropriate cache directory
        if os.name == 'nt':  # Windows
            cache_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'RAGGGIT')
        else:
            cache_dir = os.path.join(os.path.expanduser('~'), '.cache', 'RAGGGIT')
        os.makedirs(cache_dir, exist_ok=True)

        target_directory = cache_dir
        # target_directory = os.environ.get('DEFAULT_TARGET_DIR', "C:/Users/nithi/.cache/RAGGGIT")

    try:
        # Clone or update the repository
        repo_path = clone_or_update_repo(repo_url, target_directory)
        
        if not repo_path:
            return jsonify({"status": "error", "message": "Failed to clone repository"})
        
        # Update the repo_bot with the new repository path
        global repo_bot
        repo_bot = GitRepoBot(repo_path=repo_path)
        
        return jsonify({"status": "success", "message": "Repository loaded successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def clone_or_update_repo(repo_url, parent_dir):
    repo_name = os.path.basename(repo_url).replace(".git", "")
    repo_dir = os.path.join(parent_dir, repo_name)

    if os.path.exists(repo_dir):
        try:
            print(f"Repository already exists at {repo_dir}. Pulling latest changes...")
            repo = Repo(repo_dir)
            repo.remotes.origin.pull()
            print("Repository updated successfully.")
        except GitCommandError as e:
            print(f"Error pulling repository: {e}")
            raise e
    else:
        try:
            print(f"Cloning repository into {repo_dir}...")
            repo = Repo.clone_from(repo_url, repo_dir)
            print("Clone completed.")
        except Exception as e:
            print(f"Error cloning repository: {e}")
            raise e

    return repo_dir

@app.route('/query', methods=['POST'])
def process_query():
    user_query = request.json.get('query')
    try:
        response,context = repo_bot.answer_query(user_query)
        print(response)
        return jsonify({"status": "success", "response": response.raw, "context": context})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/save_note', methods=['POST'])
def save_note():
    # In a real application, you'd save this to a database
    query = request.json.get('query')
    response = request.json.get('response')
    note = request.json.get('note')
    
    # Here you would implement actual saving logic
    return jsonify({"status": "success", "message": "Note saved successfully"})

if __name__ == "__main__":
    app.run(debug=True)