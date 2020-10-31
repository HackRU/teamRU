"""Utility functions that are used throughout the codebase."""

from functools import wraps

from src.flaskapp.db import coll


def format_string(input_):
    """Formats the input depending on if it is a string or a list of strings.

    Determines the type of the input. If it is a string then strips leading spaces and lowercases
    all letters. If it is a list, then the aforementioned process is applied to each of the list elements.

    Arg:
        s: string or list of strings that needs to be formatted

    Return:
        a formatted string is returned if a string is provided
        a formatted list is returned if a list is provided
    """
    if isinstance(input_, str):
        return input_.strip().lower()
    if isinstance(input_, list):
        res = []
        for element in input_:
            if isinstance(element, str):
                res.append(element.strip().lower())
            else:
                # NOTE when the element is not of string typ (we can handle this case different if necessary)
                res.append(element)
        return res
    # NOTE Simply returns the input if the input is not a string or a list
    return input_

    #  TestCases:
    #     print(format_string("  JaS on   "))
    #     print(format_string(["  JaS on   C  ", "CHE"]))
    #     print(format_string(["  JaS on   C  ", "CHE", 6]))
    #     print(format_string(6))
    #     print(format_string({"TeamRU": 2020}))


def aggregate_team_meta(members):
    team_members = coll("users").find({"_id": {"$in": members}})
    skills, prizes, interests = set(), set(), set()
    seriousness = 0

    for member in team_members:
        skills.update(member["skills"])
        prizes.update(member["prizes"])
        interests.update(member["interests"])
        seriousness += member["seriousness"]
    seriousness /= len(members)
    return {
        "skills": list(skills),
        "prizes": list(prizes),
        "interests": list(interests),
        "seriousness": seriousness,
    }


def format_team_object(team):
    team["team_id"] = team.pop("_id")

    # Change structure of members list in team response
    members = []
    for member_email in team["members"]:
        user = coll("users").find_one({"_id": member_email})
        partial_user = {
            "user_id": user["_id"],
            "bio": user["bio"],
            "seriousness": user["seriousness"]
        }
        members.append(partial_user)

    team["members"] = members

    return team
