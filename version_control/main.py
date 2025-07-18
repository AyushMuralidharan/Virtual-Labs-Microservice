from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import os
import shutil
import git
import tempfile
import uuid
from pydantic import BaseModel
import logging
import json
from datetime import datetime
from version_control.utils.service_health import service_health
from version_control.middleware.service_check import ServiceCheckMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Version Control Microservice",
    description="A microservice implementing basic version control functionality",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware
app.add_middleware(ServiceCheckMiddleware)

# Base directory for repositories
REPOS_DIR = os.environ.get("REPOS_DIR", "/app/repositories")

# Ensure the repositories directory exists
os.makedirs(REPOS_DIR, exist_ok=True)

# Models
class CommitInfo(BaseModel):
    message: str
    author_name: str
    author_email: str

class BranchCreate(BaseModel):
    name: str
    source_branch: Optional[str] = "main"

class FileContent(BaseModel):
    content: str
    commit_message: str
    author_name: str
    author_email: str

# Helper functions
def get_repo_path(repo_name: str) -> str:
    """Get the full path to a repository."""
    return os.path.join(REPOS_DIR, repo_name)

def repo_exists(repo_name: str) -> bool:
    """Check if a repository exists."""
    repo_path = get_repo_path(repo_name)
    return os.path.exists(repo_path) and os.path.isdir(repo_path)

def get_repo(repo_name: str) -> git.Repo:
    """Get a Git repository object."""
    if not repo_exists(repo_name):
        raise HTTPException(status_code=404, detail=f"Repository '{repo_name}' not found")
    
    repo_path = get_repo_path(repo_name)
    try:
        return git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        raise HTTPException(status_code=400, detail=f"'{repo_name}' is not a valid Git repository")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint to check if the service is running."""
    return {"message": "Version Control Microservice is running"}

@app.get("/repos")
async def list_repositories():
    """List all repositories."""
    try:
        if not os.path.exists(REPOS_DIR):
            return {"repositories": []}
        
        repos = [name for name in os.listdir(REPOS_DIR) 
                if os.path.isdir(os.path.join(REPOS_DIR, name)) and 
                os.path.exists(os.path.join(REPOS_DIR, name, ".git"))]
        
        return {"repositories": repos}
    except Exception as e:
        logger.error(f"Error listing repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list repositories: {str(e)}")

@app.post("/repos/{repo_name}")
async def create_repository(repo_name: str):
    """Create a new repository."""
    repo_path = get_repo_path(repo_name)
    
    if repo_exists(repo_name):
        raise HTTPException(status_code=400, detail=f"Repository '{repo_name}' already exists")
    
    try:
        # Create the repository directory
        os.makedirs(repo_path, exist_ok=True)
        
        # Initialize a new Git repository
        repo = git.Repo.init(repo_path)
        
        # Create an initial README.md file
        readme_path = os.path.join(repo_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(f"# {repo_name}\n\nThis repository was created by the Version Control Microservice.")
        
        # Add and commit the README file
        repo.git.add("README.md")
        repo.git.config("user.name", "Version Control Service")
        repo.git.config("user.email", "service@example.com")
        repo.git.commit("-m", "Initial commit")
        
        return {"message": f"Repository '{repo_name}' created successfully"}
    except Exception as e:
        # Clean up if something went wrong
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path, ignore_errors=True)
        
        logger.error(f"Error creating repository: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create repository: {str(e)}")

@app.delete("/repos/{repo_name}")
async def delete_repository(repo_name: str):
    """Delete a repository."""
    repo_path = get_repo_path(repo_name)
    
    if not repo_exists(repo_name):
        raise HTTPException(status_code=404, detail=f"Repository '{repo_name}' not found")
    
    try:
        shutil.rmtree(repo_path)
        return {"message": f"Repository '{repo_name}' deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting repository: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete repository: {str(e)}")

@app.get("/repos/{repo_name}/branches")
async def list_branches(repo_name: str):
    """List all branches in a repository."""
    repo = get_repo(repo_name)
    
    try:
        branches = [branch.name for branch in repo.branches]
        return {"branches": branches}
    except Exception as e:
        logger.error(f"Error listing branches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list branches: {str(e)}")

@app.post("/repos/{repo_name}/branches")
async def create_branch(repo_name: str, branch_data: BranchCreate):
    """Create a new branch in a repository."""
    repo = get_repo(repo_name)
    
    try:
        # Check if the branch already exists
        if branch_data.name in [branch.name for branch in repo.branches]:
            raise HTTPException(status_code=400, detail=f"Branch '{branch_data.name}' already exists")
        
        # Check if the source branch exists
        if branch_data.source_branch not in [branch.name for branch in repo.branches]:
            raise HTTPException(status_code=404, detail=f"Source branch '{branch_data.source_branch}' not found")
        
        # Create the new branch
        source_branch = repo.branches[branch_data.source_branch]
        repo.create_head(branch_data.name, source_branch)
        
        return {"message": f"Branch '{branch_data.name}' created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating branch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create branch: {str(e)}")

@app.get("/repos/{repo_name}/commits")
async def list_commits(repo_name: str, branch: Optional[str] = None):
    """List commits in a repository, optionally filtered by branch."""
    repo = get_repo(repo_name)
    
    try:
        if branch:
            if branch not in [b.name for b in repo.branches]:
                raise HTTPException(status_code=404, detail=f"Branch '{branch}' not found")
            commits = list(repo.iter_commits(branch))
        else:
            commits = list(repo.iter_commits())
        
        commit_list = []
        for commit in commits:
            commit_list.append({
                "id": commit.hexsha,
                "message": commit.message,
                "author": {
                    "name": commit.author.name,
                    "email": commit.author.email
                },
                "date": commit.committed_datetime.isoformat(),
                "stats": {
                    "files_changed": len(commit.stats.files),
                    "insertions": commit.stats.total["insertions"],
                    "deletions": commit.stats.total["deletions"]
                }
            })
        
        return {"commits": commit_list}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing commits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list commits: {str(e)}")

@app.get("/repos/{repo_name}/files")
async def list_files(repo_name: str, branch: Optional[str] = "main"):
    """List files in a repository branch."""
    repo = get_repo(repo_name)
    
    try:
        if branch not in [b.name for b in repo.branches]:
            raise HTTPException(status_code=404, detail=f"Branch '{branch}' not found")
        
        # Checkout the branch
        repo.git.checkout(branch)
        
        # Get the repository root directory
        repo_root = repo.working_dir
        
        # List all files (excluding .git directory)
        files = []
        for root, dirs, filenames in os.walk(repo_root):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, repo_root)
                files.append(rel_path)
        
        return {"files": files}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.get("/repos/{repo_name}/files/{file_path:path}")
async def get_file_content(repo_name: str, file_path: str, branch: Optional[str] = "main"):
    """Get the content of a file in a repository branch."""
    repo = get_repo(repo_name)
    
    try:
        if branch not in [b.name for b in repo.branches]:
            raise HTTPException(status_code=404, detail=f"Branch '{branch}' not found")
        
        # Checkout the branch
        repo.git.checkout(branch)
        
        # Get the full path to the file
        full_path = os.path.join(repo.working_dir, file_path)
        
        # Check if the file exists
        if not os.path.isfile(full_path):
            raise HTTPException(status_code=404, detail=f"File '{file_path}' not found")
        
        # Read the file content
        with open(full_path, "r") as f:
            content = f.read()
        
        return {"content": content}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get file content: {str(e)}")

@app.put("/repos/{repo_name}/files/{file_path:path}")
async def update_file(repo_name: str, file_path: str, file_data: FileContent, branch: Optional[str] = "main"):
    """Update a file in a repository branch and commit the changes."""
    repo = get_repo(repo_name)
    
    try:
        if branch not in [b.name for b in repo.branches]:
            raise HTTPException(status_code=404, detail=f"Branch '{branch}' not found")
        
        # Checkout the branch
        repo.git.checkout(branch)
        
        # Get the full path to the file
        full_path = os.path.join(repo.working_dir, file_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write the file content
        with open(full_path, "w") as f:
            f.write(file_data.content)
        
        # Add the file to the staging area
        repo.git.add(file_path)
        
        # Configure the author
        repo.git.config("user.name", file_data.author_name)
        repo.git.config("user.email", file_data.author_email)
        
        # Commit the changes
        repo.git.commit("-m", file_data.commit_message)
        
        return {"message": f"File '{file_path}' updated and committed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")

@app.delete("/repos/{repo_name}/files/{file_path:path}")
async def delete_file(
    repo_name: str, 
    file_path: str, 
    commit_message: str = Form(...),
    author_name: str = Form(...),
    author_email: str = Form(...),
    branch: Optional[str] = "main"
):
    """Delete a file from a repository branch and commit the changes."""
    repo = get_repo(repo_name)
    
    try:
        if branch not in [b.name for b in repo.branches]:
            raise HTTPException(status_code=404, detail=f"Branch '{branch}' not found")
        
        # Checkout the branch
        repo.git.checkout(branch)
        
        # Get the full path to the file
        full_path = os.path.join(repo.working_dir, file_path)
        
        # Check if the file exists
        if not os.path.isfile(full_path):
            raise HTTPException(status_code=404, detail=f"File '{file_path}' not found")
        
        # Remove the file
        os.remove(full_path)
        
        # Add the removal to the staging area
        repo.git.add(file_path)
        
        # Configure the author
        repo.git.config("user.name", author_name)
        repo.git.config("user.email", author_email)
        
        # Commit the changes
        repo.git.commit("-m", commit_message)
        
        return {"message": f"File '{file_path}' deleted and committed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@app.post("/repos/{repo_name}/checkout")
async def checkout_branch(repo_name: str, branch: str):
    """Checkout a branch in a repository."""
    repo = get_repo(repo_name)
    
    try:
        if branch not in [b.name for b in repo.branches]:
            raise HTTPException(status_code=404, detail=f"Branch '{branch}' not found")
        
        # Checkout the branch
        repo.git.checkout(branch)
        
        return {"message": f"Checked out branch '{branch}' successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking out branch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to checkout branch: {str(e)}")

@app.get("/repos/{repo_name}/diff")
async def get_diff(repo_name: str, commit1: str, commit2: Optional[str] = None):
    """Get the diff between two commits."""
    repo = get_repo(repo_name)
    
    try:
        # If commit2 is not provided, compare with the previous commit
        if not commit2:
            commit_obj = repo.commit(commit1)
            if len(commit_obj.parents) > 0:
                commit2 = commit_obj.parents[0].hexsha
            else:
                # This is the first commit
                return {"diff": "This is the first commit, no diff available"}
        
        # Get the diff
        diff = repo.git.diff(commit2, commit1)
        
        return {"diff": diff}
    except git.BadName:
        raise HTTPException(status_code=404, detail=f"Commit not found")
    except Exception as e:
        logger.error(f"Error getting diff: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get diff: {str(e)}")

@app.post("/repos/{repo_name}/merge")
async def merge_branches(
    repo_name: str, 
    source_branch: str = Form(...),
    target_branch: str = Form(...),
    commit_message: Optional[str] = Form("Merge branch"),
    author_name: str = Form(...),
    author_email: str = Form(...)
):
    """Merge a source branch into a target branch."""
    repo = get_repo(repo_name)
    
    try:
        # Check if branches exist
        branches = [b.name for b in repo.branches]
        if source_branch not in branches:
            raise HTTPException(status_code=404, detail=f"Source branch '{source_branch}' not found")
        if target_branch not in branches:
            raise HTTPException(status_code=404, detail=f"Target branch '{target_branch}' not found")
        
        # Checkout the target branch
        repo.git.checkout(target_branch)
        
        # Configure the author
        repo.git.config("user.name", author_name)
        repo.git.config("user.email", author_email)
        
        # Merge the source branch
        try:
            repo.git.merge(source_branch, "-m", commit_message)
            return {"message": f"Merged '{source_branch}' into '{target_branch}' successfully"}
        except git.GitCommandError as e:
            if "CONFLICT" in str(e):
                # Handle merge conflicts
                repo.git.merge("--abort")
                return {"message": f"Merge conflict detected. Merge aborted.", "status": "conflict"}
            else:
                raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error merging branches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to merge branches: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for the service."""
    return {"status": "healthy"}

@app.get("/services/status")
async def check_services():
    """Check the status of all dependent services."""
    status = await service_health.check_all_services()
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
