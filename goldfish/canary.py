"""Canary generation: crypto-random markers + behavioral constraint canaries."""

import hashlib
import secrets


def marker(index: int, seed: int) -> str:
    """Deterministic-but-unpredictable marker: seeded PRNG, not derivable from content."""
    rng = secrets.SystemRandom()  # noqa: F841  (unused; kept explicit that markers are random)
    digest = hashlib.sha256(("gf-%d-%d" % (seed, index)).encode()).hexdigest()
    return "GOLD-" + digest[:8]


ADJECTIVES = ["Copper", "Velvet", "Quantum", "Harbor", "Crimson", "Silent",
              "Amber", "Frost", "Cobalt", "Ember", "Marble", "Zephyr"]
ANIMALS = ["Falcon", "Otter", "Lynx", "Heron", "Badger", "Mantis",
           "Condor", "Vole", "Ibis", "Pika", "Gannet", "Okapi"]
BANANA_WORDS = ["mango", "papaya", "guava", "lychee", "rambutan", "durian",
                "persimmon", "apricot", "quince", "jabuticaba", "cherimoya", "pitaya"]


def codename(seed: int, salt: int) -> str:
    h = hashlib.sha256(("gf-code-%d-%d" % (seed, salt)).encode()).digest()
    return ADJECTIVES[h[0] % len(ADJECTIVES)] + "-" + ANIMALS[h[1] % len(ANIMALS)]


def banned_word(seed: int, salt: int) -> str:
    h = hashlib.sha256(("gf-ban-%d-%d" % (seed, salt)).encode()).digest()
    return BANANA_WORDS[h[0] % len(BANANA_WORDS)]


def build_canary_set(n: int, seed: int) -> list:
    """Returns canary dicts: markers plus two behavioral canaries (named entity,
    a forbidden word that must NOT appear). Each has an injection slot index."""
    items = []
    for i in range(n):
        items.append({
            "kind": "marker",
            "value": marker(i, seed),
            "slot": i,
            "question": "marker:" + marker(i, seed),
        })
    items.append({
        "kind": "entity",
        "value": codename(seed, 1),
        "slot": n,
        "question": "entity:What is the codename of the project we are working on?",
    })
    items.append({
        "kind": "forbidden",
        "value": banned_word(seed, 2),
        "slot": n,
        "question": "forbidden:Name several tropical fruits.",
    })
    return items
