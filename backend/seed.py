from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.user import User, XPHistory
from app.models.roadmap import Topic, Problem
from app.models.progress import UserProgress, UserTopicProgress
from app.models.achievement import Achievement, UserAchievement

def seed_db():
    # Make sure tables exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Check if topics are already seeded
        if db.query(Topic).first():
            print("Database already seeded with topics. Skipping seed.")
            return

        print("Seeding database...")

        # 1. Create Topics
        topics = [
            Topic(id="arrays", title="Arrays & Hashing", description="Master array operations, two pointer techniques, and hash map searches.", order=1, xp_reward=200),
            Topic(id="sorting", title="Sorting Algorithms", description="Understand sorting logic: bubble, selection, insertion, merge, and quicksort.", order=2, xp_reward=200),
            Topic(id="binary-search", title="Binary Search", description="Solve logarithmic search challenges on arrays and virtual search spaces.", order=3, xp_reward=200),
            Topic(id="recursion", title="Recursion & Backtracking", description="Learn divide-and-conquer, backtracking, and recursive trees.", order=4, xp_reward=200),
            Topic(id="linked-list", title="Linked Lists", description="Implement singly and doubly linked list pointer manipulations.", order=5, xp_reward=200),
            Topic(id="trees", title="Binary Trees & BST", description="Traverse and manipulate hierarchical trees, binary search trees.", order=6, xp_reward=200),
        ]
        db.add_all(topics)
        db.commit()

        # 2. Create Problems
        problems = [
            # Arrays
            Problem(
                id="two-sum",
                topic_id="arrays",
                title="Two Sum",
                difficulty="Easy",
                xp_reward=50,
                statement="Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
                examples=[
                    {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."}
                ],
                constraints=["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9"],
                hints=["Can you use a hash map to look up the complement in O(1) time?", "Track seen values and their indices."],
                external_link="https://leetcode.com/problems/two-sum/",
                expected_time_complexity="O(N)",
                expected_space_complexity="O(N)"
            ),
            Problem(
                id="valid-anagram",
                topic_id="arrays",
                title="Valid Anagram",
                difficulty="Easy",
                xp_reward=50,
                statement="Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.",
                examples=[
                    {"input": "s = \"anagram\", t = \"nagaram\"", "output": "true", "explanation": "Both s and t contain the same letters with the same counts."}
                ],
                constraints=["1 <= s.length, t.length <= 5 * 10^4", "s and t consist of lowercase English letters."],
                hints=["Count occurrences of each character in both strings.", "Are the counts identical?"],
                external_link="https://leetcode.com/problems/valid-anagram/",
                expected_time_complexity="O(N)",
                expected_space_complexity="O(1)"
            ),
            Problem(
                id="max-subarray",
                topic_id="arrays",
                title="Maximum Subarray (Kadane's)",
                difficulty="Medium",
                xp_reward=100,
                statement="Given an integer array `nums`, find the subarray with the largest sum and return its sum.",
                examples=[
                    {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6", "explanation": "The subarray [4,-1,2,1] has the largest sum = 6."}
                ],
                constraints=["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
                hints=["Try tracking the current subarray sum, resetting it to 0 if it becomes negative.", "Compare with a global max sum."],
                external_link="https://leetcode.com/problems/maximum-subarray/",
                expected_time_complexity="O(N)",
                expected_space_complexity="O(1)"
            ),

            # Sorting
            Problem(
                id="bubble-sort",
                topic_id="sorting",
                title="Bubble Sort Implementation",
                difficulty="Easy",
                xp_reward=50,
                statement="Given an array of integers, sort the array in-place in non-decreasing order using the Bubble Sort algorithm.",
                examples=[
                    {"input": "nums = [5,1,4,2,8]", "output": "[1,2,4,5,8]"}
                ],
                constraints=["1 <= nums.length <= 1000", "-10^4 <= nums[i] <= 10^4"],
                hints=["Repeatedly swap adjacent elements if they are in the wrong order.", "Optimize by stopping early if no swaps occurred during a pass."],
                external_link="https://www.geeksforgeeks.org/bubble-sort/",
                expected_time_complexity="O(N^2)",
                expected_space_complexity="O(1)"
            ),
            Problem(
                id="quick-sort",
                topic_id="sorting",
                title="Quick Sort Implementation",
                difficulty="Medium",
                xp_reward=100,
                statement="Given an array of integers, sort the array in-place using the Quick Sort algorithm. Use the last element as pivot.",
                examples=[
                    {"input": "nums = [10,7,8,9,1,5]", "output": "[1,5,7,8,9,10]"}
                ],
                constraints=["1 <= nums.length <= 5 * 10^4", "-10^5 <= nums[i] <= 10^5"],
                hints=["Choose a pivot, partition the array such that smaller elements go left and larger go right.", "Recursively sort sub-segments."],
                external_link="https://www.geeksforgeeks.org/quick-sort/",
                expected_time_complexity="O(N log N)",
                expected_space_complexity="O(log N)"
            ),

            # Binary Search
            Problem(
                id="binary-search-problem",
                topic_id="binary-search",
                title="Binary Search",
                difficulty="Easy",
                xp_reward=50,
                statement="Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`. If `target` exists, then return its index. Otherwise, return `-1`.",
                examples=[
                    {"input": "nums = [-1,0,3,5,9,12], target = 9", "output": "4", "explanation": "9 exists in nums and its index is 4"}
                ],
                constraints=["1 <= nums.length <= 10^4", "-10^4 < nums[i], target < 10^4", "All the integers in nums are unique.", "nums is sorted in ascending order."],
                hints=["Use left and right pointers to track the search space.", "Compute mid = left + (right - left) // 2.", "Narrow search space by half."],
                external_link="https://leetcode.com/problems/binary-search/",
                expected_time_complexity="O(log N)",
                expected_space_complexity="O(1)"
            ),
        ]
        db.add_all(problems)
        db.commit()

        # 3. Create Achievements
        achievements = [
            Achievement(id="first_problem", title="First Blood", description="Complete your first DSA problem in DSArena.", icon="Shield"),
            Achievement(id="first_topic", title="Topic Conqueror", description="Master all problems within your first topic node.", icon="Trophy"),
            Achievement(id="7_day_streak", title="Week of Fire", description="Maintain a login/solving streak for 7 consecutive days.", icon="Flame"),
            Achievement(id="30_day_streak", title="Ascended Routine", description="Maintain a login/solving streak for 30 consecutive days.", icon="Zap"),
            Achievement(id="100_problems", title="Centurion", description="Solve 100 problems on the roadmap.", icon="Award"),
            Achievement(id="array_master", title="Array Commander", description="Complete all Arrays and Hashing nodes.", icon="Layers"),
            Achievement(id="graph_explorer", title="Graph Cartographer", description="Complete the Graph and Trees nodes.", icon="GitFork"),
            Achievement(id="dp_survivor", title="DP Overlord", description="Successfully conquer the Dynamic Programming nodes.", icon="TrendingUp"),
            Achievement(id="night_owl", title="Night Owl", description="Submit a correct solution between 12:00 AM and 4:00 AM.", icon="Moon"),
            Achievement(id="early_bird", title="Early Bird", description="Submit a correct solution between 5:00 AM and 8:00 AM.", icon="Sun"),
        ]
        db.add_all(achievements)
        db.commit()

        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
