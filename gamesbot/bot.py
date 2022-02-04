import discord
from discord import player
from xoxo_game import Game
import json

TOKEN = 'token here'
client = discord.Client()

class GameClient(object):
    game_id = None
    slots_left = []
    turn = True
    game = None

    player1 = None
    player2 = None

    leaderboard = None

    def __init__(self):
        self.game_id = None
        self.slots_left = [1,2,3,4,5,6,7,8,9]
        self.turn = True
        self.game = Game()
        self.player1 = None
        self.player2 = None

        self.leaderboard = None
    
    def curr_turn(self):
        if self.turn:
            return "X"
        else:
            return "O"
        
    def next_turn(self):
        if self.turn:
            self.turn = False
        else:
            self.turn = True
    
    def restart_game(self):
        self.game_id = None
        self.slots_left = [1,2,3,4,5,6,7,8,9]
        self.turn = True
        self.game = Game()

        self.player1 = None
        self.player2 = None
    
    def can_start(self):
        return bool(self.player1 and self.player2)

    def save_leaderboard(self):
        with open('leaderboard.json', 'w') as fp:
            json.dump(self.leaderboard, fp)

    def load_leaderboard(self):
        with open('leaderboard.json', 'r') as fp:
            self.leaderboard = json.load(fp)
    
    def is_playing_user(self, user):
        return (self.player1 == user or self.player2 == user)


game_client = GameClient()
game_client.load_leaderboard()

EMOJI_MAPPING = {
                        1: "1️⃣",
                        2: "2️⃣",
                        3: "3️⃣",
                        4: "4️⃣",
                        5: "5️⃣",
                        6: "6️⃣",
                        7: "7️⃣",
                        8: "8️⃣",
                        9: "9️⃣",
                        "1️⃣": 1, 
                        "2️⃣": 2,
                        "3️⃣": 3,
                        "4️⃣": 4,
                        "5️⃣": 5,
                        "6️⃣": 6,
                        "7️⃣": 7,
                        "8️⃣": 8,
                        "9️⃣": 9,
                        "🗑️": -1
                    }

EMOJI_MAPPINGV2 = {
                    1: "↖️",
                    2: "⬆️",
                    3: "↗️",
                    4: "⬅️",
                    5: "⏹️",
                    6: "➡️",
                    7: "↙️",
                    8: "⬇️",
                    9: "↘️",
                    "↖️": 1,
                    "⬆️": 2,
                    "↗️": 3,
                    "⬅️": 4,
                    "⏹️": 5,  
                    "➡️": 6,
                    "↙️": 7,
                    "⬇️": 8,
                    "↘️": 9,
                    "🗑️": -1
                    }

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_reaction_add(reaction, user):

    # Base case where bot adds stickers
    if (user.id == client.user.id):
        return None

    if reaction.message.id == game_client.game_id:

        if not game_client.can_start():
            if reaction.emoji == "❌":
                if game_client.player2 != str(user) and game_client.player1 == None:
                    game_client.player1 = str(user)
                else:
                    print(f"{user} trying to make illegal move")

            if reaction.emoji == "⭕":
                if game_client.player1 != str(user) and game_client.player2 == None:
                    game_client.player2 = str(user)
                else:
                    print(f"{user} trying to make illegal move")
            
            if reaction.emoji == "🗑️":
                if not game_client.is_playing_user(str(user)):
                    return None

                game_client.restart_game()
                await reaction.message.delete()
                return await reaction.message.channel.send(f"Game session ended by {user}")
        
            if game_client.can_start():
                game = game_client.game.board
                response = await reaction.message.channel.send(f"Current turn: {game_client.curr_turn()}\n{game}")

                for n in range(1,10):
                    await response.add_reaction(EMOJI_MAPPINGV2[n])
                await response.add_reaction("🗑️")
                # Initial starting state
                game_client.game_id = response.id

            return None

        if reaction.emoji in EMOJI_MAPPINGV2.keys():
            
            if reaction.emoji == "🗑️":
                if not game_client.is_playing_user(str(user)):
                    return None
                game_client.restart_game()
                await reaction.message.delete()
                return await reaction.message.channel.send(f"Game session ended by {user}")

            else:
                if game_client.curr_turn() == "X":
                    pass
                    if str(user) != game_client.player1:
                        return None
                    else:
                        print("not allowed")
                elif game_client.curr_turn() == "O":
                    if str(user) != game_client.player2:
                        return None
                    else:
                        print("not allowed")

                # Input new position and symbol
                game_client.game.input_game(game_client.curr_turn(), EMOJI_MAPPINGV2[reaction.emoji])

                # Check if winning state
                if game_client.game.end_game():
                    # Winning board
                    new_state = game_client.game.board

                    await reaction.message.delete()
                    await reaction.message.channel.send(f"{user} won!\n{new_state}")
                    
                    if str(user) in game_client.leaderboard.keys():
                        game_client.leaderboard[str(user)]['wins'] += 1
                        if game_client.curr_turn == "X":
                            game_client.leaderboard[str(user)]['wins/X'] += 1
                        else:
                            game_client.leaderboard[str(user)]['wins/O'] += 1

                        game_client.save_leaderboard()
                    else:
                        if game_client.curr_turn() == "X":
                            win_info = {str(user): {"wins": 1, "wins/X": 1, "wins/O": 0}}
                        else: 
                            win_info = {str(user): {"wins": 1, "wins/X": 0, "wins/O": 1}}

                        game_client.leaderboard.update(win_info)
                        game_client.save_leaderboard()

                    game_client.restart_game()
                    return None
                    
                # New updated board
                new_state = game_client.game.board
                # Next turn
                game_client.next_turn()
                new_state = f"Current turn: {game_client.curr_turn()}\n{new_state}"
                response = await reaction.message.channel.send(new_state)

                # Delete old gameboard
                await reaction.message.delete()
                # Remove slot from slots_left
                game_client.slots_left.remove(EMOJI_MAPPINGV2[reaction.emoji])
                
                for n in game_client.slots_left:
                    await response.add_reaction(EMOJI_MAPPINGV2[n])
                await response.add_reaction("🗑️")

                game_client.game_id = response.id

@client.event
async def on_message(message):

    VALID_GAME_NAMES = ["-game XOXO", "-game xoxo", "-game xo", "-game XO"]

    if message.content in VALID_GAME_NAMES:

        if game_client.game_id:
            return await message.channel.send("There is a game ongoing currently. Finish or discard the game to start a new one.")
        
        else:
            response = await message.channel.send(f"Pick which player you want to be:")
            await response.add_reaction("❌")
            await response.add_reaction("⭕")
            await response.add_reaction("🗑️")

            # Save prompt id
            game_client.game_id = response.id
    
    if message.content == "-game leaderboard":
        game_client.load_leaderboard()

        rankings = []
        leader_board_to_send = ""

        for key, value in game_client.leaderboard.items():
            if key != "Leaderboard":
                string = f"{leader_board_to_send}{key} stats:\ntotal wins: {value['wins']} (winsX, winsO): {(value['wins/X'], value['wins/O'])}\n\n"
                rankings.append((value['wins'], string))

        sorted_by_wins = sorted(rankings, reverse=True)

        for rank, position in enumerate(sorted_by_wins):
            leader_board_to_send = f"{leader_board_to_send}({rank+1}) {position[1]}"

        await message.channel.send(leader_board_to_send)

    if message.content == "-game clear":

        if game_client.game_id:
            message = await message.channel.fetch_message(game_client.game_id) 
            game_client.restart_game()
            await message.delete()
    
    if message.content == "-game clear leaderboard":
        # TODO
        pass

            

client.run(TOKEN)