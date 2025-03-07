def get_actor_or_director(person, sets):
    if person in sets["actors"]:
        return True, "actors"

    if person in sets["directors"]:
        return True, "directors"

    else:
        return False, "unknown"