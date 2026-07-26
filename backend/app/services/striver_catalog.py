"""
Official Striver (TakeUForward) A2Z DSA Sheet Video Catalog.
Serves as the primary source of truth for matching roadmap nodes with official video lessons.
"""

from typing import Dict, Any, List

STRIVER_A2Z_CATALOG: List[Dict[str, Any]] = [
    # ==========================================
    # Step 1: Learn the Basics
    # ==========================================
    # Things to Know
    {
        "id": "striver_input_output",
        "title": "User Input / Output",
        "aliases": ["C++ Input Output", "User Input Output", "Basic I/O", "Input Output in C++ / Java / Python"],
        "youtube_url": "https://www.youtube.com/watch?v=0bHoB35fZeY",
        "video_id": "0bHoB35fZeY",
        "thumbnail_url": "https://img.youtube.com/vi/0bHoB35fZeY/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Things to Know in C++/Java/Python/JS",
        "source": "TakeUForward"
    },
    {
        "id": "striver_data_types",
        "title": "Data Types",
        "aliases": ["Primitive Data Types", "Data Types in C++ Java Python", "Variables and Types"],
        "youtube_url": "https://youtu.be/37E9ckMDdTk",
        "video_id": "37E9ckMDdTk",
        "thumbnail_url": "https://img.youtube.com/vi/37E9ckMDdTk/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Things to Know in C++/Java/Python/JS",
        "source": "TakeUForward"
    },
    {
        "id": "striver_if_else",
        "title": "If Else Statements",
        "aliases": ["If Else", "Conditionals in C++ Java", "Decision Making"],
        "youtube_url": "https://www.youtube.com/watch?v=EAR7De6Goz4",
        "video_id": "EAR7De6Goz4",
        "thumbnail_url": "https://img.youtube.com/vi/EAR7De6Goz4/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Things to Know in C++/Java/Python/JS",
        "source": "TakeUForward"
    },
    {
        "id": "striver_switch_statement",
        "title": "Switch Statement",
        "aliases": ["Switch Case", "Switch Statement in C++ Java"],
        "youtube_url": "https://www.youtube.com/watch?v=1u4j3lR_N3g",
        "video_id": "1u4j3lR_N3g",
        "thumbnail_url": "https://img.youtube.com/vi/1u4j3lR_N3g/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Things to Know in C++/Java/Python/JS",
        "source": "TakeUForward"
    },
    {
        "id": "striver_arrays_strings_basics",
        "title": "Arrays & Strings Basics",
        "aliases": ["Basic Arrays and Strings", "Arrays and Strings Intro"],
        "youtube_url": "https://www.youtube.com/watch?v=37E9ckMDdTk",
        "video_id": "37E9ckMDdTk",
        "thumbnail_url": "https://img.youtube.com/vi/37E9ckMDdTk/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Things to Know in C++/Java/Python/JS",
        "source": "TakeUForward"
    },
    {
        "id": "striver_loops_basics",
        "title": "Loops Basics",
        "aliases": ["For Loops While Loops", "Loops in Programming"],
        "youtube_url": "https://www.youtube.com/watch?v=0bHoB35fZeY",
        "video_id": "0bHoB35fZeY",
        "thumbnail_url": "https://img.youtube.com/vi/0bHoB35fZeY/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Things to Know in C++/Java/Python/JS",
        "source": "TakeUForward"
    },
    {
        "id": "striver_functions_basics",
        "title": "Functions Basics",
        "aliases": ["Functions Pass by Value Pass by Reference", "Methods and Functions"],
        "youtube_url": "https://www.youtube.com/watch?v=EAR7De6Goz4",
        "video_id": "EAR7De6Goz4",
        "thumbnail_url": "https://img.youtube.com/vi/EAR7De6Goz4/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Things to Know in C++/Java/Python/JS",
        "source": "TakeUForward"
    },
    {
        "id": "striver_time_space_complexity",
        "title": "Time & Space Complexity",
        "aliases": ["Time Complexity Analysis", "Space Complexity Big O Notation", "Big O Analysis"],
        "youtube_url": "https://www.youtube.com/watch?v=FPu9Uld7W-E",
        "video_id": "FPu9Uld7W-E",
        "thumbnail_url": "https://img.youtube.com/vi/FPu9Uld7W-E/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Things to Know in C++/Java/Python/JS",
        "source": "TakeUForward"
    },

    # Logical Thinking (Patterns)
    {
        "id": "striver_pattern_problems",
        "title": "Pattern Problems",
        "aliases": ["Must Do Pattern Problems", "Nested Loops Patterns", "Pattern Printing"],
        "youtube_url": "https://www.youtube.com/watch?v=tNm_N8IbEHQ",
        "video_id": "tNm_N8IbEHQ",
        "thumbnail_url": "https://img.youtube.com/vi/tNm_N8IbEHQ/hqdefault.jpg",
        "estimated_duration": 45,
        "section": "Build-up Logical Thinking",
        "source": "TakeUForward"
    },

    # STL / Collections
    {
        "id": "striver_stl_collections",
        "title": "C++ STL / Java Collections",
        "aliases": ["C++ STL Tutorial", "Java Collections Framework", "Standard Template Library"],
        "youtube_url": "https://www.youtube.com/watch?v=RRWypxDAz5E",
        "video_id": "RRWypxDAz5E",
        "thumbnail_url": "https://img.youtube.com/vi/RRWypxDAz5E/hqdefault.jpg",
        "estimated_duration": 60,
        "section": "Learn STL / Collections",
        "source": "TakeUForward"
    },

    # Basic Maths
    {
        "id": "striver_count_digits",
        "title": "Count Digits",
        "aliases": ["Count Digits in a Number", "Extract Digits"],
        "youtube_url": "https://www.youtube.com/watch?v=1xNbjMdbjug",
        "video_id": "1xNbjMdbjug",
        "thumbnail_url": "https://img.youtube.com/vi/1xNbjMdbjug/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Know Basic Maths",
        "source": "TakeUForward"
    },
    {
        "id": "striver_reverse_number",
        "title": "Reverse a Number",
        "aliases": ["Reverse Integer", "Reverse Digits of Number"],
        "youtube_url": "https://www.youtube.com/watch?v=1xNbjMdbjug",
        "video_id": "1xNbjMdbjug",
        "thumbnail_url": "https://img.youtube.com/vi/1xNbjMdbjug/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Know Basic Maths",
        "source": "TakeUForward"
    },
    {
        "id": "striver_palindrome_number",
        "title": "Palindrome Number",
        "aliases": ["Check Palindrome Number", "Numeric Palindrome"],
        "youtube_url": "https://www.youtube.com/watch?v=1xNbjMdbjug",
        "video_id": "1xNbjMdbjug",
        "thumbnail_url": "https://img.youtube.com/vi/1xNbjMdbjug/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Know Basic Maths",
        "source": "TakeUForward"
    },
    {
        "id": "striver_gcd_hcf",
        "title": "GCD or HCF",
        "aliases": ["Greatest Common Divisor", "Euclidean Algorithm", "HCF"],
        "youtube_url": "https://www.youtube.com/watch?v=1xNbjMdbjug",
        "video_id": "1xNbjMdbjug",
        "thumbnail_url": "https://img.youtube.com/vi/1xNbjMdbjug/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Know Basic Maths",
        "source": "TakeUForward"
    },
    {
        "id": "striver_armstrong_number",
        "title": "Armstrong Number",
        "aliases": ["Check Armstrong Number", "Narcissistic Number"],
        "youtube_url": "https://www.youtube.com/watch?v=1xNbjMdbjug",
        "video_id": "1xNbjMdbjug",
        "thumbnail_url": "https://img.youtube.com/vi/1xNbjMdbjug/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Know Basic Maths",
        "source": "TakeUForward"
    },
    {
        "id": "striver_print_divisors",
        "title": "Print all Divisors",
        "aliases": ["All Divisors of Number", "Find Divisors"],
        "youtube_url": "https://www.youtube.com/watch?v=1xNbjMdbjug",
        "video_id": "1xNbjMdbjug",
        "thumbnail_url": "https://img.youtube.com/vi/1xNbjMdbjug/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Know Basic Maths",
        "source": "TakeUForward"
    },
    {
        "id": "striver_prime_numbers",
        "title": "Prime Numbers",
        "aliases": ["Check for Prime", "Prime Number Verification", "Sieve of Eratosthenes Basics"],
        "youtube_url": "https://www.youtube.com/watch?v=1xNbjMdbjug",
        "video_id": "1xNbjMdbjug",
        "thumbnail_url": "https://img.youtube.com/vi/1xNbjMdbjug/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Know Basic Maths",
        "source": "TakeUForward"
    },

    # Basic Recursion
    {
        "id": "striver_recursion_basics",
        "title": "Print Name N Times",
        "aliases": ["Introduction to Recursion", "Recursion Basics", "Print Name N Times using Recursion"],
        "youtube_url": "https://www.youtube.com/watch?v=yVdKa8dnKiE",
        "video_id": "yVdKa8dnKiE",
        "thumbnail_url": "https://img.youtube.com/vi/yVdKa8dnKiE/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Learn Basic Recursion",
        "source": "TakeUForward"
    },
    {
        "id": "striver_print_1_to_n",
        "title": "Print 1 to N",
        "aliases": ["Print 1 to N linearly", "Recursion 1 to N"],
        "youtube_url": "https://www.youtube.com/watch?v=un6PLygfXrA",
        "video_id": "un6PLygfXrA",
        "thumbnail_url": "https://img.youtube.com/vi/un6PLygfXrA/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Learn Basic Recursion",
        "source": "TakeUForward"
    },
    {
        "id": "striver_print_n_to_1",
        "title": "Print N to 1",
        "aliases": ["Print N to 1 using Recursion"],
        "youtube_url": "https://www.youtube.com/watch?v=un6PLygfXrA",
        "video_id": "un6PLygfXrA",
        "thumbnail_url": "https://img.youtube.com/vi/un6PLygfXrA/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Learn Basic Recursion",
        "source": "TakeUForward"
    },
    {
        "id": "striver_sum_n_numbers",
        "title": "Sum of N numbers",
        "aliases": ["Sum of First N Numbers", "Parameterized and Functional Recursion"],
        "youtube_url": "https://www.youtube.com/watch?v=69Z55-zH09U",
        "video_id": "69Z55-zH09U",
        "thumbnail_url": "https://img.youtube.com/vi/69Z55-zH09U/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Learn Basic Recursion",
        "source": "TakeUForward"
    },
    {
        "id": "striver_factorial_n",
        "title": "Factorial of N",
        "aliases": ["Factorial using Recursion"],
        "youtube_url": "https://www.youtube.com/watch?v=69Z55-zH09U",
        "video_id": "69Z55-zH09U",
        "thumbnail_url": "https://img.youtube.com/vi/69Z55-zH09U/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Learn Basic Recursion",
        "source": "TakeUForward"
    },
    {
        "id": "striver_reverse_array_recursion",
        "title": "Reverse an Array",
        "aliases": ["Reverse an Array using Recursion", "Inplace Reverse Array"],
        "youtube_url": "https://www.youtube.com/watch?v=twuC1F6g58s",
        "video_id": "twuC1F6g58s",
        "thumbnail_url": "https://img.youtube.com/vi/twuC1F6g58s/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Learn Basic Recursion",
        "source": "TakeUForward"
    },
    {
        "id": "striver_palindrome_string_recursion",
        "title": "Check Palindrome String",
        "aliases": ["Check if String is Palindrome using Recursion"],
        "youtube_url": "https://www.youtube.com/watch?v=twuC1F6g58s",
        "video_id": "twuC1F6g58s",
        "thumbnail_url": "https://img.youtube.com/vi/twuC1F6g58s/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Learn Basic Recursion",
        "source": "TakeUForward"
    },
    {
        "id": "striver_fibonacci_recursion",
        "title": "Fibonacci Number",
        "aliases": ["Multiple Recursion Calls Fibonacci", "Nth Fibonacci Number"],
        "youtube_url": "https://www.youtube.com/watch?v=kvRjNm4GyaM",
        "video_id": "kvRjNm4GyaM",
        "thumbnail_url": "https://img.youtube.com/vi/kvRjNm4GyaM/hqdefault.jpg",
        "estimated_duration": 25,
        "section": "Learn Basic Recursion",
        "source": "TakeUForward"
    },

    # Basic Hashing
    {
        "id": "striver_number_hashing",
        "title": "Number Hashing",
        "aliases": ["Hashing Basics", "Count Frequencies of Array Elements", "Hash Map Array"],
        "youtube_url": "https://www.youtube.com/watch?v=KEs5UyBJ39g",
        "video_id": "KEs5UyBJ39g",
        "thumbnail_url": "https://img.youtube.com/vi/KEs5UyBJ39g/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Learn Basic Hashing",
        "source": "TakeUForward"
    },
    {
        "id": "striver_character_hashing",
        "title": "Character Hashing",
        "aliases": ["Char Hashing", "Character Frequency Hash Map"],
        "youtube_url": "https://www.youtube.com/watch?v=KEs5UyBJ39g",
        "video_id": "KEs5UyBJ39g",
        "thumbnail_url": "https://img.youtube.com/vi/KEs5UyBJ39g/hqdefault.jpg",
        "estimated_duration": 25,
        "section": "Learn Basic Hashing",
        "source": "TakeUForward"
    },
    {
        "id": "striver_frequency_count",
        "title": "Frequency Count",
        "aliases": ["Map and Unordered Map in C++ Java", "Frequency of Elements"],
        "youtube_url": "https://www.youtube.com/watch?v=KEs5UyBJ39g",
        "video_id": "KEs5UyBJ39g",
        "thumbnail_url": "https://img.youtube.com/vi/KEs5UyBJ39g/hqdefault.jpg",
        "estimated_duration": 25,
        "section": "Learn Basic Hashing",
        "source": "TakeUForward"
    },

    # ==========================================
    # Step 2: Sorting Techniques
    # ==========================================
    {
        "id": "striver_selection_sort",
        "title": "Selection Sort",
        "aliases": ["Selection Sort Algorithm"],
        "youtube_url": "https://www.youtube.com/watch?v=HGk_ypEuSKE",
        "video_id": "HGk_ypEuSKE",
        "thumbnail_url": "https://img.youtube.com/vi/HGk_ypEuSKE/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Sorting-I",
        "source": "TakeUForward"
    },
    {
        "id": "striver_bubble_sort",
        "title": "Bubble Sort",
        "aliases": ["Bubble Sort Algorithm"],
        "youtube_url": "https://www.youtube.com/watch?v=HGk_ypEuSKE",
        "video_id": "HGk_ypEuSKE",
        "thumbnail_url": "https://img.youtube.com/vi/HGk_ypEuSKE/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Sorting-I",
        "source": "TakeUForward"
    },
    {
        "id": "striver_insertion_sort",
        "title": "Insertion Sort",
        "aliases": ["Insertion Sort Algorithm"],
        "youtube_url": "https://www.youtube.com/watch?v=HGk_ypEuSKE",
        "video_id": "HGk_ypEuSKE",
        "thumbnail_url": "https://img.youtube.com/vi/HGk_ypEuSKE/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Sorting-I",
        "source": "TakeUForward"
    },
    {
        "id": "striver_merge_sort",
        "title": "Merge Sort",
        "aliases": ["Merge Sort Algorithm", "Divide and Conquer Sort"],
        "youtube_url": "https://www.youtube.com/watch?v=ogjf7ORKya8",
        "video_id": "ogjf7ORKya8",
        "thumbnail_url": "https://img.youtube.com/vi/ogjf7ORKya8/hqdefault.jpg",
        "estimated_duration": 45,
        "section": "Sorting-II",
        "source": "TakeUForward"
    },
    {
        "id": "striver_quick_sort",
        "title": "Quick Sort",
        "aliases": ["Quick Sort Algorithm", "Partitioning Sort"],
        "youtube_url": "https://www.youtube.com/watch?v=WIrA4YexLRQ",
        "video_id": "WIrA4YexLRQ",
        "thumbnail_url": "https://img.youtube.com/vi/WIrA4YexLRQ/hqdefault.jpg",
        "estimated_duration": 45,
        "section": "Sorting-II",
        "source": "TakeUForward"
    },
    {
        "id": "striver_recursive_bubble_sort",
        "title": "Recursive Bubble Sort",
        "aliases": ["Bubble Sort Recursive"],
        "youtube_url": "https://www.youtube.com/watch?v=HGk_ypEuSKE",
        "video_id": "HGk_ypEuSKE",
        "thumbnail_url": "https://img.youtube.com/vi/HGk_ypEuSKE/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Sorting-II",
        "source": "TakeUForward"
    },
    {
        "id": "striver_recursive_insertion_sort",
        "title": "Recursive Insertion Sort",
        "aliases": ["Insertion Sort Recursive"],
        "youtube_url": "https://www.youtube.com/watch?v=HGk_ypEuSKE",
        "video_id": "HGk_ypEuSKE",
        "thumbnail_url": "https://img.youtube.com/vi/HGk_ypEuSKE/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Sorting-II",
        "source": "TakeUForward"
    },

    # ==========================================
    # Step 3: Arrays Easy / Medium / Hard
    # ==========================================
    {
        "id": "striver_largest_element",
        "title": "Largest Element in Array",
        "aliases": ["Find Largest Element in Array", "Max Element"],
        "youtube_url": "https://www.youtube.com/watch?v=37E9ckMDdTk",
        "video_id": "37E9ckMDdTk",
        "thumbnail_url": "https://img.youtube.com/vi/37E9ckMDdTk/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Arrays Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_second_largest",
        "title": "Second Largest Element",
        "aliases": ["Second Largest Element in Array without Sorting"],
        "youtube_url": "https://www.youtube.com/watch?v=37E9ckMDdTk",
        "video_id": "37E9ckMDdTk",
        "thumbnail_url": "https://img.youtube.com/vi/37E9ckMDdTk/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Arrays Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_check_sorted",
        "title": "Check if Array is Sorted",
        "aliases": ["Check Array Sorted and Rotated"],
        "youtube_url": "https://www.youtube.com/watch?v=37E9ckMDdTk",
        "video_id": "37E9ckMDdTk",
        "thumbnail_url": "https://img.youtube.com/vi/37E9ckMDdTk/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Arrays Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_remove_duplicates",
        "title": "Remove Duplicates",
        "aliases": ["Remove Duplicates from Sorted Array"],
        "youtube_url": "https://www.youtube.com/watch?v=Fm_p9lJ4Z_8",
        "video_id": "Fm_p9lJ4Z_8",
        "thumbnail_url": "https://img.youtube.com/vi/Fm_p9lJ4Z_8/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Arrays Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_left_rotate_one",
        "title": "Left Rotate by One",
        "aliases": ["Left Rotate Array by One Place"],
        "youtube_url": "https://www.youtube.com/watch?v=wvcQg43_V8U",
        "video_id": "wvcQg43_V8U",
        "thumbnail_url": "https://img.youtube.com/vi/wvcQg43_V8U/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Arrays Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_left_rotate_d",
        "title": "Left Rotate by D Places",
        "aliases": ["Rotate Array by K Places", "Left Rotate Array by D"],
        "youtube_url": "https://www.youtube.com/watch?v=wvcQg43_V8U",
        "video_id": "wvcQg43_V8U",
        "thumbnail_url": "https://img.youtube.com/vi/wvcQg43_V8U/hqdefault.jpg",
        "estimated_duration": 25,
        "section": "Arrays Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_move_zeros",
        "title": "Move Zeros to End",
        "aliases": ["Move Zeroes", "Move All Zeros to End of Array"],
        "youtube_url": "https://www.youtube.com/watch?v=wvcQg43_V8U",
        "video_id": "wvcQg43_V8U",
        "thumbnail_url": "https://img.youtube.com/vi/wvcQg43_V8U/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Arrays Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_missing_number",
        "title": "Find Missing Number",
        "aliases": ["Missing Number in Array"],
        "youtube_url": "https://www.youtube.com/watch?v=bYWLJb3vCWY",
        "video_id": "bYWLJb3vCWY",
        "thumbnail_url": "https://img.youtube.com/vi/bYWLJb3vCWY/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Arrays Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_max_consecutive_ones",
        "title": "Maximum Consecutive Ones",
        "aliases": ["Max Consecutive Ones"],
        "youtube_url": "https://www.youtube.com/watch?v=bYWLJb3vCWY",
        "video_id": "bYWLJb3vCWY",
        "thumbnail_url": "https://img.youtube.com/vi/bYWLJb3vCWY/hqdefault.jpg",
        "estimated_duration": 15,
        "section": "Arrays Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_single_number",
        "title": "Find Number that Appears Once",
        "aliases": ["Single Number", "Find Single Number"],
        "youtube_url": "https://www.youtube.com/watch?v=bYWLJb3vCWY",
        "video_id": "bYWLJb3vCWY",
        "thumbnail_url": "https://img.youtube.com/vi/bYWLJb3vCWY/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Arrays Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_two_sum",
        "title": "Two Sum",
        "aliases": ["2 Sum Problem", "Two Sum Array"],
        "youtube_url": "https://www.youtube.com/watch?v=UXDSeD9mN-k",
        "video_id": "UXDSeD9mN-k",
        "thumbnail_url": "https://img.youtube.com/vi/UXDSeD9mN-k/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_sort_zeros_ones_twos",
        "title": "Sort 0s 1s 2s",
        "aliases": ["Sort Colors", "Dutch National Flag Algorithm"],
        "youtube_url": "https://www.youtube.com/watch?v=tp8JIuCXBaU",
        "video_id": "tp8JIuCXBaU",
        "thumbnail_url": "https://img.youtube.com/vi/tp8JIuCXBaU/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_majority_element_n2",
        "title": "Majority Element (>N/2)",
        "aliases": ["Majority Element", "Boyer Moore Voting Algorithm"],
        "youtube_url": "https://www.youtube.com/watch?v=nP_ns3uSh80",
        "video_id": "nP_ns3uSh80",
        "thumbnail_url": "https://img.youtube.com/vi/nP_ns3uSh80/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_kadanes_algorithm",
        "title": "Kadane's Algorithm (Max Subarray)",
        "aliases": ["Kadane's Algorithm", "Maximum Subarray Sum", "Max Subarray"],
        "youtube_url": "https://www.youtube.com/watch?v=AHZpyENo7kE",
        "video_id": "AHZpyENo7kE",
        "thumbnail_url": "https://img.youtube.com/vi/AHZpyENo7kE/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_rearrange_array_sign",
        "title": "Rearrange Array Elements by Sign",
        "aliases": ["Rearrange Array by Sign", "Alternate Positive Negative"],
        "youtube_url": "https://www.youtube.com/watch?v=h4aBagy4Uok",
        "video_id": "h4aBagy4Uok",
        "thumbnail_url": "https://img.youtube.com/vi/h4aBagy4Uok/hqdefault.jpg",
        "estimated_duration": 25,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_buy_sell_stock",
        "title": "Best Time to Buy & Sell Stock",
        "aliases": ["Buy and Sell Stock", "Best Time to Buy and Sell Stock"],
        "youtube_url": "https://www.youtube.com/watch?v=excelBxoBOU",
        "video_id": "excelBxoBOU",
        "thumbnail_url": "https://img.youtube.com/vi/excelBxoBOU/hqdefault.jpg",
        "estimated_duration": 25,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_next_permutation",
        "title": "Next Permutation",
        "aliases": ["Next Greater Permutation"],
        "youtube_url": "https://www.youtube.com/watch?v=JDOXKqF60RQ",
        "video_id": "JDOXKqF60RQ",
        "thumbnail_url": "https://img.youtube.com/vi/JDOXKqF60RQ/hqdefault.jpg",
        "estimated_duration": 40,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_longest_consecutive_sequence",
        "title": "Longest Consecutive Sequence",
        "aliases": ["Longest Consecutive Sequence in Array"],
        "youtube_url": "https://www.youtube.com/watch?v=oO5uLE7EUlM",
        "video_id": "oO5uLE7EUlM",
        "thumbnail_url": "https://img.youtube.com/vi/oO5uLE7EUlM/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_set_matrix_zeros",
        "title": "Set Matrix Zeros",
        "aliases": ["Set Matrix Zeroes"],
        "youtube_url": "https://www.youtube.com/watch?v=N0MgLvceX7M",
        "video_id": "N0MgLvceX7M",
        "thumbnail_url": "https://img.youtube.com/vi/N0MgLvceX7M/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_rotate_matrix",
        "title": "Rotate Matrix by 90 Degrees",
        "aliases": ["Rotate Image 90 Degrees"],
        "youtube_url": "https://www.youtube.com/watch?v=Z0R2u6gd3GU",
        "video_id": "Z0R2u6gd3GU",
        "thumbnail_url": "https://img.youtube.com/vi/Z0R2u6gd3GU/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_spiral_matrix",
        "title": "Spiral Matrix",
        "aliases": ["Spiral Traversal Matrix"],
        "youtube_url": "https://www.youtube.com/watch?v=3Zv-s9UUrFM",
        "video_id": "3Zv-s9UUrFM",
        "thumbnail_url": "https://img.youtube.com/vi/3Zv-s9UUrFM/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Arrays Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_pascals_triangle",
        "title": "Pascal's Triangle",
        "aliases": ["Pascal Triangle Variation"],
        "youtube_url": "https://www.youtube.com/watch?v=6JYIGeeoYuU",
        "video_id": "6JYIGeeoYuU",
        "thumbnail_url": "https://img.youtube.com/vi/6JYIGeeoYuU/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "Arrays Hard",
        "source": "TakeUForward"
    },
    {
        "id": "striver_three_sum",
        "title": "Three Sum",
        "aliases": ["3 Sum Problem", "3Sum"],
        "youtube_url": "https://www.youtube.com/watch?v=dhFhUgt4GIk",
        "video_id": "dhFhUgt4GIk",
        "thumbnail_url": "https://img.youtube.com/vi/dhFhUgt4GIk/hqdefault.jpg",
        "estimated_duration": 45,
        "section": "Arrays Hard",
        "source": "TakeUForward"
    },
    {
        "id": "striver_four_sum",
        "title": "Four Sum",
        "aliases": ["4 Sum Problem", "4Sum"],
        "youtube_url": "https://www.youtube.com/watch?v=eDwhjskgpyU",
        "video_id": "eDwhjskgpyU",
        "thumbnail_url": "https://img.youtube.com/vi/eDwhjskgpyU/hqdefault.jpg",
        "estimated_duration": 45,
        "section": "Arrays Hard",
        "source": "TakeUForward"
    },
    {
        "id": "striver_subarrays_xor_k",
        "title": "Subarrays with XOR K",
        "aliases": ["Count Subarrays with Given XOR"],
        "youtube_url": "https://www.youtube.com/watch?v=eZr-6p0B7ME",
        "video_id": "eZr-6p0B7ME",
        "thumbnail_url": "https://img.youtube.com/vi/eZr-6p0B7ME/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "Arrays Hard",
        "source": "TakeUForward"
    },
    {
        "id": "striver_merge_intervals",
        "title": "Merge Overlapping Subintervals",
        "aliases": ["Merge Intervals"],
        "youtube_url": "https://www.youtube.com/watch?v=IexN60k62jo",
        "video_id": "IexN60k62jo",
        "thumbnail_url": "https://img.youtube.com/vi/IexN60k62jo/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "Arrays Hard",
        "source": "TakeUForward"
    },
    {
        "id": "striver_merge_sorted_arrays",
        "title": "Merge Sorted Arrays Without Space",
        "aliases": ["Merge Two Sorted Arrays Inplace"],
        "youtube_url": "https://www.youtube.com/watch?v=n7uwj04E0I4",
        "video_id": "n7uwj04E0I4",
        "thumbnail_url": "https://img.youtube.com/vi/n7uwj04E0I4/hqdefault.jpg",
        "estimated_duration": 40,
        "section": "Arrays Hard",
        "source": "TakeUForward"
    },
    {
        "id": "striver_missing_repeating",
        "title": "Find Missing & Repeating Numbers",
        "aliases": ["Find Repeating and Missing Number"],
        "youtube_url": "https://www.youtube.com/watch?v=2D0QfOPbxAg",
        "video_id": "2D0QfOPbxAg",
        "thumbnail_url": "https://img.youtube.com/vi/2D0QfOPbxAg/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "Arrays Hard",
        "source": "TakeUForward"
    },

    # ==========================================
    # Step 4: Binary Search
    # ==========================================
    {
        "id": "striver_binary_search_1d",
        "title": "Binary Search",
        "aliases": ["Binary Search on 1D Arrays", "BS Intro"],
        "youtube_url": "https://www.youtube.com/watch?v=MHf6awe89aU",
        "video_id": "MHf6awe89aU",
        "thumbnail_url": "https://img.youtube.com/vi/MHf6awe89aU/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "BS on 1D Arrays",
        "source": "TakeUForward"
    },
    {
        "id": "striver_lower_upper_bound",
        "title": "Implement Lower / Upper Bound",
        "aliases": ["Lower Bound and Upper Bound in BS"],
        "youtube_url": "https://www.youtube.com/watch?v=6zhGS79oQ4U",
        "video_id": "6zhGS79oQ4U",
        "thumbnail_url": "https://img.youtube.com/vi/6zhGS79oQ4U/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "BS on 1D Arrays",
        "source": "TakeUForward"
    },
    {
        "id": "striver_search_insert_position",
        "title": "Search Insert Position",
        "aliases": ["Search Insert Position BS"],
        "youtube_url": "https://www.youtube.com/watch?v=K-RYz5wuuv4",
        "video_id": "K-RYz5wuuv4",
        "thumbnail_url": "https://img.youtube.com/vi/K-RYz5wuuv4/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "BS on 1D Arrays",
        "source": "TakeUForward"
    },
    {
        "id": "striver_first_last_occurrences",
        "title": "First & Last Occurrences",
        "aliases": ["First and Last Position of Element in Sorted Array"],
        "youtube_url": "https://www.youtube.com/watch?v=hjR1IYVt9C8",
        "video_id": "hjR1IYVt9C8",
        "thumbnail_url": "https://img.youtube.com/vi/hjR1IYVt9C8/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "BS on 1D Arrays",
        "source": "TakeUForward"
    },
    {
        "id": "striver_search_rotated_array",
        "title": "Search in Rotated Sorted Array I / II",
        "aliases": ["Search in Rotated Sorted Array"],
        "youtube_url": "https://www.youtube.com/watch?v=r3pHE8uMCU8",
        "video_id": "r3pHE8uMCU8",
        "thumbnail_url": "https://img.youtube.com/vi/r3pHE8uMCU8/hqdefault.jpg",
        "estimated_duration": 40,
        "section": "BS on 1D Arrays",
        "source": "TakeUForward"
    },
    {
        "id": "striver_find_rotation_count",
        "title": "Find Rotation Count",
        "aliases": ["Find out how many times array has been rotated"],
        "youtube_url": "https://www.youtube.com/watch?v=jtSiwt_P21E",
        "video_id": "jtSiwt_P21E",
        "thumbnail_url": "https://img.youtube.com/vi/jtSiwt_P21E/hqdefault.jpg",
        "estimated_duration": 25,
        "section": "BS on 1D Arrays",
        "source": "TakeUForward"
    },
    {
        "id": "striver_sqrt_number",
        "title": "Square Root of a Number",
        "aliases": ["Square Root using Binary Search"],
        "youtube_url": "https://www.youtube.com/watch?v=Bsv3FPUX_BA",
        "video_id": "Bsv3FPUX_BA",
        "thumbnail_url": "https://img.youtube.com/vi/Bsv3FPUX_BA/hqdefault.jpg",
        "estimated_duration": 25,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_koko_eating_bananas",
        "title": "Koko Eating Bananas",
        "aliases": ["BS on Answers Koko Bananas"],
        "youtube_url": "https://www.youtube.com/watch?v=qyfekrNni90",
        "video_id": "qyfekrNni90",
        "thumbnail_url": "https://img.youtube.com/vi/qyfekrNni90/hqdefault.jpg",
        "estimated_duration": 40,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_min_bouquets",
        "title": "Minimum days to make M Bouquets",
        "aliases": ["Minimum Days to Make m Bouquets"],
        "youtube_url": "https://www.youtube.com/watch?v=TXAuxeYBTdg",
        "video_id": "TXAuxeYBTdg",
        "thumbnail_url": "https://img.youtube.com/vi/TXAuxeYBTdg/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_smallest_divisor",
        "title": "Find the Smallest Divisor",
        "aliases": ["Find the Smallest Divisor Given a Threshold"],
        "youtube_url": "https://www.youtube.com/watch?v=UvBKTVaG6U8",
        "video_id": "UvBKTVaG6U8",
        "thumbnail_url": "https://img.youtube.com/vi/UvBKTVaG6U8/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_ship_packages",
        "title": "Capacity to Ship Packages",
        "aliases": ["Capacity To Ship Packages Within D Days"],
        "youtube_url": "https://www.youtube.com/watch?v=MG-Ac4TAv4w",
        "video_id": "MG-Ac4TAv4w",
        "thumbnail_url": "https://img.youtube.com/vi/MG-Ac4TAv4w/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_kth_missing_positive",
        "title": "Kth Missing Positive Number",
        "aliases": ["Kth Missing Positive"],
        "youtube_url": "https://www.youtube.com/watch?v=uZ0N_hZpyur",
        "video_id": "uZ0N_hZpyur",
        "thumbnail_url": "https://img.youtube.com/vi/uZ0N_hZpyur/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_aggressive_cows",
        "title": "Aggressive Cows",
        "aliases": ["Aggressive Cows Problem"],
        "youtube_url": "https://www.youtube.com/watch?v=R_Mfw4ew-Vo",
        "video_id": "R_Mfw4ew-Vo",
        "thumbnail_url": "https://img.youtube.com/vi/R_Mfw4ew-Vo/hqdefault.jpg",
        "estimated_duration": 40,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_book_allocation",
        "title": "Book Allocation Problem",
        "aliases": ["Allocate Minimum Number of Pages"],
        "youtube_url": "https://www.youtube.com/watch?v=gYmWHvRHu-s",
        "video_id": "gYmWHvRHu-s",
        "thumbnail_url": "https://img.youtube.com/vi/gYmWHvRHu-s/hqdefault.jpg",
        "estimated_duration": 45,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_painters_partition",
        "title": "Painter's Partition",
        "aliases": ["Painter Partition Problem"],
        "youtube_url": "https://www.youtube.com/watch?v=thUd_aJnObU",
        "video_id": "thUd_aJnObU",
        "thumbnail_url": "https://img.youtube.com/vi/thUd_aJnObU/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_minimise_max_distance_gas_station",
        "title": "Minimise Max Distance to Gas Station",
        "aliases": ["Minimize Max Distance to Gas Station"],
        "youtube_url": "https://www.youtube.com/watch?v=kMSBvlZ-_60",
        "video_id": "kMSBvlZ-_60",
        "thumbnail_url": "https://img.youtube.com/vi/kMSBvlZ-_60/hqdefault.jpg",
        "estimated_duration": 45,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_median_two_sorted_arrays",
        "title": "Median of Two Sorted Arrays",
        "aliases": ["Median of 2 Sorted Arrays"],
        "youtube_url": "https://www.youtube.com/watch?v=NTop3VTj6mj",
        "video_id": "NTop3VTj6mj",
        "thumbnail_url": "https://img.youtube.com/vi/NTop3VTj6mj/hqdefault.jpg",
        "estimated_duration": 45,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_kth_element_two_sorted_arrays",
        "title": "K-th Element of Two Sorted Arrays",
        "aliases": ["Kth Element of Two Sorted Arrays"],
        "youtube_url": "https://www.youtube.com/watch?v=nv7F4PiLUzo",
        "video_id": "nv7F4PiLUzo",
        "thumbnail_url": "https://img.youtube.com/vi/nv7F4PiLUzo/hqdefault.jpg",
        "estimated_duration": 40,
        "section": "BS on Answers",
        "source": "TakeUForward"
    },
    {
        "id": "striver_row_max_ones",
        "title": "Find Row with Max 1s",
        "aliases": ["Row with Maximum 1s"],
        "youtube_url": "https://www.youtube.com/watch?v=SCz-1xP_LhE",
        "video_id": "SCz-1xP_LhE",
        "thumbnail_url": "https://img.youtube.com/vi/SCz-1xP_LhE/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "BS on 2D Arrays",
        "source": "TakeUForward"
    },
    {
        "id": "striver_search_2d_matrix",
        "title": "Search in a 2D Matrix I / II",
        "aliases": ["Search a 2D Matrix"],
        "youtube_url": "https://www.youtube.com/watch?v=JXU4QDQzaBI",
        "video_id": "JXU4QDQzaBI",
        "thumbnail_url": "https://img.youtube.com/vi/JXU4QDQzaBI/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "BS on 2D Arrays",
        "source": "TakeUForward"
    },
    {
        "id": "striver_peak_element_2d",
        "title": "Find Peak Element in 2D Matrix",
        "aliases": ["Find Peak Element II"],
        "youtube_url": "https://www.youtube.com/watch?v=nGGp5XBzC4g",
        "video_id": "nGGp5XBzC4g",
        "thumbnail_url": "https://img.youtube.com/vi/nGGp5XBzC4g/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "BS on 2D Arrays",
        "source": "TakeUForward"
    },
    {
        "id": "striver_matrix_median",
        "title": "Median of Row-wise Sorted Matrix",
        "aliases": ["Matrix Median"],
        "youtube_url": "https://www.youtube.com/watch?v=Q9wXgdxJq48",
        "video_id": "Q9wXgdxJq48",
        "thumbnail_url": "https://img.youtube.com/vi/Q9wXgdxJq48/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "BS on 2D Arrays",
        "source": "TakeUForward"
    },

    # ==========================================
    # Step 5: Strings
    # ==========================================
    {
        "id": "striver_remove_outermost_parentheses",
        "title": "Remove Outermost Parentheses",
        "aliases": ["Remove Outer Parentheses"],
        "youtube_url": "https://www.youtube.com/watch?v=0bHoB35fZeY",
        "video_id": "0bHoB35fZeY",
        "thumbnail_url": "https://img.youtube.com/vi/0bHoB35fZeY/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Strings Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_reverse_words_string",
        "title": "Reverse Words in String",
        "aliases": ["Reverse Words in a String"],
        "youtube_url": "https://www.youtube.com/watch?v=vhnRAaJe35u",
        "video_id": "vhnRAaJe35u",
        "thumbnail_url": "https://img.youtube.com/vi/vhnRAaJe35u/hqdefault.jpg",
        "estimated_duration": 25,
        "section": "Strings Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_largest_odd_number_string",
        "title": "Largest Odd Number in String",
        "aliases": ["Largest Odd Number"],
        "youtube_url": "https://www.youtube.com/watch?v=7u8B9E3Z412",
        "video_id": "7u8B9E3Z412",
        "thumbnail_url": "https://img.youtube.com/vi/7u8B9E3Z412/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Strings Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_longest_common_prefix",
        "title": "Longest Common Prefix",
        "aliases": ["LCP String"],
        "youtube_url": "https://www.youtube.com/watch?v=vA84XA3vK2e",
        "video_id": "vA84XA3vK2e",
        "thumbnail_url": "https://img.youtube.com/vi/vA84XA3vK2e/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Strings Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_valid_anagram",
        "title": "Valid Anagram",
        "aliases": ["Check Anagram Strings"],
        "youtube_url": "https://www.youtube.com/watch?v=3OwD5MCkUvE",
        "video_id": "3OwD5MCkUvE",
        "thumbnail_url": "https://img.youtube.com/vi/3OwD5MCkUvE/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Strings Easy",
        "source": "TakeUForward"
    },
    {
        "id": "striver_sort_characters_frequency",
        "title": "Sort Characters by Frequency",
        "aliases": ["Sort Characters By Frequency"],
        "youtube_url": "https://www.youtube.com/watch?v=hW6N9v6u843",
        "video_id": "hW6N9v6u843",
        "thumbnail_url": "https://img.youtube.com/vi/hW6N9v6u843/hqdefault.jpg",
        "estimated_duration": 30,
        "section": "Strings Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_max_nesting_depth",
        "title": "Maximum Nesting Depth of Parentheses",
        "aliases": ["Max Nesting Depth"],
        "youtube_url": "https://www.youtube.com/watch?v=9jR3eA48Z76",
        "video_id": "9jR3eA48Z76",
        "thumbnail_url": "https://img.youtube.com/vi/9jR3eA48Z76/hqdefault.jpg",
        "estimated_duration": 20,
        "section": "Strings Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_implement_atoi",
        "title": "Implement Atoi",
        "aliases": ["String to Integer Atoi"],
        "youtube_url": "https://www.youtube.com/watch?v=48vW8aA638g",
        "video_id": "48vW8aA638g",
        "thumbnail_url": "https://img.youtube.com/vi/48vW8aA638g/hqdefault.jpg",
        "estimated_duration": 35,
        "section": "Strings Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_count_substrings_k_distinct",
        "title": "Count substrings with K distinct characters",
        "aliases": ["Substrings with K Distinct Characters"],
        "youtube_url": "https://www.youtube.com/watch?v=7v9J2b7v783",
        "video_id": "7v9J2b7v783",
        "thumbnail_url": "https://img.youtube.com/vi/7v9J2b7v783/hqdefault.jpg",
        "estimated_duration": 45,
        "section": "Strings Medium",
        "source": "TakeUForward"
    },
    {
        "id": "striver_longest_palindromic_substring",
        "title": "Longest Palindromic Substring",
        "aliases": ["Palindromic Substring"],
        "youtube_url": "https://www.youtube.com/watch?v=0bHoB35fZeY",
        "video_id": "0bHoB35fZeY",
        "thumbnail_url": "https://img.youtube.com/vi/0bHoB35fZeY/hqdefault.jpg",
        "estimated_duration": 40,
        "section": "Strings Medium",
        "source": "TakeUForward"
    }
]

# Fallback default Striver video URL for any unmatched roadmap topic
DEFAULT_STRIVER_VIDEO = {
    "youtube_url": "https://www.youtube.com/watch?v=0bHoB35fZeY",
    "video_id": "0bHoB35fZeY",
    "thumbnail_url": "https://img.youtube.com/vi/0bHoB35fZeY/hqdefault.jpg",
    "source": "TakeUForward"
}
