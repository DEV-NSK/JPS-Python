"""
Run with: python manage.py shell < scripts/seed_coding_problems.py
Or: python manage.py runscript seed_coding_problems (with django-extensions)
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_backend.settings')
django.setup()

from features.models import CodingProblem

PROBLEMS = [
    {
        'title': 'Two Sum',
        'slug': 'two-sum',
        'difficulty': 'Easy',
        'topic': 'Arrays',
        'company': 'Google',
        'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
        'examples': [{'input': 'nums = [2,7,11,15], target = 9', 'output': '[0,1]', 'explanation': 'nums[0] + nums[1] = 2 + 7 = 9'}],
        'constraints': ['2 <= nums.length <= 10^4', '-10^9 <= nums[i] <= 10^9'],
        'starter_code': {
            'python': 'def twoSum(nums, target):\n    pass',
            'javascript': 'var twoSum = function(nums, target) {\n    \n};',
        },
        'test_cases': [{'input': '[2,7,11,15]\n9', 'expectedOutput': '[0,1]'}],
        'xp': 10,
        'tags': ['array', 'hash-table'],
    },
    {
        'title': 'Valid Parentheses',
        'slug': 'valid-parentheses',
        'difficulty': 'Easy',
        'topic': 'Stack',
        'company': 'Amazon',
        'description': 'Given a string s containing just the characters (, ), {, }, [ and ], determine if the input string is valid.',
        'examples': [{'input': 's = "()"', 'output': 'true'}, {'input': 's = "()[]{}"', 'output': 'true'}],
        'constraints': ['1 <= s.length <= 10^4'],
        'starter_code': {
            'python': 'def isValid(s):\n    pass',
            'javascript': 'var isValid = function(s) {\n    \n};',
        },
        'test_cases': [{'input': '()', 'expectedOutput': 'true'}],
        'xp': 10,
        'tags': ['stack', 'string'],
    },
    {
        'title': 'Longest Substring Without Repeating Characters',
        'slug': 'longest-substring-without-repeating',
        'difficulty': 'Medium',
        'topic': 'Sliding Window',
        'company': 'Microsoft',
        'description': 'Given a string s, find the length of the longest substring without repeating characters.',
        'examples': [{'input': 's = "abcabcbb"', 'output': '3', 'explanation': 'The answer is "abc", with the length of 3.'}],
        'constraints': ['0 <= s.length <= 5 * 10^4'],
        'starter_code': {
            'python': 'def lengthOfLongestSubstring(s):\n    pass',
            'javascript': 'var lengthOfLongestSubstring = function(s) {\n    \n};',
        },
        'test_cases': [{'input': 'abcabcbb', 'expectedOutput': '3'}],
        'xp': 20,
        'tags': ['hash-table', 'string', 'sliding-window'],
    },
    {
        'title': 'Merge K Sorted Lists',
        'slug': 'merge-k-sorted-lists',
        'difficulty': 'Hard',
        'topic': 'Linked List',
        'company': 'Facebook',
        'description': 'You are given an array of k linked-lists lists, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.',
        'examples': [{'input': 'lists = [[1,4,5],[1,3,4],[2,6]]', 'output': '[1,1,2,3,4,4,5,6]'}],
        'constraints': ['k == lists.length', '0 <= k <= 10^4'],
        'starter_code': {
            'python': 'def mergeKLists(lists):\n    pass',
            'javascript': 'var mergeKLists = function(lists) {\n    \n};',
        },
        'test_cases': [{'input': '[[1,4,5],[1,3,4],[2,6]]', 'expectedOutput': '[1,1,2,3,4,4,5,6]'}],
        'xp': 30,
        'tags': ['linked-list', 'divide-and-conquer', 'heap'],
    },
    {
        'title': 'Binary Search',
        'slug': 'binary-search',
        'difficulty': 'Easy',
        'topic': 'Binary Search',
        'company': 'Apple',
        'description': 'Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums.',
        'examples': [{'input': 'nums = [-1,0,3,5,9,12], target = 9', 'output': '4'}],
        'constraints': ['1 <= nums.length <= 10^4'],
        'starter_code': {
            'python': 'def search(nums, target):\n    pass',
            'javascript': 'var search = function(nums, target) {\n    \n};',
        },
        'test_cases': [{'input': '[-1,0,3,5,9,12]\n9', 'expectedOutput': '4'}],
        'xp': 10,
        'tags': ['array', 'binary-search'],
    },
    {
        'title': 'Maximum Subarray',
        'slug': 'maximum-subarray',
        'difficulty': 'Medium',
        'topic': 'Dynamic Programming',
        'company': 'Google',
        'description': 'Given an integer array nums, find the subarray with the largest sum, and return its sum.',
        'examples': [{'input': 'nums = [-2,1,-3,4,-1,2,1,-5,4]', 'output': '6', 'explanation': 'The subarray [4,-1,2,1] has the largest sum 6.'}],
        'constraints': ['1 <= nums.length <= 10^5'],
        'starter_code': {
            'python': 'def maxSubArray(nums):\n    pass',
            'javascript': 'var maxSubArray = function(nums) {\n    \n};',
        },
        'test_cases': [{'input': '[-2,1,-3,4,-1,2,1,-5,4]', 'expectedOutput': '6'}],
        'xp': 20,
        'tags': ['array', 'dynamic-programming', 'divide-and-conquer'],
    },
]

created = 0
for p in PROBLEMS:
    obj, was_created = CodingProblem.objects.get_or_create(slug=p['slug'], defaults=p)
    if was_created:
        created += 1
        print(f"  Created: {obj.title}")
    else:
        print(f"  Exists:  {obj.title}")

print(f"\nDone. {created} new problems created.")
