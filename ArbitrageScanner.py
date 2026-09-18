import os
import requests

def calculate_stakes(total_bankroll, odds_a, odds_b):
    implied_prob = (1 / odds_a) + (1 / odds_b)
    stake_a = (total_bankroll * (1 / odds_a)) / implied_prob
    stake_b = total_bankroll - stake_a
    total_payout = stake_a * odds_a
    profit = total_payout - total_bankroll
    return round(stake_a, 2), round(stake_b, 2), round(total_payout, 2), round(profit, 2)

def to_american(decimal_odds):
    if decimal_odds >= 2.0:
        val = round((decimal_odds - 1) * 100)
        return f"+{val}"
    else:
        val = round(-100 / (decimal_odds - 1))
        return f"{val}"


api_key = "67731391cb78a25b7c7089e4ecb0b15c"
sport = "baseball_mlb"
markets_to_scan = "h2h,spreads,totals"
url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={api_key}&regions=us&markets={markets_to_scan}"

response = requests.get(url)
games = response.json()

# Handle potential API errors or bad key responses
if isinstance(games, dict) and "message" in games:
    print(f"API Error: {games['message']}")
    exit()

print(f"Scanning {len(games)} games across {markets_to_scan}...\n")

arbs_found = 0

for game in games:
    match_title = f"{game['home_team']} vs {game['away_team']}"

    # Structure: market_groups[market_key][line_threshold] = { side_identifier: {price, book} }
    # Example: market_groups["totals"][8.5]["Over"] = {"price": 1.95, "book": "DraftKings"}
    market_groups = {}

    for book in game.get("bookmakers", []):
        book_title = book["title"]

        for market in book.get("markets", []):
            mkey = market["key"]
            outcomes = market.get("outcomes", [])
            if len(outcomes) < 2:
                continue

            if mkey not in market_groups:
                market_groups[mkey] = {}

            if mkey == "h2h":
                line_id = "moneyline"
                if line_id not in market_groups[mkey]:
                    market_groups[mkey][line_id] = {}

                for outcome in outcomes:
                    team = outcome["name"]
                    price = outcome["price"]
                    current = market_groups[mkey][line_id].get(team)
                    if not current or price > current["price"]:
                        market_groups[mkey][line_id][team] = {"price": price, "book": book_title}

            elif mkey == "totals":
                for outcome in outcomes:
                    point = outcome.get("point")
                    side = outcome["name"]  # "Over" or "Under"
                    price = outcome["price"]

                    if point not in market_groups[mkey]:
                        market_groups[mkey][point] = {}

                    current = market_groups[mkey][point].get(side)
                    if not current or price > current["price"]:
                        market_groups[mkey][point][side] = {"price": price, "book": book_title}

            elif mkey == "spreads":
                # For spreads, pair by the absolute line spread (e.g., 1.5)
                # Team A (-1.5) pairs against Team B (+1.5)
                for outcome in outcomes:
                    team = outcome["name"]
                    point = outcome.get("point")
                    price = outcome["price"]
                    abs_line = abs(point)

                    if abs_line not in market_groups[mkey]:
                        market_groups[mkey][abs_line] = {}

                    # Key by team and sign, e.g., "Dodgers (-1.5)"
                    side_label = f"{team} ({point:+g})"

                    current = market_groups[mkey][abs_line].get(side_label)
                    if not current or price > current["price"]:
                        market_groups[mkey][abs_line][side_label] = {"price": price, "book": book_title}

    # Evaluate the grouped pairs
    for mkey, lines in market_groups.items():
        for line_id, sides in lines.items():
            # A valid market pair must have exactly 2 opposing sides
            if len(sides) == 2:
                legs = list(sides.keys())
                leg_1, leg_2 = legs[0], legs[1]

                price_1 = sides[leg_1]["price"]
                book_1 = sides[leg_1]["book"]

                price_2 = sides[leg_2]["price"]
                book_2 = sides[leg_2]["book"]

                # Ensure we aren't pairing two favorites or two underdogs in spreads
                implied_prob = (1 / price_1) + (1 / price_2)

                if implied_prob < 1.0:
                    arbs_found += 1
                    margin = (1 - implied_prob) * 100

                    # Calculate order sizing based on a $1,000 operational allocation
                    bankroll = 1000
                    stake_1, stake_2, payout, net_profit = calculate_stakes(bankroll, price_1, price_2)

                    print(f"=== [{mkey.upper()}] ARBITRAGE DETECTED ===")
                    print(f"Match: {match_title}")
                    print(f"Line Target: {line_id}")
                    print(f"Leg 1: {leg_1} @ {book_1} ({to_american(price_1)}) | Order: ${stake_1}")
                    print(f"Leg 2: {leg_2} @ {book_2} ({to_american(price_2)}) | Order: ${stake_2}")
                    print(f"Capital: ${bankroll} -> Payout: ${payout} | Guaranteed Profit: ${net_profit} ({margin:.2f}%)\n")


if arbs_found == 0:
    print("Scan complete. No active arbitrage margins detected across requested markets.")
else:
    print(f"Scan complete. Total opportunities identified: {arbs_found}")