from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.user import User, XPHistory
from app.models.roadmap import RoadmapNode, Problem
from app.models.progress import UserProgress, UserNodeProgress
from app.models.achievement import Achievement, UserAchievement
from app.models.quiz import Quiz, QuizQuestion
from app.models.learning_content import LearningResource, KeyConcept

def seed_db():
    # Make sure tables exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Clear existing roadmap nodes & problems if any (we want to re-seed cleanly)
        db.query(LearningResource).delete()
        db.query(KeyConcept).delete()
        db.query(QuizQuestion).delete()
        db.query(Quiz).delete()
        db.query(Problem).delete()
        db.query(RoadmapNode).delete()
        db.commit()

        print("Seeding steps, sections, and topics...")
        
        # 1. Seed Steps (Campaigns)
        steps = [
            RoadmapNode(id="step_1", title="Step 1: Learn the Basics", slug="learn-the-basics", type="step", order_index=1, estimated_time=360, xp_reward=500, difficulty="Easy"),
            RoadmapNode(id="step_2", title="Step 2: Learn Important Sorting Techniques", slug="learn-important-sorting-techniques", type="step", order_index=2, estimated_time=180, xp_reward=300, difficulty="Easy"),
            RoadmapNode(id="step_3", title="Step 3: Solve Problems on Arrays [Easy -> Medium -> Hard]", slug="arrays-easy-medium-hard", type="step", order_index=3, estimated_time=720, xp_reward=1000, difficulty="Medium"),
            RoadmapNode(id="step_4", title="Step 4: Binary Search [1D, 2D Arrays, Search Space]", slug="binary-search-arrays", type="step", order_index=4, estimated_time=600, xp_reward=800, difficulty="Medium"),
            RoadmapNode(id="step_5", title="Step 5: Learn Strings [Easy -> Medium]", slug="learn-strings", type="step", order_index=5, estimated_time=480, xp_reward=600, difficulty="Medium"),
        ]
        db.add_all(steps)
        db.commit()

        # 2. Seed Sections
        sections = [
            # Step 1 Sections
            RoadmapNode(id="sec_1_1", parent_id="step_1", title="Things to Know in C++/Java/Python/JS", slug="things-to-know", type="section", order_index=1, estimated_time=60, xp_reward=100, difficulty="Easy"),
            RoadmapNode(id="sec_1_2", parent_id="step_1", title="Build-up Logical Thinking", slug="build-up-logical-thinking", type="section", order_index=2, estimated_time=60, xp_reward=100, difficulty="Easy"),
            RoadmapNode(id="sec_1_3", parent_id="step_1", title="Learn STL / Collections", slug="learn-stl-collections", type="section", order_index=3, estimated_time=60, xp_reward=100, difficulty="Easy"),
            RoadmapNode(id="sec_1_4", parent_id="step_1", title="Know Basic Maths", slug="know-basic-maths", type="section", order_index=4, estimated_time=60, xp_reward=100, difficulty="Easy"),
            RoadmapNode(id="sec_1_5", parent_id="step_1", title="Learn Basic Recursion", slug="learn-basic-recursion", type="section", order_index=5, estimated_time=60, xp_reward=100, difficulty="Easy"),
            RoadmapNode(id="sec_1_6", parent_id="step_1", title="Learn Basic Hashing", slug="learn-basic-hashing", type="section", order_index=6, estimated_time=60, xp_reward=100, difficulty="Easy"),
            
            # Step 2 Sections
            RoadmapNode(id="sec_2_1", parent_id="step_2", title="Sorting-I", slug="sorting-i", type="section", order_index=1, estimated_time=90, xp_reward=150, difficulty="Easy"),
            RoadmapNode(id="sec_2_2", parent_id="step_2", title="Sorting-II", slug="sorting-ii", type="section", order_index=2, estimated_time=90, xp_reward=150, difficulty="Medium"),
            
            # Step 3 Sections
            RoadmapNode(id="sec_3_1", parent_id="step_3", title="Arrays Easy", slug="arrays-easy", type="section", order_index=1, estimated_time=240, xp_reward=300, difficulty="Easy"),
            RoadmapNode(id="sec_3_2", parent_id="step_3", title="Arrays Medium", slug="arrays-medium", type="section", order_index=2, estimated_time=240, xp_reward=300, difficulty="Medium"),
            RoadmapNode(id="sec_3_3", parent_id="step_3", title="Arrays Hard", slug="arrays-hard", type="section", order_index=3, estimated_time=240, xp_reward=400, difficulty="Hard"),
            
            # Step 4 Sections
            RoadmapNode(id="sec_4_1", parent_id="step_4", title="BS on 1D Arrays", slug="bs-on-1d-arrays", type="section", order_index=1, estimated_time=200, xp_reward=250, difficulty="Easy"),
            RoadmapNode(id="sec_4_2", parent_id="step_4", title="BS on Answers", slug="bs-on-answers", type="section", order_index=2, estimated_time=200, xp_reward=300, difficulty="Medium"),
            RoadmapNode(id="sec_4_3", parent_id="step_4", title="BS on 2D Arrays", slug="bs-on-2d-arrays", type="section", order_index=3, estimated_time=200, xp_reward=250, difficulty="Hard"),
            
            # Step 5 Sections
            RoadmapNode(id="sec_5_1", parent_id="step_5", title="Strings Easy", slug="strings-easy", type="section", order_index=1, estimated_time=240, xp_reward=300, difficulty="Easy"),
            RoadmapNode(id="sec_5_2", parent_id="step_5", title="Strings Medium", slug="strings-medium", type="section", order_index=2, estimated_time=240, xp_reward=300, difficulty="Medium"),
        ]
        db.add_all(sections)
        db.commit()

        # 3. Seed Topics (Concepts)
        topics = [
            # Step 1 - Things to Know
            RoadmapNode(id="topic_1_1_1", parent_id="sec_1_1", title="User Input / Output", slug="user-input-output", type="topic", order_index=1, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_1_2", parent_id="sec_1_1", title="Data Types", slug="data-types", type="topic", order_index=2, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_1_3", parent_id="sec_1_1", title="If Else Statements", slug="if-else-statements", type="topic", order_index=3, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_1_4", parent_id="sec_1_1", title="Switch Statement", slug="switch-statement", type="topic", order_index=4, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_1_5", parent_id="sec_1_1", title="Arrays & Strings Basics", slug="arrays-strings-basics", type="topic", order_index=5, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_1_6", parent_id="sec_1_1", title="Loops Basics", slug="loops-basics", type="topic", order_index=6, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_1_7", parent_id="sec_1_1", title="Functions Basics", slug="functions-basics", type="topic", order_index=7, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_1_8", parent_id="sec_1_1", title="Time & Space Complexity", slug="time-space-complexity", type="topic", order_index=8, estimated_time=15, xp_reward=50, difficulty="Easy"),
            
            # Step 1 - Logical Thinking
            RoadmapNode(id="topic_1_2_1", parent_id="sec_1_2", title="Pattern Problems", slug="pattern-problems", type="topic", order_index=1, estimated_time=30, xp_reward=50, difficulty="Easy"),
            
            # Step 1 - STL/Collections
            RoadmapNode(id="topic_1_3_1", parent_id="sec_1_3", title="C++ STL / Java Collections", slug="cpp-stl-collections", type="topic", order_index=1, estimated_time=30, xp_reward=50, difficulty="Easy"),
            
            # Step 1 - Basic Maths
            RoadmapNode(id="topic_1_4_1", parent_id="sec_1_4", title="Count Digits", slug="count-digits", type="topic", order_index=1, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_4_2", parent_id="sec_1_4", title="Reverse a Number", slug="reverse-number", type="topic", order_index=2, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_4_3", parent_id="sec_1_4", title="Palindrome Number", slug="palindrome-number", type="topic", order_index=3, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_4_4", parent_id="sec_1_4", title="GCD or HCF", slug="gcd-or-hcf", type="topic", order_index=4, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_4_5", parent_id="sec_1_4", title="Armstrong Number", slug="armstrong-number", type="topic", order_index=5, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_4_6", parent_id="sec_1_4", title="Print all Divisors", slug="print-all-divisors", type="topic", order_index=6, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_4_7", parent_id="sec_1_4", title="Prime Numbers", slug="prime-numbers", type="topic", order_index=7, estimated_time=15, xp_reward=50, difficulty="Easy"),
            
            # Step 1 - Basic Recursion
            RoadmapNode(id="topic_1_5_1", parent_id="sec_1_5", title="Print Name N Times", slug="print-name-n-times", type="topic", order_index=1, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_5_2", parent_id="sec_1_5", title="Print 1 to N", slug="print-1-to-n", type="topic", order_index=2, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_5_3", parent_id="sec_1_5", title="Print N to 1", slug="print-n-to-1", type="topic", order_index=3, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_5_4", parent_id="sec_1_5", title="Sum of N numbers", slug="sum-of-n-numbers", type="topic", order_index=4, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_5_5", parent_id="sec_1_5", title="Factorial of N", slug="factorial-of-n", type="topic", order_index=5, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_5_6", parent_id="sec_1_5", title="Reverse an Array", slug="reverse-an-array", type="topic", order_index=6, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_5_7", parent_id="sec_1_5", title="Check Palindrome String", slug="check-palindrome-string", type="topic", order_index=7, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_5_8", parent_id="sec_1_5", title="Fibonacci Number", slug="fibonacci-number", type="topic", order_index=8, estimated_time=15, xp_reward=50, difficulty="Easy"),
            
            # Step 1 - Basic Hashing
            RoadmapNode(id="topic_1_6_1", parent_id="sec_1_6", title="Number Hashing", slug="number-hashing", type="topic", order_index=1, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_6_2", parent_id="sec_1_6", title="Character Hashing", slug="character-hashing", type="topic", order_index=2, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_1_6_3", parent_id="sec_1_6", title="Frequency Count", slug="frequency-count", type="topic", order_index=3, estimated_time=15, xp_reward=50, difficulty="Easy"),
            
            # Step 2 - Sorting-I
            RoadmapNode(id="topic_2_1_1", parent_id="sec_2_1", title="Selection Sort", slug="selection-sort", type="topic", order_index=1, estimated_time=30, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_2_1_2", parent_id="sec_2_1", title="Bubble Sort", slug="bubble-sort-topic", type="topic", order_index=2, estimated_time=30, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_2_1_3", parent_id="sec_2_1", title="Insertion Sort", slug="insertion-sort", type="topic", order_index=3, estimated_time=30, xp_reward=50, difficulty="Easy"),
            
            # Step 2 - Sorting-II
            RoadmapNode(id="topic_2_2_1", parent_id="sec_2_2", title="Merge Sort", slug="merge-sort", type="topic", order_index=1, estimated_time=45, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_2_2_2", parent_id="sec_2_2", title="Quick Sort", slug="quick-sort-topic", type="topic", order_index=2, estimated_time=45, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_2_2_3", parent_id="sec_2_2", title="Recursive Bubble Sort", slug="recursive-bubble-sort", type="topic", order_index=3, estimated_time=30, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_2_2_4", parent_id="sec_2_2", title="Recursive Insertion Sort", slug="recursive-insertion-sort", type="topic", order_index=4, estimated_time=30, xp_reward=100, difficulty="Medium"),
            
            # Step 3 - Arrays Easy
            RoadmapNode(id="topic_3_1_1", parent_id="sec_3_1", title="Largest Element in Array", slug="largest-element", type="topic", order_index=1, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_2", parent_id="sec_3_1", title="Second Largest Element", slug="second-largest-element", type="topic", order_index=2, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_3", parent_id="sec_3_1", title="Check if Array is Sorted", slug="check-if-sorted", type="topic", order_index=3, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_4", parent_id="sec_3_1", title="Remove Duplicates", slug="remove-duplicates", type="topic", order_index=4, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_5", parent_id="sec_3_1", title="Left Rotate by One", slug="left-rotate-by-one", type="topic", order_index=5, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_6", parent_id="sec_3_1", title="Left Rotate by D Places", slug="left-rotate-by-d-places", type="topic", order_index=6, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_7", parent_id="sec_3_1", title="Move Zeros to End", slug="move-zeros-to-end", type="topic", order_index=7, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_8", parent_id="sec_3_1", title="Linear Search", slug="linear-search", type="topic", order_index=8, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_9", parent_id="sec_3_1", title="Find Union", slug="find-union", type="topic", order_index=9, estimated_time=30, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_10", parent_id="sec_3_1", title="Find Missing Number", slug="find-missing-number", type="topic", order_index=10, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_11", parent_id="sec_3_1", title="Maximum Consecutive Ones", slug="maximum-consecutive-ones", type="topic", order_index=11, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_12", parent_id="sec_3_1", title="Find Number that Appears Once", slug="find-single-number", type="topic", order_index=12, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_3_1_13", parent_id="sec_3_1", title="Longest Subarray with Sum K", slug="longest-subarray-sum-k", type="topic", order_index=13, estimated_time=30, xp_reward=50, difficulty="Easy"),
            
            # Step 3 - Arrays Medium
            RoadmapNode(id="topic_3_2_1", parent_id="sec_3_2", title="Two Sum", slug="two-sum-topic", type="topic", order_index=1, estimated_time=25, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_2", parent_id="sec_3_2", title="Sort 0s 1s 2s", slug="sort-zeros-ones-twos", type="topic", order_index=2, estimated_time=20, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_3", parent_id="sec_3_2", title="Majority Element (>N/2)", slug="majority-element-n-2", type="topic", order_index=3, estimated_time=25, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_4", parent_id="sec_3_2", title="Kadane's Algorithm (Max Subarray)", slug="kadanes-algorithm", type="topic", order_index=4, estimated_time=30, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_5", parent_id="sec_3_2", title="Print Subarray with Max Sum", slug="print-max-subarray", type="topic", order_index=5, estimated_time=30, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_6", parent_id="sec_3_2", title="Best Time to Buy & Sell Stock", slug="buy-sell-stock", type="topic", order_index=6, estimated_time=20, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_7", parent_id="sec_3_2", title="Rearrange Array Elements by Sign", slug="rearrange-array-sign", type="topic", order_index=7, estimated_time=25, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_8", parent_id="sec_3_2", title="Next Permutation", slug="next-permutation", type="topic", order_index=8, estimated_time=45, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_9", parent_id="sec_3_2", title="Leaders in an Array", slug="leaders-in-array", type="topic", order_index=9, estimated_time=25, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_10", parent_id="sec_3_2", title="Longest Consecutive Sequence", slug="longest-consecutive-sequence", type="topic", order_index=10, estimated_time=35, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_11", parent_id="sec_3_2", title="Set Matrix Zeros", slug="set-matrix-zeros", type="topic", order_index=11, estimated_time=30, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_12", parent_id="sec_3_2", title="Rotate Matrix by 90 Degrees", slug="rotate-matrix-90", type="topic", order_index=12, estimated_time=30, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_13", parent_id="sec_3_2", title="Spiral Matrix", slug="spiral-matrix", type="topic", order_index=13, estimated_time=35, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_3_2_14", parent_id="sec_3_2", title="Subarray Sum Equals K", slug="subarray-sum-k", type="topic", order_index=14, estimated_time=40, xp_reward=100, difficulty="Medium"),
            
            # Step 3 - Arrays Hard
            RoadmapNode(id="topic_3_3_1", parent_id="sec_3_3", title="Pascal's Triangle", slug="pascals-triangle", type="topic", order_index=1, estimated_time=30, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_2", parent_id="sec_3_3", title="Majority Element (>N/3)", slug="majority-element-n-3", type="topic", order_index=2, estimated_time=30, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_3", parent_id="sec_3_3", title="Three Sum", slug="three-sum", type="topic", order_index=3, estimated_time=45, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_4", parent_id="sec_3_3", title="Four Sum", slug="four-sum", type="topic", order_index=4, estimated_time=45, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_5", parent_id="sec_3_3", title="Longest Subarray with 0 Sum", slug="longest-subarray-zero-sum", type="topic", order_index=5, estimated_time=30, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_6", parent_id="sec_3_3", title="Subarrays with XOR K", slug="subarrays-xor-k", type="topic", order_index=6, estimated_time=40, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_7", parent_id="sec_3_3", title="Merge Overlapping Subintervals", slug="merge-intervals", type="topic", order_index=7, estimated_time=35, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_8", parent_id="sec_3_3", title="Merge Sorted Arrays Without Space", slug="merge-sorted-arrays", type="topic", order_index=8, estimated_time=40, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_9", parent_id="sec_3_3", title="Find Missing & Repeating Numbers", slug="find-missing-repeating", type="topic", order_index=9, estimated_time=30, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_10", parent_id="sec_3_3", title="Count Inversions", slug="count-inversions", type="topic", order_index=10, estimated_time=45, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_11", parent_id="sec_3_3", title="Reverse Pairs", slug="reverse-pairs", type="topic", order_index=11, estimated_time=45, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_3_3_12", parent_id="sec_3_3", title="Maximum Product Subarray", slug="maximum-product-subarray", type="topic", order_index=12, estimated_time=35, xp_reward=150, difficulty="Hard"),
            
            # Step 4 - BS on 1D
            RoadmapNode(id="topic_4_1_1", parent_id="sec_4_1", title="Binary Search", slug="binary-search-topic", type="topic", order_index=1, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_4_1_2", parent_id="sec_4_1", title="Implement Lower / Upper Bound", slug="lower-upper-bound", type="topic", order_index=2, estimated_time=25, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_4_1_3", parent_id="sec_4_1", title="Search Insert Position", slug="search-insert-position", type="topic", order_index=3, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_4_1_4", parent_id="sec_4_1", title="Floor / Ceil in Sorted Array", slug="floor-ceil-sorted", type="topic", order_index=4, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_4_1_5", parent_id="sec_4_1", title="First & Last Occurrences", slug="first-last-occurrences", type="topic", order_index=5, estimated_time=25, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_4_1_6", parent_id="sec_4_1", title="Count Occurrences in Sorted Array", slug="count-occurrences", type="topic", order_index=6, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_4_1_7", parent_id="sec_4_1", title="Search in Rotated Sorted Array I / II", slug="search-rotated-array", type="topic", order_index=7, estimated_time=40, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_4_1_8", parent_id="sec_4_1", title="Find Minimum in Rotated Sorted Array", slug="find-min-rotated", type="topic", order_index=8, estimated_time=30, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_4_1_9", parent_id="sec_4_1", title="Find Rotation Count", slug="find-rotation-count", type="topic", order_index=9, estimated_time=25, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_4_1_10", parent_id="sec_4_1", title="Single Element in Sorted Array", slug="single-element-sorted", type="topic", order_index=10, estimated_time=30, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_4_1_11", parent_id="sec_4_1", title="Find Peak Element", slug="find-peak-element", type="topic", order_index=11, estimated_time=30, xp_reward=50, difficulty="Easy"),
            
            # Step 4 - BS on Answers
            RoadmapNode(id="topic_4_2_1", parent_id="sec_4_2", title="Square Root of a Number", slug="square-root-bs", type="topic", order_index=1, estimated_time=25, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_2", parent_id="sec_4_2", title="Nth Root of a Number", slug="nth-root-bs", type="topic", order_index=2, estimated_time=25, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_3", parent_id="sec_4_2", title="Koko Eating Bananas", slug="koko-eating-bananas", type="topic", order_index=3, estimated_time=40, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_4", parent_id="sec_4_2", title="Minimum days to make M Bouquets", slug="min-days-bouquets", type="topic", order_index=4, estimated_time=35, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_5", parent_id="sec_4_2", title="Find the Smallest Divisor", slug="smallest-divisor-threshold", type="topic", order_index=5, estimated_time=35, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_6", parent_id="sec_4_2", title="Capacity to Ship Packages", slug="ship-packages-d-days", type="topic", order_index=6, estimated_time=35, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_7", parent_id="sec_4_2", title="Kth Missing Positive Number", slug="kth-missing-positive", type="topic", order_index=7, estimated_time=30, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_8", parent_id="sec_4_2", title="Aggressive Cows", slug="aggressive-cows", type="topic", order_index=8, estimated_time=45, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_9", parent_id="sec_4_2", title="Book Allocation Problem", slug="book-allocation", type="topic", order_index=9, estimated_time=45, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_10", parent_id="sec_4_2", title="Split Array Largest Sum", slug="split-array-largest-sum", type="topic", order_index=10, estimated_time=40, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_11", parent_id="sec_4_2", title="Painter's Partition", slug="painters-partition", type="topic", order_index=11, estimated_time=40, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_12", parent_id="sec_4_2", title="Minimise Max Distance to Gas Station", slug="minimize-max-distance-gas", type="topic", order_index=12, estimated_time=50, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_13", parent_id="sec_4_2", title="Median of Two Sorted Arrays", slug="median-two-sorted-arrays", type="topic", order_index=13, estimated_time=50, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_4_2_14", parent_id="sec_4_2", title="K-th Element of Two Sorted Arrays", slug="kth-element-two-sorted", type="topic", order_index=14, estimated_time=45, xp_reward=100, difficulty="Medium"),
            
            # Step 4 - BS on 2D
            RoadmapNode(id="topic_4_3_1", parent_id="sec_4_3", title="Find Row with Max 1s", slug="row-max-ones", type="topic", order_index=1, estimated_time=25, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_4_3_2", parent_id="sec_4_3", title="Search in a 2D Matrix I / II", slug="search-2d-matrix", type="topic", order_index=2, estimated_time=35, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_4_3_3", parent_id="sec_4_3", title="Find Peak Element in 2D Matrix", slug="peak-element-2d", type="topic", order_index=3, estimated_time=40, xp_reward=150, difficulty="Hard"),
            RoadmapNode(id="topic_4_3_4", parent_id="sec_4_3", title="Median of Row-wise Sorted Matrix", slug="median-matrix", type="topic", order_index=4, estimated_time=45, xp_reward=150, difficulty="Hard"),
            
            # Step 5 - Strings Easy
            RoadmapNode(id="topic_5_1_1", parent_id="sec_5_1", title="Remove Outermost Parentheses", slug="remove-outermost-parentheses", type="topic", order_index=1, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_5_1_2", parent_id="sec_5_1", title="Reverse Words in String", slug="reverse-words-string", type="topic", order_index=2, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_5_1_3", parent_id="sec_5_1", title="Largest Odd Number in String", slug="largest-odd-number", type="topic", order_index=3, estimated_time=15, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_5_1_4", parent_id="sec_5_1", title="Longest Common Prefix", slug="longest-common-prefix", type="topic", order_index=4, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_5_1_5", parent_id="sec_5_1", title="Isomorphic Strings", slug="isomorphic-strings", type="topic", order_index=5, estimated_time=25, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_5_1_6", parent_id="sec_5_1", title="Check if String is Rotation", slug="string-rotations", type="topic", order_index=6, estimated_time=20, xp_reward=50, difficulty="Easy"),
            RoadmapNode(id="topic_5_1_7", parent_id="sec_5_1", title="Valid Anagram", slug="valid-anagram-topic", type="topic", order_index=7, estimated_time=20, xp_reward=50, difficulty="Easy"),
            
            # Step 5 - Strings Medium
            RoadmapNode(id="topic_5_2_1", parent_id="sec_5_2", title="Sort Characters by Frequency", slug="sort-characters-frequency", type="topic", order_index=1, estimated_time=30, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_5_2_2", parent_id="sec_5_2", title="Maximum Nesting Depth of Parentheses", slug="max-nesting-depth", type="topic", order_index=2, estimated_time=20, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_5_2_3", parent_id="sec_5_2", title="Roman to Integer / Integer to Roman", slug="roman-integer-conversion", type="topic", order_index=3, estimated_time=30, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_5_2_4", parent_id="sec_5_2", title="Implement Atoi", slug="implement-atoi", type="topic", order_index=4, estimated_time=35, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_5_2_5", parent_id="sec_5_2", title="Count substrings with K distinct characters", slug="substrings-k-distinct", type="topic", order_index=5, estimated_time=45, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_5_2_6", parent_id="sec_5_2", title="Longest Palindromic Substring", slug="longest-palindromic-substring", type="topic", order_index=6, estimated_time=45, xp_reward=100, difficulty="Medium"),
            RoadmapNode(id="topic_5_2_7", parent_id="sec_5_2", title="Sum of Beauty of all substrings", slug="beauty-substrings-sum", type="topic", order_index=7, estimated_time=40, xp_reward=100, difficulty="Medium"),
        ]
        db.add_all(topics)
        db.commit()

        print("Seeding problems...")
        problems = [
            # Two Sum under Arrays Medium -> Two Sum Topic
            Problem(
                id="two-sum",
                parent_id="topic_3_2_1",
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
                parent_id="topic_3_2_4",
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
                parent_id="topic_2_1_2",
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
                parent_id="topic_2_2_2",
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
                parent_id="topic_4_1_1",
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
                parent_id="topic_5_1_7",
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

        # Seed default AI Settings & Adaptive Preferences for mock_user_striver
        from app.models.adaptive import UserPreferences, DailyStudyPlan, LearningRecommendation, LearningInsight
        db.query(LearningRecommendation).delete()
        db.query(DailyStudyPlan).delete()
        db.query(UserPreferences).delete()
        db.commit()

        user = db.query(User).filter(User.clerk_id == "mock_user_striver").first()
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
            db.commit()

        print("Database seeded successfully with AI Mentor Foundation & Adaptive Learning Engine!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()

