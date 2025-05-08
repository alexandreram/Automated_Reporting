from main.models import Profile

def can_access(requesting_user, target_user):
    """
    Check if the requesting_user can access the target_user's data.
    """
    if requesting_user.profile.level == 1:
        # Level 1 (Admin) can access everyone
        return True

    if requesting_user.profile.level == 2:
        # Level 2 can access Level 3 and Level 4 under them
        return target_user.profile.manager == requesting_user.profile

    if requesting_user.profile.level == 3:
        # Level 3 can access Level 4 under them
        return target_user.profile.manager == requesting_user.profile

    # Level 4 cannot access anyone
    return False

def get_all_subordinates(manager, visited=None):
        if visited is None:
            visited = set()

        # Avoid infinite recursion by checking if the manager has already been visited
        if manager in visited:
            return []

        visited.add(manager)

        subordinates = Profile.objects.filter(manager=manager)
        all_subordinates = list(subordinates)

        for subordinate in subordinates:
            all_subordinates.extend(get_all_subordinates(subordinate, visited))

        return all_subordinates