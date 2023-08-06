"""
Repository-related operations
"""
import os
import tempfile
import git

class Repository:
    """
    Abstracts git-related operations.
    """
    def __init__(self, path :str=os.getcwd(), version :str=None):
        """
        def __init__(self, path :str=os.getcwd(), version :str=None):

        Receives the path to the repository you wish to manage.

        Input:
          - path: a local or remote (starting with 'git@github.com') path to the repositpry you wish to manage.
          - version: a tag name you with to checkout.

        """
        if path.startswith('git@github.com'): #It is a remote repository
            self.remote_url = path
            self.path = tempfile.TemporaryDirectory()
            self.rep = git.Repo.clone_from(self.remote_url, self.path.name)
        else: #it is a local repository
            self.remote_url = None
            self.path = path
            self.rep = git.Repo(self.path)
        
        if version:
            self.rep.git.checkout(version)


    def get_version(self) -> str:
        """
        def get_version(self) -> str

        Returns the version of the cloned repository.
        """
        return self.rep.git.describe(tags=True)

    
    def get_location(self):
        """
        def get_version(self) -> str

        Returns the location (URL) of the cloned repository in GtHub.
        """
        return self.rep.remotes.origin.url
