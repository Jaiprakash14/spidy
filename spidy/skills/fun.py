"""Fun - jokes & light replies. All local, no APIs."""
import random

_JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I would tell you a UDP joke, but you might not get it.",
    "There are 10 types of people in the world — those who understand binary and those who don't.",
    "Why did the developer go broke? Because he used up all his cache.",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
    "Why do Java developers wear glasses? Because they don't C#.",
    "I told my computer I needed a break — it froze.",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
    "I'd tell you a joke about HTTP, but you'd only get a 404.",
    "Debugging: being the detective in a crime movie where you're also the murderer.",
]

_GREETINGS = [
    "Hey there, ready when you are.",
    "Hi! What are we tackling today?",
    "Hello, at your service.",
    "Yo. Say the word.",
]

_THANKS = [
    "Anytime.",
    "Happy to help.",
    "You got it.",
    "No worries.",
]

_BYES = [
    "See you around.",
    "Later!",
    "Signing off. I'll keep an eye on your reminders.",
    "Bye. Say 'Hey Spidy' whenever you need me.",
]


def joke() -> str:
    return random.choice(_JOKES)


def greeting() -> str:
    return random.choice(_GREETINGS)


def thanks() -> str:
    return random.choice(_THANKS)


def goodbye() -> str:
    return random.choice(_BYES)
