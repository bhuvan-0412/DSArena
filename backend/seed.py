import datetime
import re
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
import app.models
from app.models.user import User, XPHistory
from app.models.roadmap import RoadmapNode, Problem
from app.models.progress import UserProgress, UserNodeProgress
from app.models.achievement import Achievement, UserAchievement
from app.models.quiz import Quiz, QuizQuestion
from app.models.learning_content import LearningResource, KeyConcept # Ensures all models are registered on Base.metadata
from app.services.striver_importer import StriverVideoImporter

def extract_youtube_video_id(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    short_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
    if short_match:
        return short_match.group(1)
    watch_match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
    if watch_match:
        return watch_match.group(1)
    embed_match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', url)
    if embed_match:
        return embed_match.group(1)
    return None


def seed_db():
    # Make sure tables exist
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Import and sync full 18-Step Striver Curriculum
        import sync_all_striver_steps
        sync_all_striver_steps.run_sync()

        print("Seeding problems...")
        problems = [
            # Two Sum under Arrays Medium -> Two Sum Topic
            Problem(
                id="two-sum",
                parent_id="topic_sec_3_2_1",
                title="Two Sum",
                slug="two-sum",
                type="problem",
                order_index=1,
                estimated_time=25,
                xp_reward=50,
                difficulty="Easy",
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
            # Max Subarray under Arrays Medium -> Kadane's Topic
            Problem(
                id="max-subarray",
                parent_id="topic_sec_3_2_4",
                title="Maximum Subarray (Kadane's)",
                slug="maximum-subarray",
                type="problem",
                order_index=1,
                estimated_time=30,
                xp_reward=100,
                difficulty="Medium",
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
            # Bubble Sort under Sorting-I -> Bubble Sort Topic
            Problem(
                id="bubble-sort",
                parent_id="topic_sec_2_1_1",
                title="Bubble Sort Implementation",
                slug="bubble-sort",
                type="problem",
                order_index=1,
                estimated_time=30,
                xp_reward=50,
                difficulty="Easy",
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
            # Quick Sort under Sorting-II -> Quick Sort Topic
            Problem(
                id="quick-sort",
                parent_id="topic_sec_2_2_2",
                title="Quick Sort Implementation",
                slug="quick-sort",
                type="problem",
                order_index=1,
                estimated_time=45,
                xp_reward=100,
                difficulty="Medium",
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
            # Binary Search under BS 1D -> Binary Search Topic
            Problem(
                id="binary-search-problem",
                parent_id="topic_sec_4_1_1",
                title="Binary Search",
                slug="binary-search",
                type="problem",
                order_index=1,
                estimated_time=20,
                xp_reward=50,
                difficulty="Easy",
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
            # Valid Anagram under Strings Easy -> Valid Anagram Topic
            Problem(
                id="valid-anagram",
                parent_id="topic_sec_5_1_3",
                title="Valid Anagram",
                slug="valid-anagram",
                type="problem",
                order_index=1,
                estimated_time=20,
                xp_reward=50,
                difficulty="Easy",
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
        ]
        db.add_all(problems)
        db.commit()

        # 4. Seed Achievements
        if not db.query(Achievement).first():
            print("Seeding achievements...")
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

        # 5. Seed Quizzes & Questions
        print("Seeding interactive quizzes & questions...")
        
        # Arrays Quiz linked to Two Sum topic_3_2_1
        quiz_arrays = Quiz(
            id=1,
            node_id="topic_3_2_1",
            title="Arrays & Hashing Mastery Battle",
            description="Test your understanding of array memory allocation, hash map lookups, and time complexities.",
            difficulty="Easy",
            estimated_time=5,
            xp_reward=100,
            pass_mark=70,
            question_count=6
        )
        db.add(quiz_arrays)
        db.commit()

        q_arrays = [
            QuizQuestion(
                quiz_id=1,
                question="What is the average-case time complexity of looking up a key in a Hash Map?",
                type="MCQ",
                options=["O(1)", "O(log N)", "O(N)", "O(N²)"],
                correct_answer=[0],
                explanation="Hash maps provide constant O(1) average lookup time via direct key hashing and bucket indexing.",
                difficulty="Easy",
                order_index=1,
                concept="Hash Map Lookup",
                tags=["Hashing", "Time Complexity"],
                expected_time_seconds=30,
                option_explanations=[
                    "Correct! Hash maps compute the array bucket index directly from the key's hash code.",
                    "Incorrect. O(log N) is typical for Binary Search Trees, not Hash Maps.",
                    "Incorrect. O(N) only occurs in worst-case severe hash collisions.",
                    "Incorrect. O(N²) is quadratic time and not associated with hash lookups."
                ]
            ),
            QuizQuestion(
                quiz_id=1,
                question="Which of the following operations on a standard dynamic array (vector) take O(1) time in the worst case? (Select all that apply)",
                type="MULTIPLE_SELECT",
                options=["Accessing element by index", "Inserting element at the beginning", "Updating element value by index", "Inserting element at the end when capacity is full"],
                correct_answer=[0, 2],
                explanation="Accessing and updating by index are direct memory offsets and take O(1). Inserting at the beginning takes O(N) because elements must shift. Inserting at the end when full requires reallocation and copying, taking O(N) worst case.",
                difficulty="Medium",
                order_index=2,
                concept="Subarray Algorithms",
                tags=["Arrays", "Prefix Sum"],
                expected_time_seconds=45,
                option_explanations=[
                    "Correct! Direct index offset calculation is O(1).",
                    "Incorrect. Inserting at index 0 shifts N elements.",
                    "Correct! Updating by index changes the memory location directly in O(1).",
                    "Incorrect. Array reallocation copies N elements."
                ]
            ),
            QuizQuestion(
                quiz_id=1,
                question="True or False: Array elements are stored in contiguous memory locations.",
                type="TRUE_FALSE",
                options=["True", "False"],
                correct_answer=[0],
                explanation="True! Arrays are allocated as contiguous memory blocks, enabling O(1) random index access.",
                difficulty="Easy",
                order_index=3,
                concept="Array Memory Allocation",
                tags=["Arrays", "Memory"],
                expected_time_seconds=20,
                option_explanations=[
                    "Correct! Memory contiguity is the defining property of arrays.",
                    "Incorrect. Array elements are strictly adjacent in RAM."
                ]
            ),
            QuizQuestion(
                quiz_id=1,
                question="Complete the code: To check if a key exists in a Python dictionary `d`, we use `if key ___ d:`",
                type="FILL_BLANK",
                options=["in", "has", "contains", "exists"],
                correct_answer=[0],
                explanation="In Python, the `in` operator checks key membership in O(1) average time.",
                difficulty="Easy",
                order_index=4,
                concept="Python Dictionary Membership",
                tags=["Python", "Hashing"],
                expected_time_seconds=25,
                option_explanations=[
                    "Correct! `if key in d:` is valid Python syntax.",
                    "Incorrect. `has` is not a Python membership operator.",
                    "Incorrect. `contains` is not a keyword in Python.",
                    "Incorrect. `exists` is not valid Python syntax."
                ]
            ),
            QuizQuestion(
                quiz_id=1,
                question="Arrange the time complexities of two-sum approaches from FASTEST to SLOWEST:",
                type="ARRANGE_ORDER",
                options=["Hash Map O(N)", "Two Pointers on Sorted Array O(N log N)", "Brute Force Nested Loops O(N²)"],
                correct_answer=[0, 1, 2],
                explanation="Hash Map O(N) is fastest, followed by Sorting + Two Pointers O(N log N), and Brute Force O(N²) is slowest.",
                difficulty="Medium",
                order_index=5,
                concept="Complexity Comparison",
                tags=["Arrays", "Two Pointers"],
                expected_time_seconds=40,
                option_explanations=[
                    "Correct order! O(N) < O(N log N) < O(N²)."
                ]
            ),
            QuizQuestion(
                quiz_id=1,
                question="What is the worst-case space complexity of storing N elements in a Hash Set?",
                type="MCQ",
                options=["O(N)", "O(1)", "O(N²)", "O(log N)"],
                correct_answer=[0],
                explanation="A Hash Set requires O(N) auxiliary space to store N unique elements.",
                difficulty="Easy",
                order_index=6,
                concept="Hash Set Space Complexity",
                tags=["Hashing", "Space Complexity"],
                expected_time_seconds=30,
                option_explanations=[
                    "Correct! Storing N items takes linear O(N) space.",
                    "Incorrect. O(1) space applies to in-place operations.",
                    "Incorrect. O(N²) is unnecessary quadratic space.",
                    "Incorrect. O(log N) is stack space, not set storage."
                ]
            )
        ]
        db.add_all(q_arrays)

        # Sorting Quiz linked to Bubble Sort topic_2_1_2
        quiz_sorting = Quiz(
            id=2,
            node_id="topic_2_1_2",
            title="Bubble Sort Arena Quiz",
            description="Validate your knowledge on adjacent swaps, pass invariants, and linear best-case optimizations.",
            difficulty="Easy",
            estimated_time=4,
            xp_reward=80,
            pass_mark=70,
            question_count=2
        )
        db.add(quiz_sorting)
        db.commit()

        q_sorting = [
            QuizQuestion(
                quiz_id=2,
                question="What is the best-case time complexity of an optimized Bubble Sort on an already sorted array?",
                type="MCQ",
                options=["O(N)", "O(N log N)", "O(N²)", "O(1)"],
                correct_answer=[0],
                explanation="An optimized Bubble Sort uses a swap flag and exits on pass 1 if no swaps occur, running in O(N) time.",
                difficulty="Easy",
                order_index=1,
                concept="Bubble Sort Best Case",
                tags=["Sorting", "Bubble Sort"],
                expected_time_seconds=30,
                option_explanations=[
                    "Correct! With a `did_swap` flag, Bubble Sort detects a sorted array in 1 pass (O(N)).",
                    "Incorrect. O(N log N) is Merge/Quick Sort best/average time.",
                    "Incorrect. O(N²) is unoptimized Bubble Sort best case.",
                    "Incorrect. O(1) is constant time and cannot inspect an array of size N."
                ]
            ),
            QuizQuestion(
                quiz_id=2,
                question="True or False: Bubble Sort is a stable sorting algorithm.",
                type="TRUE_FALSE",
                options=["True", "False"],
                correct_answer=[0],
                explanation="True! Bubble Sort only swaps adjacent elements if arr[j] > arr[j+1], preserving relative order of equal elements.",
                difficulty="Easy",
                order_index=2,
                concept="Sorting Stability",
                tags=["Sorting", "Stability"],
                expected_time_seconds=20,
                option_explanations=[
                    "Correct! Equal elements never swap past each other in standard Bubble Sort.",
                    "Incorrect. Bubble Sort is indeed stable."
                ]
            )
        ]
        db.add_all(q_sorting)

        # Binary Search Quiz linked to Binary Search topic_4_1_1
        quiz_bs = Quiz(
            id=3,
            node_id="topic_4_1_1",
            title="Binary Search Logarithmic Gauntlet",
            description="Test your limits on search boundary conditions, mid calculation overflows, and virtual spaces.",
            difficulty="Medium",
            estimated_time=6,
            xp_reward=120,
            pass_mark=70,
            question_count=2
        )
        db.add(quiz_bs)
        db.commit()

        q_bs = [
            QuizQuestion(
                quiz_id=3,
                question="To avoid integer overflow when calculating mid in Binary Search, which expression should be used?",
                type="MCQ",
                options=["mid = low + (high - low) // 2", "mid = (low + high) // 2", "mid = (low + high) / 2", "mid = high - low // 2"],
                correct_answer=[0],
                explanation="`low + (high - low) // 2` prevents integer overflow by keeping calculations within integer boundary.",
                difficulty="Easy",
                order_index=1,
                concept="Overflow Prevention",
                tags=["Binary Search", "Bit Tricks"],
                expected_time_seconds=30,
                option_explanations=[
                    "Correct! This formula guarantees no intermediate sum overflow.",
                    "Incorrect. `(low + high)` can overflow if low and high are near INT_MAX.",
                    "Incorrect. Floating point division is inappropriate.",
                    "Incorrect. Operator precedence subtracts `low // 2` first."
                ]
            ),
            QuizQuestion(
                quiz_id=3,
                question="Binary search can only be performed on arrays that are sorted. True or False?",
                type="TRUE_FALSE",
                options=["True", "False"],
                correct_answer=[0],
                explanation="Binary search relies on the monotonicity of the search space, which requires the array to be sorted.",
                difficulty="Easy",
                order_index=2,
                concept="Search Space Monotonicity",
                tags=["Binary Search"],
                expected_time_seconds=20,
                option_explanations=[
                    "Correct! Monotonicity (sorted property) is required for binary halving.",
                    "Incorrect. Unsorted arrays require linear search or sorting first."
                ]
            )
        ]
        db.add_all(q_bs)
        db.commit()

        # 6. Seed Learning Resources
        print("Seeding learning resources...")
        resources = [
            # Two Sum / Arrays topic_3_2_1
            LearningResource(
                node_id="topic_3_2_1",
                title="Striver's Arrays & Hashing Masterclass",
                type="Video",
                author="Striver (takeUforward)",
                duration="28 mins",
                difficulty="Easy",
                url="https://www.youtube.com/watch?v=KLlXCFG5TnA",
                order_index=1
            ),
            LearningResource(
                node_id="topic_3_2_1",
                title="Hash Maps & Subarray Sum Comprehensive Guide",
                type="Article",
                author="takeUforward Editorial",
                duration="12 min read",
                difficulty="Medium",
                url="https://takeuforward.org/data-structure/two-sum-check-if-a-pair-with-given-sum-exists-in-array/",
                order_index=2
            ),
            LearningResource(
                node_id="topic_3_2_1",
                title="Python & C++ Standard Hash Table Implementations",
                type="Documentation",
                author="cppreference.com",
                duration="8 min read",
                difficulty="Easy",
                url="https://en.cppreference.com/w/cpp/container/unordered_map",
                order_index=3
            ),
            # Bubble Sort / Sorting topic_2_1_2
            LearningResource(
                node_id="topic_2_1_2",
                title="Complete Sorting Algorithms Breakdown",
                type="Video",
                author="Striver (takeUforward)",
                duration="35 mins",
                difficulty="Easy",
                url="https://www.youtube.com/watch?v=HGk_ypEuSKE",
                order_index=1
            ),
            LearningResource(
                node_id="topic_2_1_2",
                title="Bubble Sort In-Depth Explanation & In-Place Analysis",
                type="Article",
                author="takeUforward Editorial",
                duration="10 min read",
                difficulty="Easy",
                url="https://takeuforward.org/sorting/bubble-sort-algorithm/",
                order_index=2
            ),
            # Binary Search topic_4_1_1
            LearningResource(
                node_id="topic_4_1_1",
                title="Binary Search 1D Array Deep Dive",
                type="Video",
                author="Striver (takeUforward)",
                duration="40 mins",
                difficulty="Medium",
                url="https://www.youtube.com/watch?v=MHf6aWe2v2Q",
                order_index=1
            ),
            LearningResource(
                node_id="topic_4_1_1",
                title="Binary Search Cheat Sheet & Corner Cases",
                type="Article",
                author="takeUforward Editorial",
                duration="15 min read",
                difficulty="Medium",
                url="https://takeuforward.org/data-structure/binary-search-explained/",
                order_index=2
            )
        ]
        db.add_all(resources)
        db.commit()

        # 7. Seed Key Concepts
        print("Seeding key concepts...")
        key_concepts = [
            # Two Sum / Arrays topic_3_2_1
            KeyConcept(
                node_id="topic_3_2_1",
                title="Hash Map Complement Lookup",
                summary="Instead of nested iterations checking every pair O(N²), store elements in a hash map as you iterate to check for the required complement (target - current) in O(1) time.",
                key_points=[
                    "Maintain a hash map mapping element_value -> index.",
                    "For element X, calculate target - X.",
                    "If complement exists in map, return indices immediately.",
                    "Otherwise, insert X into map and continue."
                ],
                complexity_notes="Time Complexity: O(N) single pass lookup.\nSpace Complexity: O(N) for storing up to N elements in hash map.",
                common_mistakes=[
                    "Using the same element twice (e.g., matching nums[i] with itself).",
                    "Inserting into the map BEFORE checking for the complement.",
                    "Assuming the array is sorted when it is not."
                ],
                best_practices=[
                    "Check for complement before inserting current value to avoid self-matching.",
                    "Use unordered_map in C++ or dict in Python for average O(1) amortized lookup.",
                    "If space is tightly constrained (O(1)), sort array first and use Two-Pointers (O(N log N))."
                ],
                order_index=1
            ),
            KeyConcept(
                node_id="topic_3_2_1",
                title="Array Memory & Subarray Contiguity",
                summary="Arrays allocate contiguous memory blocks. Subarray problems often leverage contiguous indexing techniques like Sliding Window or Prefix Sums.",
                key_points=[
                    "Subarray = contiguous sequence of elements.",
                    "Subsequence = ordered subset, does NOT need to be contiguous.",
                    "Prefix sum map enables computing sum(i...j) in O(1) as prefix[j] - prefix[i-1]."
                ],
                complexity_notes="Prefix Sum Map: Time O(N), Space O(N).\nTwo Pointers / Sliding Window: Time O(N), Space O(1).",
                common_mistakes=[
                    "Confusing subarrays with subsequences.",
                    "Off-by-one errors when computing prefix sum bounds."
                ],
                best_practices=[
                    "Use prefix sums with hash maps for target subarray sum problems with negative numbers.",
                    "Use two pointers sliding window ONLY when all numbers are non-negative."
                ],
                order_index=2
            ),
            # Bubble Sort / Sorting topic_2_1_2
            KeyConcept(
                node_id="topic_2_1_2",
                title="Adjacent Swapping & Bubble Optimization",
                summary="Bubble sort repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order.",
                key_points=[
                    "Pass 1 pushes the maximum element to the rightmost index.",
                    "Subsequent passes sort remaining n-i elements.",
                    "An optimized version maintains a 'swapped' flag to terminate early if array is already sorted."
                ],
                complexity_notes="Worst/Average Time: O(N²).\nBest Time (Optimized): O(N) when array is already sorted.\nSpace: O(1) in-place.",
                common_mistakes=[
                    "Running inner loop up to N-1 on every pass without reducing boundary.",
                    "Forgetting early exit optimization flag."
                ],
                best_practices=[
                    "Use boolean `did_swap` flag inside outer loop to achieve linear O(N) best case.",
                    "Prefer Merge Sort or Quick Sort for large datasets (N > 10^3)."
                ],
                order_index=1
            ),
            # Binary Search topic_4_1_1
            KeyConcept(
                node_id="topic_4_1_1",
                title="Logarithmic Search Space Reduction",
                summary="Binary search works by repeatedly dividing the search interval in half. Search space must satisfy a monotonic property (e.g. sorted array).",
                key_points=[
                    "Calculate mid = low + (high - low) // 2 to avoid integer overflow.",
                    "Compare target with mid value.",
                    "Adjust low = mid + 1 or high = mid - 1 based on comparison."
                ],
                complexity_notes="Time Complexity: O(log N) due to halving the search space.\nSpace Complexity: O(1) iterative or O(log N) recursive call stack.",
                common_mistakes=[
                    "Using (low + high) / 2 which can overflow integer limit in C++/Java.",
                    "Infinite loop caused by improper low/high update conditions (e.g. low = mid instead of low = mid + 1).",
                    "Off-by-one errors in while condition (low <= high vs low < high)."
                ],
                best_practices=[
                    "Always calculate mid as `low + (high - low) // 2`.",
                    "Define search invariant clearly (e.g., target is guaranteed in [low, high]).",
                    "Use lower_bound and upper_bound patterns for duplicate elements."
                ],
                order_index=1
            )
        ]
        # 12. Seed AI Provider Configs & Prompt Templates
        from app.models.ai import ProviderConfig, AISettings, PromptTemplate, Conversation, Message
        from app.services.ai.prompt_engine import DEFAULT_SYSTEM_PROMPTS

        db.query(Message).delete()
        db.query(Conversation).delete()
        db.query(AISettings).delete()
        db.query(PromptTemplate).delete()
        db.query(ProviderConfig).delete()
        db.commit()

        print("Seeding AI Providers, System Prompt Templates, and Default AI Settings...")

        providers = [
            ProviderConfig(
                provider_name="openai",
                display_name="OpenAI GPT-4o Mini",
                is_active=True,
                is_default=True,
                default_model="gpt-4o-mini"
            ),
            ProviderConfig(
                provider_name="gemini",
                display_name="Google Gemini 1.5 Flash",
                is_active=True,
                is_default=False,
                default_model="gemini-1.5-flash"
            ),
            ProviderConfig(
                provider_name="anthropic",
                display_name="Anthropic Claude 3.5 Sonnet",
                is_active=True,
                is_default=False,
                default_model="claude-3-5-sonnet"
            ),
            ProviderConfig(
                provider_name="local",
                display_name="Local LLM (Ollama / Llama 3)",
                is_active=True,
                is_default=False,
                base_url="http://localhost:11434",
                default_model="llama-3.2"
            )
        ]
        db.add_all(providers)
        db.commit()

        # Seed Prompt Templates for 5 Modes
        templates = [
            PromptTemplate(
                mode="concept_mentor",
                version=1,
                title="Concept Mentor (Visual & Socratic Coach)",
                system_prompt=DEFAULT_SYSTEM_PROMPTS["concept_mentor"],
                is_active=True
            ),
            PromptTemplate(
                mode="hint_system",
                version=1,
                title="5-Level Progressive Hint System",
                system_prompt=DEFAULT_SYSTEM_PROMPTS["hint_system"],
                is_active=True
            ),
            PromptTemplate(
                mode="code_reviewer",
                version=1,
                title="AI Code Reviewer & Complexity Analyzer",
                system_prompt=DEFAULT_SYSTEM_PROMPTS["code_reviewer"],
                is_active=True
            ),
            PromptTemplate(
                mode="study_planner",
                version=1,
                title="AI Adaptive Study Planner",
                system_prompt=DEFAULT_SYSTEM_PROMPTS["study_planner"],
                is_active=True
            ),
            PromptTemplate(
                mode="interview_mentor",
                version=1,
                title="AI Technical Mock Interviewer",
                system_prompt=DEFAULT_SYSTEM_PROMPTS["interview_mentor"],
                is_active=True
            ),
        ]
        db.add_all(templates)
        db.commit()

        # Seed default AI Settings & Adaptive Preferences & Interview OS for mock_user_striver
        from app.models.adaptive import UserPreferences, DailyStudyPlan, LearningRecommendation, LearningInsight
        from app.models.interview import CareerGoal, UserCareerGoal, Company, CompanyTopic, UserCompany, InterviewReadiness, Milestone, UserMilestone
        
        db.query(UserMilestone).delete()
        db.query(Milestone).delete()
        db.query(UserCompany).delete()
        db.query(CompanyTopic).delete()
        db.query(Company).delete()
        db.query(UserCareerGoal).delete()
        db.query(CareerGoal).delete()
        db.query(LearningRecommendation).delete()
        db.query(DailyStudyPlan).delete()
        db.query(UserPreferences).delete()
        db.commit()

        # 1. Career Goals
        goals = [
            CareerGoal(slug="software_engineer", title="Software Engineer", description="Targeting SDE-1 / SDE-2 roles at top tech companies.", icon="Briefcase"),
            CareerGoal(slug="internship", title="Summer Internship", description="Pre-final year target for SDE internships.", icon="GraduationCap"),
            CareerGoal(slug="campus_placement", title="Campus Placement", description="On-campus placement drives & college hiring.", icon="Building2"),
            CareerGoal(slug="competitive_programming", title="Competitive Programming", description="Rating push on Codeforces / LeetCode Contests.", icon="Trophy"),
            CareerGoal(slug="learn_dsa", title="Learn DSA Fundamentals", description="Mastering core data structures & algorithms from scratch.", icon="BookOpen"),
            CareerGoal(slug="switch_company", title="Company Switch", description="Experienced engineer switching to tier-1 companies.", icon="Zap"),
        ]
        db.add_all(goals)

        # 2. Target Companies (14 requested)
        companies = [
            Company(slug="amazon", name="Amazon", logo_url="https://api.iconify.design/logos:aws.svg", difficulty="Hard", interview_rounds=["Online Assessment (2 Questions)", "Technical Round 1 (DSA)", "Technical Round 2 (System Design / LLD)", "Bar Raiser (Leadership Principles)"], high_frequency_topics=["topic_3_2_1", "topic_2_1_2"], recommended_problem_count=50, expected_prep_days=30),
            Company(slug="google", name="Google", logo_url="https://api.iconify.design/logos:google-icon.svg", difficulty="Hard", interview_rounds=["Screening Round (Graphs / DP)", "Technical Round 1 (Hard Algorithms)", "Technical Round 2 (System Architecture)", "Googliness & Leadership"], high_frequency_topics=["topic_3_2_1"], recommended_problem_count=60, expected_prep_days=45),
            Company(slug="microsoft", name="Microsoft", logo_url="https://api.iconify.design/logos:microsoft.svg", difficulty="Medium", interview_rounds=["Codility Assessment", "Technical Round 1 (Trees & Arrays)", "Technical Round 2 (System Design)", "AA Round"], high_frequency_topics=["topic_3_2_1", "topic_2_1_2"], recommended_problem_count=40, expected_prep_days=25),
            Company(slug="atlassian", name="Atlassian", logo_url="https://api.iconify.design/logos:atlassian.svg", difficulty="Hard", interview_rounds=["Online Assessment", "Data Structures & Algorithms", "System Design / Coding Craftsmanship", "Values & Behavioral"], high_frequency_topics=["topic_3_2_1"], recommended_problem_count=45, expected_prep_days=30),
            Company(slug="adobe", name="Adobe", logo_url="https://api.iconify.design/logos:adobe-icon.svg", difficulty="Medium", interview_rounds=["Online Test", "Technical Round 1 (C++ / OOP / DSA)", "Technical Round 2", "HR Round"], high_frequency_topics=["topic_2_1_2"], recommended_problem_count=35, expected_prep_days=20),
            Company(slug="oracle", name="Oracle", logo_url="https://api.iconify.design/logos:oracle.svg", difficulty="Medium", interview_rounds=["Online Assessment", "Technical Round 1 (SQL & DSA)", "Technical Round 2", "Managerial Round"], high_frequency_topics=["topic_3_2_1"], recommended_problem_count=30, expected_prep_days=20),
            Company(slug="goldman_sachs", name="Goldman Sachs", logo_url="https://api.iconify.design/logos:goldmansachs.svg", difficulty="Hard", interview_rounds=["HackerRank Math & Coding", "Technical Round 1 (DP & Math)", "Technical Round 2", "HR Round"], high_frequency_topics=["topic_3_2_1"], recommended_problem_count=50, expected_prep_days=35),
            Company(slug="uber", name="Uber", logo_url="https://api.iconify.design/logos:uber.svg", difficulty="Hard", interview_rounds=["CodeSignal OA", "Technical Round 1 (Graphs / Algorithms)", "Technical Round 2 (LLD / System Design)", "Bar Raiser"], high_frequency_topics=["topic_3_2_1"], recommended_problem_count=55, expected_prep_days=40),
            Company(slug="flipkart", name="Flipkart", logo_url="https://api.iconify.design/logos:flipkart.svg", difficulty="Hard", interview_rounds=["Machine Coding Round", "Problem Solving / DSA", "System Design", "Cultural Fit"], high_frequency_topics=["topic_3_2_1"], recommended_problem_count=45, expected_prep_days=30),
            Company(slug="meesho", name="Meesho", logo_url="https://api.iconify.design/logos:meesho.svg", difficulty="Medium", interview_rounds=["Online Assessment", "Problem Solving Round", "System Design", "Culture Fit"], high_frequency_topics=["topic_3_2_1"], recommended_problem_count=35, expected_prep_days=20),
            Company(slug="zoho", name="Zoho", logo_url="https://api.iconify.design/logos:zoho.svg", difficulty="Easy", interview_rounds=["Round 1: C / Java Basics", "Round 2: Advanced Coding", "Round 3: Design", "HR Round"], high_frequency_topics=["topic_2_1_2"], recommended_problem_count=25, expected_prep_days=15),
            Company(slug="tcs", name="TCS", logo_url="https://api.iconify.design/logos:tcs.svg", difficulty="Easy", interview_rounds=["TCS NQT Assessment", "Technical Interview", "HR Interview"], high_frequency_topics=["topic_2_1_2"], recommended_problem_count=20, expected_prep_days=10),
            Company(slug="infosys", name="Infosys", logo_url="https://api.iconify.design/logos:infosys.svg", difficulty="Easy", interview_rounds=["InfyTQ / HackWithInfy", "Technical Round", "HR Round"], high_frequency_topics=["topic_2_1_2"], recommended_problem_count=20, expected_prep_days=10),
            Company(slug="wipro", name="Wipro", logo_url="https://api.iconify.design/logos:wipro.svg", difficulty="Easy", interview_rounds=["NLTH Assessment", "Technical & HR Interview"], high_frequency_topics=["topic_2_1_2"], recommended_problem_count=20, expected_prep_days=10),
        ]
        db.add_all(companies)

        # 3. Milestones
        milestones = [
            Milestone(slug="complete_arrays", title="Arrays Master", description="Solve your first array & hashing problem.", icon="Layers", xp_reward=250, badge_name="Array Pioneer"),
            Milestone(slug="solve_50_problems", title="Gladiator Centurion", description="Solve 50 Data Structure problems.", icon="Trophy", xp_reward=500, badge_name="Gladiator Centurion"),
            Milestone(slug="complete_graphs", title="Graph Conqueror", description="Master Graph Traversal (BFS / DFS).", icon="GitFork", xp_reward=400, badge_name="Graph Conqueror"),
            Milestone(slug="complete_dp", title="Dynamic Titan", description="Solve Dynamic Programming sub-problems.", icon="Zap", xp_reward=600, badge_name="Dynamic Titan"),
            Milestone(slug="readiness_80", title="Interview Ready", description="Achieve an 80%+ Interview Readiness Score.", icon="ShieldCheck", xp_reward=1000, badge_name="FAANG Ready"),
        ]
        db.add_all(milestones)
        # 4. Weekly & Monthly Challenges
        from app.models.engagement import WeeklyChallenge, MonthlyChallenge, Season, SeasonReward, StreakFreeze, RewardChest, UserTitle
        db.query(WeeklyChallenge).delete()
        db.query(MonthlyChallenge).delete()
        db.query(Season).delete()
        db.commit()

        w_challenges = [
            WeeklyChallenge(title="Solve 15 Problems", description="Solve 15 coding problems this week.", target_count=15, xp_reward=500),
            WeeklyChallenge(title="Earn 1000 XP", description="Accumulate 1000 XP through problem solving & quizzes.", target_count=1000, xp_reward=500),
            WeeklyChallenge(title="Complete 2 Topics", description="Finish 2 topics on your roadmap.", target_count=2, xp_reward=400),
            WeeklyChallenge(title="Perfect Quiz Score", description="Achieve 100% accuracy on any topic quiz.", target_count=1, xp_reward=300),
            WeeklyChallenge(title="5-Day Study Streak", description="Maintain an active study streak for 5 days.", target_count=5, xp_reward=450),
        ]
        db.add_all(w_challenges)

        m_challenges = [
            MonthlyChallenge(title="Finish Arrays & Hashing", description="Complete all Array & Hashing problems.", target_count=5, xp_reward=1500),
            MonthlyChallenge(title="Finish Binary Search", description="Master Binary Search algorithms.", target_count=5, xp_reward=1500),
            MonthlyChallenge(title="Reach Gold Rank", description="Push your rank to Gold in DSArena.", target_count=1, xp_reward=2000),
            MonthlyChallenge(title="Complete 30 Study Sessions", description="Complete 30 daily study sessions.", target_count=30, xp_reward=2500),
        ]
        db.add_all(m_challenges)

        # 5. Season 1 Pass
        season1 = Season(name="Season 1: Origin of Algorithms", is_active=True)
        db.add(season1)
        db.commit()

        # 6. Timed Coding Contests
        from app.models.contest import Contest, ContestProblem, ContestParticipation, RatingHistory
        db.query(Contest).delete()
        db.commit()

        now = datetime.datetime.utcnow()
        contests = [
            Contest(
                title="DSArena Weekly Contest 1",
                slug="weekly_contest_1",
                contest_type="weekly",
                description="Official weekly competitive algorithms contest. 4 problems, 90 minutes.",
                difficulty="Medium",
                duration_minutes=90,
                start_time=now - datetime.timedelta(minutes=30),
                end_time=now + datetime.timedelta(minutes=60),
                prize_xp=1500,
                is_active=True
            ),
            Contest(
                title="Daily Speed Challenge #42",
                slug="daily_speed_42",
                contest_type="daily",
                description="Fast-paced 30-minute daily algorithm sprint.",
                difficulty="Easy",
                duration_minutes=30,
                start_time=now - datetime.timedelta(minutes=10),
                end_time=now + datetime.timedelta(minutes=20),
                prize_xp=500,
                is_active=True
            ),
            Contest(
                title="Amazon SDE Championship",
                slug="amazon_sde_champ",
                contest_type="company",
                description="Simulated Amazon Online Assessment contest with real interview questions.",
                difficulty="Hard",
                duration_minutes=120,
                start_time=now + datetime.timedelta(days=2),
                end_time=now + datetime.timedelta(days=2, hours=2),
                prize_xp=3000,
                is_active=True
            ),
            Contest(
                title="Monthly Grand Master Cup",
                slug="monthly_gm_cup",
                contest_type="monthly",
                description="Past championship contest available for Virtual Contest replay.",
                difficulty="Hard",
                duration_minutes=120,
                start_time=now - datetime.timedelta(days=7),
                end_time=now - datetime.timedelta(days=7, hours=-2),
                prize_xp=5000,
                is_active=False
            )
        ]
        db.add_all(contests)
        db.commit()

        # Seed contest problems for Weekly Contest 1
        c1 = db.query(Contest).filter(Contest.slug == "weekly_contest_1").first()
        if c1:
            cp1 = ContestProblem(contest_id=c1.id, problem_id="problem_3_2_1", problem_order=1, points=500, editorial_markdown="Use Two Pointers to find target sum in O(N).")
            cp2 = ContestProblem(contest_id=c1.id, problem_id="problem_2_1_2", problem_order=2, points=1000, editorial_markdown="Use HashMap to store element indices.")
            db.add_all([cp1, cp2])
            db.commit()

        user = db.query(User).filter(User.clerk_id == "mock_user_striver").first()
        if not user:
            user = User(
                clerk_id="mock_user_striver",
                email="striver@dsarena.com",
                username="striver",
                display_name="Striver",
                xp=1000,
                level=5,
                rank="Gold",
                current_streak=7,
                max_streak=14
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Seed initial node progress (topic_1_1_1 is AVAILABLE)
        db.query(UserNodeProgress).filter(UserNodeProgress.user_id == user.id).delete()
        unp_first = UserNodeProgress(
            user_id=user.id,
            node_id="topic_1_1_1",
            status="AVAILABLE",
            started_at=datetime.datetime.utcnow()
        )
        db.add(unp_first)
        db.commit()

        if user:

            default_prov = db.query(ProviderConfig).filter(ProviderConfig.is_default == True).first()
            ai_setting = AISettings(
                user_id=user.id,
                active_provider_id=default_prov.id if default_prov else None,
                temperature=0.7,
                preferred_explanation_style="visual_socratic"
            )
            db.add(ai_setting)

            prefs = UserPreferences(
                user_id=user.id,
                target_company="FAANG / Top Tech",
                daily_time_available_minutes=60,
                difficulty_preference="Adaptive",
                learning_style="Visual & Hands-on",
                favorite_language="python"
            )
            db.add(prefs)

            # Seed default titles & streak freeze & mystery chest
            db.add(StreakFreeze(user_id=user.id, current_freezes=1, max_freezes=2))
            db.add(RewardChest(user_id=user.id, chest_type="mystery", is_opened=False))
            db.add(UserTitle(user_id=user.id, title_name="Algorithm Explorer", is_equipped=True))
            db.add(UserTitle(user_id=user.id, title_name="Array Conqueror", is_equipped=False))

            # User selected goals & companies
            g1 = db.query(CareerGoal).filter(CareerGoal.slug == "software_engineer").first()
            g2 = db.query(CareerGoal).filter(CareerGoal.slug == "switch_company").first()
            if g1: db.add(UserCareerGoal(user_id=user.id, goal_id=g1.id))
            if g2: db.add(UserCareerGoal(user_id=user.id, goal_id=g2.id))

            c1 = db.query(Company).filter(Company.slug == "amazon").first()
            c2 = db.query(Company).filter(Company.slug == "google").first()
            c3 = db.query(Company).filter(Company.slug == "microsoft").first()
            if c1: db.add(UserCompany(user_id=user.id, company_id=c1.id))
            if c2: db.add(UserCompany(user_id=user.id, company_id=c2.id))
            if c3: db.add(UserCompany(user_id=user.id, company_id=c3.id))

            db.commit()

        print("Database seeded successfully with AI Mentor, Adaptive Learning, Interview OS & Engagement Engine!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()

