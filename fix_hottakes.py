import csv

SYNTHETIC_HOT_TAKES = [
    "LeBron is not and has never been better than Jordan. End of discussion.",
    "Kobe was more clutch than anyone in NBA history and it's not even close.",
    "The Warriors dynasty is the most fraudulent championship run ever. KD ruined basketball.",
    "Luka Doncic is lazy and will never win a championship because of it.",
    "Kyrie Irving is the most skilled player to ever play the game, full stop.",
    "The Celtics are the most overrated franchise in NBA history and their fans are insufferable.",
    "Westbrook was never a good basketball player. Just an empty stats guy.",
    "Nikola Jokic does not deserve a single MVP. The voters have lost their minds.",
    "The NBA is rigged for big market teams. There is zero doubt about this.",
    "Carmelo Anthony is a top 10 player all time and everyone is wrong about him.",
    "Trae Young will never win anything meaningful. Too small, too selfish.",
    "The 2017 Warriors would destroy any team in NBA history and it would not be competitive.",
    "Anthony Davis is soft and will never be the best player on a championship team.",
    "Point guard is the most overvalued position in the modern NBA by a mile.",
    "Giannis only looks good because of how weak the Eastern Conference is.",
    "The three point revolution ruined basketball. The league is unwatchable now.",
    "Pat Riley is the most overrated coach and executive in NBA history.",
    "Zion Williamson does not care about basketball and never will.",
    "The Spurs dynasty only happened because they tanked and got lucky with Tim Duncan.",
    "Damian Lillard wasted his prime crying about wanting a trade instead of winning.",
    "Stephen Curry cannot be the GOAT because he cannot create off the dribble consistently.",
    "Load management is destroying the NBA. These guys are just not mentally tough.",
    "Kevin Durant has no loyalty and that disqualifies him from any GOAT conversation.",
    "Victor Wembanyama is going to be a bust. The hype is completely out of control.",
    "The Knicks will never win a championship as long as James Dolan owns the team.",
    "Chris Paul choked in every series that actually mattered. The stats do not lie.",
    "European players have made the NBA soft. The physicality of the 90s was better.",
    "James Harden quit on every single team he was ever on. Worst competitor in the league.",
    "The modern NBA player could not survive a week in the 1990s playoffs.",
    "Jayson Tatum is not a top 5 player and Celtics fans have completely lost the plot.",
    "Dwyane Wade only won because of LeBron and Shaq. His legacy is built on other people.",
    "The league office actively protects star players from foul calls and always has.",
    "Russell Westbrook is the worst max contract player in NBA history, no competition.",
    "Scottie Pippen would have been nothing without Jordan and everyone knows it.",
    "The Nets superteam failure is the most embarrassing front office disaster ever.",
    "Refs in the NBA finals are absolutely deciding the outcomes of games on purpose.",
    "Devin Booker is good in the regular season but mentally weak when it counts.",
    "Jimmy Butler is the most overrated two-way player in the league right now.",
    "The Thunder were right to blow it up. Harden and Westbrook were never winning anything.",
    "Ben Simmons is the biggest bust in NBA draft history and nothing will change that.",
    "Kawhi Leonard only looks like a GOAT candidate because he plays 40 games a year.",
    "Paul George does not show up in big moments. It is a documented fact at this point.",
    "The Suns will never win a chip with that ownership and that culture. Never.",
    "College basketball is meaningless for predicting NBA success. Stop watching it.",
    "Shaquille O'Neal would average 45 points a game in today's NBA with no effort.",
    "The draft lottery should be abolished. It just rewards bad management.",
    "Ja Morant is going to flame out before he wins anything significant.",
    "Magic Johnson is the most overrated Laker of all time and the revisionism is insane.",
    "Charles Barkley was never a champion because he was never actually the best player.",
    "The Eastern Conference has been a joke for 15 years and nobody wants to admit it.",
    "Bradley Beal signed the worst contract in NBA history and he knew exactly what he was doing.",
    "The 1986 Celtics would beat this generation's best team in 5 games.",
    "Playoff seeding should be redone completely. The current format makes no sense.",
]

rows = [{"text": t, "label": "hot_take", "notes": "synthetic"} for t in SYNTHETIC_HOT_TAKES]

with open("dataset.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["text", "label", "notes"])
    writer.writerows(rows)

print(f"Appended {len(rows)} synthetic hot_takes.")

# Verify final counts
import pandas as pd
df = pd.read_csv("dataset.csv")
print(df["label"].value_counts())
print("Total:", len(df))
