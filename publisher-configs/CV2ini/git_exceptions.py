#!/usr/bin/env python
# -*- coding: utf-8 -*-


class GitHubException(Exception):
    """
    Basic exception for GitHub errors.

    """
    # API call url
    URI = []

    def __init__(self, msg):
        self.uri = GitHubException.URI
        self.msg = msg
        self.msg += "\n<url: '{}'>".format(self.uri)
        super(GitHubException, self).__init__(self.msg)


class GitHubUnauthorized(GitHubException):
    """
    Raised when no read access on GitHub repo.

    """

    def __init__(self):
        self.msg = "GitHub permission denied"
        super(self.__class__, self).__init__(self.msg)


class GitHubAPIRateLimit(GitHubException):
    """
    Raised when GitHub API rate limit exceeded.

    """

    def __init__(self):
        self.msg = "GitHub API rate limit exceeded (try again in 60 minutes or submit GitHub user/password)"
        super(self.__class__, self).__init__(self.msg)


class GitHubFileNotFound(GitHubException):
    """
    Raised when no file found on GitHub repo.

    """

    def __init__(self):
        self.msg = "GitHub file not found"
        super(self.__class__, self).__init__(self.msg)


class GitHubConnectionError(GitHubException):
    """
    Raised when the GitHub request fails.

    """

    def __init__(self):
        self.msg = "GitHub connection error"
        super(self.__class__, self).__init__(self.msg)
