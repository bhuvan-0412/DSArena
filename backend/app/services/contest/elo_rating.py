from typing import Tuple

class EloRatingService:
    """
    Elo Rating Calculator for DSArena Timed Coding Contests.
    Ranks:
    - < 1200: Beginner
    - 1200 - 1399: Novice
    - 1400 - 1599: Apprentice
    - 1600 - 1799: Specialist
    - 1800 - 1999: Expert
    - 2000 - 2199: Candidate Master
    - 2200 - 2399: Master
    - 2400 - 2599: Grandmaster
    - 2600+: Legend
    """

    @staticmethod
    def get_rank_title(rating: int) -> str:
        if rating < 1200: return "Beginner"
        elif rating < 1400: return "Novice"
        elif rating < 1600: return "Apprentice"
        elif rating < 1800: return "Specialist"
        elif rating < 2000: return "Expert"
        elif rating < 2200: return "Candidate Master"
        elif rating < 2400: return "Master"
        elif rating < 2600: return "Grandmaster"
        else: return "Legend"

    @staticmethod
    def calculate_rating_change(current_rating: int, user_rank: int, total_participants: int) -> Tuple[int, int, str]:
        # K-factor weighting
        k_factor = 32
        expected_rank = max(1, (total_participants + 1) // 2)

        # Delta based on actual vs expected performance
        if user_rank <= expected_rank:
            performance_ratio = (expected_rank - user_rank + 1) / max(1, expected_rank)
            delta = int(k_factor * (1 + performance_ratio))
        else:
            performance_ratio = (user_rank - expected_rank) / max(1, total_participants - expected_rank)
            delta = -int(k_factor * performance_ratio)

        new_rating = max(800, current_rating + delta)
        new_title = EloRatingService.get_rank_title(new_rating)
        return new_rating, delta, new_title
