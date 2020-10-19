from collections import defaultdict
from github import Github


def get_git_skills(username):
    g = Github()
    user = g.get_user(username)

    tags = defaultdict()
    languages = defaultdict(int)

    for repo in user.get_repos():
        # new_repo_languages = repo.get_languages()
        # for lang in new_repo_languages:
        #     languages[lang] += new_repo_languages[lang]

        new_repo_topics = repo.get_topics()
        for topic in new_repo_topics:
            print (topic)

    print(languages)
    return sorted(languages.items(), key=lambda x: x[1], reverse=True)


