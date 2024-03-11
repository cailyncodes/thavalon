from http.server import BaseHTTPRequestHandler
import json
import random


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        # parse request body as json
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        players = data.get("players", [])
        variant = data.get("variant", "thavalon")
        num_players = len(players)
        if not (5 <= num_players <= 10):
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write('{"error":"Invalid number of players"}'.encode("utf-8"))
            return

        players = set(players)  # use as set to avoid duplicate players
        players = list(players)  # convert to list
        random.shuffle(
            players
        )  # ensure random order, though set should already do that
        if len(players) != num_players:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write('{"error":"Duplicate player names"}'.encode("utf-8"))
            return

        computedData = get_player_info(players, variant)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(computedData).encode("utf-8"))
        return


# get_role_descriptions - this is called when information files are generated.
def get_role_description(role, variant = "thavalon"):
    return {
        "Tristan": "The person you see is also Good and is aware that you are Good.\nYou and Iseult are collectively a valid Assassination target." + ("\nYou and Iseult will receive immunity from assassination if you correctly identify the Jealous Ex at the end of the game.\nYou appear to the Jealous Ex." if variant == "jealousy" else ""),
        "Iseult": "The person you see is also Good and is aware that you are Good.\nYou and Tristan are collectively a valid Assassination target." + ("\nYou and Tristan will receive immunity from assassination if they correctly identify the Jealous Ex at the end of the game.\nYou appear to the Jealous Ex." if variant == "jealousy" else ""),
        "Merlin": "You know which people have Evil roles, but not who has any specific role.\nYou are a valid Assassination target.",
        "Percival": "You know which people have the Merlin or Morgana roles, but not specifically who has each.",
        "Lancelot": "You may play Reversal cards while on missions.\nYou appear Evil to Merlin.",
        "Arthur": "You know which Good roles are in the game, but not who has any given role.\nIf two missions have Failed, and less than two missions have Succeeded, you may declare as Arthur.\nAfter declaring, your vote on team proposals is counted twice, but you are unable to be on mission teams until the 5th mission.\nAfter declaring, you are immune to any effect that can forcibly change your vote.",
        "Titania": "You appear as Evil to all players with Evil roles (except Colgrevance).",
        "Nimue": "You know which Good and Evil roles are in the game, but not who has any given role.\nYou are a valid Assassination target.",
        "Mordred": "You are hidden from all Good Information roles. \nLike other Evil characters, you know who else is Evil (except Colgrevance).",
        "Morgana": "You appear like Merlin to Percival. \nLike other Evil characters, you know who else is Evil (except Colgrevance).",
        "Maelagant": "You may play Reversal cards while on missions. \nLike other Evil characters, you know who else is Evil (except Colgrevance).",
        "Agravaine": "You must play Fail cards while on missions. \nIf you are on a mission that Succeeds, you may declare as Agravaine to cause it to Fail instead. \nLike other Evil characters, you know who else is Evil (except Colgrevance).",
        "Colgrevance": "You know not only who else is Evil, but what role each other Evil player possess. \nEvil players know that there is a Colgrevance, but do not know that it is you.",
        "Jealous Ex": "You see either Iseult (if there are two lovers) or the Older Sibling (if there are no lovers).\nIf Tristan correctly identifies you at the end of the game, Tristan and Iseult will receive immunity from assassination.",
        "Older Sibling": "You appear to the Jealous Ex as Iseult. You know there are no lovers in this game."
    }.get(role, "ERROR: No description available.")


# get_role_information: this is called to populate information files
# blank roles:
# - Lancelot: no information
# - Arthur: no information?
# - Guinevere: too complicated to generate here
# - Colgrevance: name,role (evil has an update later to inform them about the presence of a Colgrevance)
def get_role_information(my_player, players):
    other_evils = [
        "{} is Evil.".format(player.name)
        for player in players
        if (
            player.team is "Evil"
            and player is not my_player
            and player.role is not "Colgrevance"
        )
        or player.role is "Titania"
    ]

    return {
        "Tristan": [
            "{} is Iseult.".format(player.name)
            for player in players
            if player.role is "Iseult"
        ],
        "Iseult": [
            "{} is Tristan.".format(player.name)
            for player in players
            if player.role is "Tristan"
        ],
        "Merlin": [
            "{} is Evil.".format(player.name)
            for player in players
            if (
                (player.team is "Evil" and player.role is not "Mordred")
                or player.role is "Lancelot"
            )
        ],
        "Percival": [
            "{} is Merlin or Morgana.".format(player.name)
            for player in players
            if player.role is "Merlin" or player.role is "Morgana"
        ],
        "Lancelot": [],
        "Arthur": [
            "{}".format(player.role)
            for player in players
            if player.team is "Good" and player.role is not "Arthur"
        ],
        "Titania": [],
        "Nimue": [
            "{}".format(player.role) for player in players if player.role is not "Nimue"
        ],
        "Mordred": other_evils,
        "Morgana": other_evils,
        "Maelagant": other_evils,
        "Agravaine": other_evils,
        "Colgrevance": [
            "{} is {}".format(player.name, player.role)
            for player in players
            if player.team is "Evil" and player is not my_player
        ],
        "Jealous Ex": other_evils,
        "Older Sibling": [],
    }.get(my_player.role, [])


class Player:
    # players have the following traits
    # name: the name of the player as fed into system arguments
    # role: the role the player possesses
    # team: whether hte player is good or evil
    # type: information or ability
    # seen: a list of what they will see
    # modifier: the random modifier this player has [NOT CURRENTLY UTILIZED]
    def __init__(self, name):
        self.name = name
        self.role = None
        self.team = None
        self.modifier = None
        self.info = []
        self.is_assassin = False

    def set_role(self, role):
        self.role = role

    def set_team(self, team):
        self.team = team

    def add_info(self, info):
        self.info += info

    def generate_info(self, players):
        pass


def get_player_info(player_names, variant = "thavalon"):
    num_players = len(player_names)

    # create player objects
    players = []
    for i in range(0, len(player_names)):
        player = Player(player_names[i])
        players.append(player)

    # number of good and evil roles
    print("Here is the number of players: ", num_players)
    if num_players < 7:
        num_evil = 2
    elif num_players < 10:
        num_evil = 3
    else:
        num_evil = 4
    num_good = num_players - num_evil

    # establish available roles
    good_roles = ["Merlin", "Percival", "Tristan", "Iseult", "Lancelot"]
    evil_roles = ["Mordred", "Morgana", "Maelagant"]

    # additional roles for player-count
    # 5 only
    if num_players < 6:
        good_roles.append("Nimue")

    # 6 plus
    if variant == "jealousy" and num_players > 5:
        good_roles.append("Older Sibling")
        evil_roles.append("Jealous Ex")

    # 7 plus
    if num_players > 6:
        good_roles.append("Arthur")
        good_roles.append("Titania")

    # 8 plus
    if num_players > 7:
        evil_roles.append("Agravaine")

    # 10 only
    if num_players == 10:
        evil_roles.append("Colgrevance")

    """
	code for testing role interaction
	if num_players == 2:
		good_roles = ['Merlin']
		evil_roles = ['Maeve']
		num_good = 1
		num_evil = 1
	"""
    good_roles_in_game = random.sample(good_roles, num_good)
    evil_roles_in_game = random.sample(evil_roles, num_evil)

    # if we took both lovers and the older sibling:
    # - we must remove the older sibling and add another role, or
    # - remove both lovers and add two other roles
    if (
        sum(gr in ["Tristan", "Iseult", "Older Sibling"] for gr in good_roles_in_game) == 3
        and num_good > 1
    ):
        available_roles = (
            set(good_roles) - set(good_roles_in_game) - set(["Tristan", "Iseult", "Older Sibling"])
        )
        if len(available_roles) < 2:
            good_roles_in_game.remove("Older Sibling")
            good_roles_in_game.append(random.sample(available_roles, 1)[0])
        else:
            if random.choice([True, False]):
                good_roles_in_game.remove("Tristan")
                good_roles_in_game.remove("Iseult")
                roll_one = random.sample(set(available_roles), 1)[0]
                good_roles_in_game.append(roll_one)
                available_roles.remove(roll_one)
                good_roles_in_game.append(random.sample(set(available_roles), 1)[0])
            else:
                good_roles_in_game.remove("Older Sibling")
                good_roles_in_game.append(random.sample(set(available_roles), 1)[0])

    # if we took one lover and the older sibling:
    # - we must remove the older sibling and replace with the other lover, or
    # - remove the lone lover and add another role
    if (
        sum(gr in ["Tristan", "Iseult"] for gr in good_roles_in_game) == 1
        and "Older Sibling" in good_roles_in_game
        and num_good > 1
    ):
        available_roles = (
            set(good_roles) - set(good_roles_in_game) - set(["Tristan", "Iseult", "Older Sibling"])
        )
        if random.choice([True, False]):
            good_roles_in_game.remove("Older Sibling")
            if "Tristan" in good_roles_in_game:
                good_roles_in_game.append("Iseult")
            if "Iseult" in good_roles_in_game:
                good_roles_in_game.append("Tristan")
        else:
            if "Tristan" in good_roles_in_game:
                good_roles_in_game.remove("Tristan")
            if "Iseult" in good_roles_in_game:
                good_roles_in_game.remove("Iseult")
            good_roles_in_game.append(random.sample(set(available_roles), 1)[0])

    # if we took one lover and not the older sibling:
    # the lone lovers are rerolled
    # 50% chance to reroll lone lover
    # 50% chance to reroll another role into a lover
    if (
        sum(gr in ["Tristan", "Iseult"] for gr in good_roles_in_game) == 1
        and "Older Sibling" not in good_roles_in_game
        and num_good > 1
    ):
        if "Tristan" in good_roles_in_game:
            good_roles_in_game.remove("Tristan")
        if "Iseult" in good_roles_in_game:
            good_roles_in_game.remove("Iseult")

        # if there are no good roles left, we need to add in a lover
        available_roles = (
            set(good_roles) - set(good_roles_in_game) - set(["Tristan", "Iseult", "Older Sibling"])
        )

        if random.choice([True, False]) and available_roles:
            # replacing the lone lover
            good_roles_in_game.append(random.sample(set(available_roles), 1)[0])
        else:
            # upgrading to pair of lovers
            rerolled = random.choice(good_roles_in_game)
            good_roles_in_game.remove(rerolled)
            good_roles_in_game.append("Tristan")
            good_roles_in_game.append("Iseult")

    # if we took no lovers and not the older sibling:
    # we must replace one role with a new role
    # if there are not enough roles to replace, we remove the older sibling and one other role,
    # and add the lovers
    if (
        sum(gr in ["Tristan", "Iseult"] for gr in good_roles_in_game) == 0
        and "Older Sibling" not in good_roles_in_game
        and num_good > 1
    ):
        available_roles = (
            set(good_roles) - set(good_roles_in_game) - set(["Tristan", "Iseult", "Older Sibling"])
        )
        if len(available_roles) == 0:
            good_roles_in_game.remove("Older Sibling")
            good_roles_in_game.append("Tristan")
            good_roles_in_game.append("Iseult")
        else:
            rerolled = random.choice(good_roles_in_game)
            good_roles_in_game.remove(rerolled)
            good_roles_in_game.append(random.sample(set(available_roles), 1)[0])
    

    # roles after validation
    # print(good_roles_in_game)
    # print(evil_roles_in_game)

    # role assignment
    random.shuffle(players)

    good_players = players[:num_good]
    evil_players = players[num_good:]

    player_of_role = dict()

    for gp in good_players:
        new_role = good_roles_in_game.pop()
        gp.set_role(new_role)
        gp.set_team("Good")
        player_of_role[new_role] = gp

    # if there is at least one evil, first evil player becomes assassin
    if len(evil_players) > 0:
        evil_players[0].is_assassin = True

    for ep in evil_players:
        new_role = evil_roles_in_game.pop()
        ep.set_role(new_role)
        ep.set_team("Evil")
        player_of_role[new_role] = ep

    for p in players:
        p.add_info(get_role_information(p, players))
        random.shuffle(p.info)
        # print(p.name,p.role,p.team,p.info)

    # Informing Evil about a Colgrevance
    for ep in evil_players:
        if ep.role != "Colgrevance" and player_of_role.get("Colgrevance"):
            ep.add_info(
                [
                    "Colgrevance lurks in the shadows. (There is another Evil that you do not see.)"
                ]
            )
        if ep.role is not "Colgrevance" and player_of_role.get("Titania"):
            ep.add_info(
                [
                    "Titania has infiltrated your ranks. (One of the people you see is not Evil.)"
                ]
            )
        if ep.role == "Jealous Ex":
            ep.add_info(
                [
                    "{} is Iseult or the Older Sibling.".format(player.name)
                        for player in players
                        if player.role == "Iseult" or player.role == "Older Sibling"
                ]
            )
        if ep.is_assassin:
            ep.add_info(["You are the Assassin."])

    bar = "----------------------------------------\n"
    data = {}
    for player in players:
        player.string = (
            bar
            + "You are "
            + ("the " if player.role == "Jealous Ex" or player.role == "Older Sibling" else "")
            + player.role
            + " ["
            + player.team
            + "]\n"
            + bar
            + get_role_description(player.role, variant)
            + "\n"
            + bar
            + "\n".join(player.info)
            + "\n"
            + bar
        )
        data[player.name] = player.string

    first_player = random.sample(players, 1)[0]
    data["start"] = "The player proposing the first mission is {}.".format(
        first_player.name
    )

    data["doNotOpen"] = (
        "Player -> Role\n\nGOOD TEAM:\n"
        + "\n".join(["{} -> {}".format(gp.name, gp.role) for gp in good_players])
        + "\n\nEVIL TEAM:\n"
        + "\n".join(["{} -> {}".format(ep.name, ep.role) for ep in evil_players])
    )

    data["players"] = [p.name for p in players]
    return data


def main():
    players = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"]
    num_players = len(players)
    if not (5 <= num_players <= 10):
        raise "Invalid number of players"

    players = set(players)  # use as set to avoid duplicate players
    players = list(players)  # convert to list
    random.shuffle(
        players
    )  # ensure random order, though set should already do that
    if len(players) != num_players:
        raise "Duplicate player names"

    computedData = get_player_info(players)
    print(computedData["doNotOpen"])
    for player in players:
        print(computedData[player])

# uncomment to run the main function for testing
# please leave commented out when deploying
# main()