from github import Github

# def get_git_skills( username ):

g = Github()
user = g.get_user("v0lv0")

languages = {}
for repo in user.get_repos():
    new_repo_languages = repo.get_languages()
    for key in new_repo_languages:
        if key in languages:
            languages[key] = languages[key] + new_repo_languages[key]
        else:
            languages[key] = new_repo_languages[key]

languages = sorted(languages.items(), key=lambda x: [1], reverse=True)
print(languages)