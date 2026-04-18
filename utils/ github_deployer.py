"""
GitHub deployment automation
Handles repository creation and file pushing via GitHub API
"""
import base64
import requests
from typing import Dict, List, Optional
from github import Github, GithubException
from utils.config import Config

class GitHubDeployer:
    """Manages GitHub repository operations"""
    
    def __init__(self):
        """Initialize GitHub deployer with authentication"""
        try:
            self.github = Github(Config.GITHUB_TOKEN)
            self.username = Config.GITHUB_USERNAME
            self.user = self.github.get_user()
        except Exception as e:
            print(f"GitHub initialization error: {str(e)}")
            self.github = None
    
    def create_repository(self, repo_name: str, description: str = "") -> Optional[Dict]:
        """
        Create a new GitHub repository
        
        Args:
            repo_name: Name of the repository
            description: Repository description
            
        Returns:
            Repository info or None if failed
        """
        try:
            if not self.github:
                raise Exception("GitHub client not initialized")
            
            # Check if repository exists
            try:
                repo = self.user.get_repo(repo_name)
                return {"exists": True, "clone_url": repo.clone_url}
            except GithubException:
                # Create new repository
                repo = self.user.create_repo(
                    name=repo_name,
                    description=description,
                    private=False,
                    auto_init=True
                )
                return {
                    "created": True,
                    "clone_url": repo.clone_url,
                    "html_url": repo.html_url,
                    "name": repo.name
                }
        except Exception as e:
            print(f"Repository creation error: {str(e)}")
            return {"error": str(e)}
    
    def push_files(self, repo_name: str, files: Dict[str, str], commit_message: str = "Initial bot deployment") -> Dict:
        """
        Push multiple files to GitHub repository
        
        Args:
            repo_name: Target repository name
            files: Dictionary of file paths to content
            commit_message: Git commit message
            
        Returns:
            Deployment status
        """
        try:
            if not self.github:
                raise Exception("GitHub client not initialized")
            
            repo = self.user.get_repo(repo_name)
            results = []
            
            for file_path, content in files.items():
                try:
                    # Encode content to base64
                    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
                    
                    # Check if file exists to determine if update or create
                    try:
                        existing_file = repo.get_contents(file_path)
                        repo.update_file(
                            path=file_path,
                            message=commit_message,
                            content=content,
                            sha=existing_file.sha,
                            branch="main"
                        )
                        results.append({"file": file_path, "status": "updated"})
                    except GithubException:
                        # File doesn't exist, create it
                        repo.create_file(
                            path=file_path,
                            message=commit_message,
                            content=content,
                            branch="main"
                        )
                        results.append({"file": file_path, "status": "created"})
                except Exception as e:
                    results.append({"file": file_path, "status": "failed", "error": str(e)})
            
            return {
                "success": True,
                "repository": repo.html_url,
                "files": results,
                "commit_message": commit_message
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_repository(self, repo_name: str) -> Dict:
        """Delete a repository (use with caution)"""
        try:
            repo = self.user.get_repo(repo_name)
            repo.delete()
            return {"success": True, "message": f"Repository {repo_name} deleted"}
        except Exception as e:
            return {"success": False, "error": str(e)}