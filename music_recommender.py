"""
Music Recommendation Module
Famous Indian & Pakistani songs matched to user mood/emotion.
"""
import random

# ───────────────────────────────────────────────────────────────
#  SONG DATABASE  –  format: (Artist, Song Title, Year)
# ───────────────────────────────────────────────────────────────
MOOD_SONGS = {

    "happy": [
        ("Atif Aslam",              "Dillagi",                        2016),
        ("Arijit Singh",            "Tum Hi Ho",                      2013),
        ("Shreya Ghoshal",          "Teri Meri",                      2010),
        ("A.R. Rahman",             "Jai Ho",                         2008),
        ("Rahat Fateh Ali Khan",    "O Re Piya",                      2007),
        ("Shankar Mahadevan",       "Breathless",                     1998),
        ("Kishore Kumar",           "Ek Ladki Ko Dekha",              1994),
        ("Mohammed Rafi",           "Aaj Mausam Bada Beimaan Hai",    1973),
        ("Lata Mangeshkar",         "Ajeeb Dastan Hai Yeh",           1960),
        ("Nusrat Fateh Ali Khan",   "Mustt Mustt",                    1990),
        ("Ali Zafar",               "Channo",                         2011),
        ("Strings",                 "Anjane",                         2003),
        ("Coke Studio",             "Afreen Afreen",                  2016),
        ("Junoon",                  "Sayonee",                        1996),
        ("Abrar Ul Haq",            "Billo De Ghar",                  1995),
    ],

    "sad": [
        ("Atif Aslam",              "Aadat",                          2004),
        ("Arijit Singh",            "Channa Mereya",                  2016),
        ("Rahat Fateh Ali Khan",    "Zaroori Tha",                    2014),
        ("KK",                      "Tadap Tadap",                    1999),
        ("Lata Mangeshkar",         "Lag Ja Gale",                    1964),
        ("Nusrat Fateh Ali Khan",   "Tumhe Dillagi",                  1997),
        ("Shafqat Amanat Ali",      "Aadat",                          2005),
        ("Shreya Ghoshal",          "Sun Raha Hai",                   2013),
        ("Ustad Nusrat",            "Allah Meherban",                 1994),
        ("Kishore Kumar",           "Rote Huye Aate Hain Sab",        1978),
        ("Mehdi Hassan",            "Ranjish Hi Sahi",                1977),
        ("Coke Studio",             "Kattey",                         2014),
        ("A.R. Rahman",             "Tere Bina",                      2007),
        ("Hadiqa Kiani",            "Woh Lamhe",                      2004),
        ("Sonu Nigam",              "Abhi Mujh Mein Kahin",           2011),
    ],

    "angry": [
        ("Bohemia",                 "Ek Second",                      2012),
        ("Yo Yo Honey Singh",       "Angreji Beat",                   2012),
        ("Badshah",                 "DJ Wale Babu",                   2015),
        ("Raftaar",                 "Swag Mera Desi",                 2016),
        ("Bilal Saeed",             "12 Saal",                        2012),
        ("Diljit Dosanjh",          "Proper Patola",                  2016),
        ("Guru Randhawa",           "Lahore",                         2017),
        ("AP Dhillon",              "Brown Munde",                    2020),
        ("Bohemia",                 "Kali Denali",                    2011),
        ("Young Stunners",          "Ghabrana Nahi Hai",              2020),
        ("Talha Anjum",             "Asim Bhai",                      2021),
        ("Faris Shafi",             "Game Over",                      2019),
        ("Imran Khan",              "Amplifier",                      2009),
        ("AR Rahman",               "Rang De Basanti",                2006),
        ("Shankar Ehsaan Loy",      "Rock On",                        2008),
    ],

    "relaxed": [
        ("Nusrat Fateh Ali Khan",   "Allah Hoo",                      1991),
        ("Rahat Fateh Ali Khan",    "Sajda",                          2010),
        ("Ustad Nusrat",            "Yeh Jo Halka Halka Suroor Hai",  1981),
        ("Mehdi Hassan",            "Gulon Mein Rang Bhare",          1979),
        ("Coke Studio",             "Pasoori",                        2022),
        ("Strings",                 "Duur",                           2003),
        ("Atif Aslam",              "Jal Pari",                       2011),
        ("A.R. Rahman",             "O Saya",                         2008),
        ("Lata Mangeshkar",         "Bahut Pyar Karte Hain",          1992),
        ("Abida Parveen",           "Tere Ishq Mein",                 1995),
        ("Ali Sethi",               "Rung",                           2022),
        ("Hadiqa Kiani",            "Boohey Barian",                  1994),
        ("Ustad Rahat",             "Teri Meri Pehchan",              2012),
        ("Farida Khanum",           "Aaj Jane Ki Zidd Na Karo",       1991),
        ("Kishore Kumar",           "Mere Sapnon Ki Rani",            1969),
    ],

    "stressed": [
        ("Atif Aslam",              "Wo Lamhe",                       2006),
        ("Arijit Singh",            "Phir Bhi Tumko Chaahunga",       2017),
        ("Sonu Nigam",              "Sandese Aate Hain",              1997),
        ("Shafqat Amanat Ali",      "Mitwa",                          2006),
        ("Coke Studio",             "Tu Kuja Man Kuja",               2013),
        ("Nusrat Fateh Ali Khan",   "Dam Mast Qalandar",              1990),
        ("Noori",                   "Manwa Re",                       2003),
        ("Junoon",                  "Mahi Ve",                        1999),
        ("Vital Signs",             "Dil Dil Pakistan",               1987),
        ("EP (Entity Paradigm)",    "Andhairon Mein",                 2002),
        ("Overload",                "Suno Ke Mein Hoon Jawan",        2004),
        ("Sajjad Ali",              "Baat Karo",                      2000),
        ("Strings",                 "Na Jane Kyon",                   2003),
        ("Ali Azmat",               "Garaj Baras",                    2004),
        ("Aaroh",                   "Ik Pal",                         2003),
    ],

    "neutral": [
        ("Coke Studio",             "Pasoori",                        2022),
        ("Ali Sethi & Shae Gill",   "Pasoori",                        2022),
        ("Aima Baig",               "Kalabaaz Dil",                   2018),
        ("Momina Mustehsan",        "Afreen Afreen (Coke Studio)",    2016),
        ("Bilal Khan",              "Bachana",                        2011),
        ("Farhan Saeed",            "Roiyaan",                        2014),
        ("Mustafa Zahid",           "Teri Yaad",                      2008),
        ("Sajjad Ali",              "Aaqa",                           2002),
        ("Ustad Nusrat",            "Kinna Sohna",                    1994),
        ("Ghulam Ali",              "Chupke Chupke",                  1977),
        ("A.R. Rahman",             "Kun Faya Kun",                   2011),
        ("Shreya Ghoshal",          "Sunn Raha Hai",                  2012),
        ("Mohit Chauhan",           "Tum Se Hi",                      2008),
        ("KK",                      "Yaaron",                         1999),
        ("Lucky Ali",               "O Sanam",                        1996),
    ],

    "fear": [
        ("Junoon",                  "Khwaab",                         1999),
        ("EP",                      "Andhairon Mein",                 2002),
        ("Noori",                   "Mujhay Dou",                     2006),
        ("Fuzon",                   "Ankhon Ko",                      2004),
        ("Aaroh",                   "Jala Do",                        2003),
        ("Mekaal Hassan Band",      "Roshni",                         2010),
        ("Lata Mangeshkar",         "Tere Bina Zindagi",              1977),
        ("Kishore Kumar",           "Aa Chal Ke Tujhe",               1970),
        ("Mehdi Hassan",            "Zindagi Mein Toh Sabhi",         1980),
        ("Nusrat Fateh Ali Khan",   "Mere Rashke Qamar",             1988),
    ],

    "disgust": [
        ("Bohemia",                 "Tenu Leke",                      2006),
        ("Young Stunners",          "Waapas",                         2021),
        ("Raftaar",                 "Bura Na Mano Holi Hai",          2019),
        ("Yo Yo Honey Singh",       "Blue Eyes",                      2013),
        ("Badshah",                 "Kar Gayi Chull",                 2016),
        ("Bilal Saeed",             "Baaki Sab Theek Hai",            2017),
        ("Diljit Dosanjh",          "Do You Know",                    2016),
        ("AP Dhillon",              "Excuses",                        2020),
        ("Imran Khan",              "Ni Nachleh",                     2015),
        ("Ali Zafar",               "Rockstar",                       2013),
    ],
}


def get_song_recommendation(emotion: str, count: int = 3) -> list[dict]:
    """
    Return `count` random famous songs matching the given emotion.
    Each item: { artist, title, year }
    """
    emotion = emotion.lower()
    songs = MOOD_SONGS.get(emotion, MOOD_SONGS["neutral"])
    picks = random.sample(songs, min(count, len(songs)))
    return [{"artist": a, "title": t, "year": y} for a, t, y in picks]
