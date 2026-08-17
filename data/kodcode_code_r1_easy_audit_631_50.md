# KodCode Easy Manual Audit Sample

Total sampled: 50

Flagged by heuristic: 14

## 01. Algorithm_2880_I `recursive_binary_search` split=sft_prompts subset=Algorithm

- prompt_chars: 2439
- solution_chars: 501
- tests: public=2 hidden=7
- flags: ['keyword_complexity']

```text
Problem:
### Implementing a Recursive Binary Search

You are tasked with implementing a recursive binary search function in Python. This function should take a sorted list and a target value, returning the index of the target value within the list, or `-1` if the target does not exist in the list.

#### Function Signature
```python
def recursive_binary_search(sorted_list: list, target: int, left: int = 0, right: int = None) -> int:
```

#### Parameters:
- `sorted_list` (list): A list of integers sorted in ascending order.
- `target` (int): The integer value to search for within the list.
- `left` (int, optional): The left boundary of the search interval. Defaults to 0.
- `right` (int, optional): The right boundary of the search interval. Defaults to `None`, which should be interpreted as `len(sorted_list) - 1`.

#### Returns:
- `int`: The index of the target within the list if found, otherwise `-1`.

### Requirements:
1. If `right` is `None` at the initial call, set it to the length of the list minus one.
2. Perform a recursive binary search using the middle element of the interval.
3. Ensure the function returns the correct index of the target if found.
4. Handle the case where the target is not found by returning `-1`.

### Constraints:
- Input list length: \( 1 \le \text{len(sorted_list)} \le 10^5 \)
- Values in the sorted list and target: \( -10^9 \le \text{target}, \text{value in sorted_list} \le 10^9 \)

### Example Usage:
```python
sorted_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

print(recursive_binary_search(sorted_list, 5))    # 4
print(recursive_binary_search(sorted
...(truncated 422 chars)
```

## 02. Taco_73793_I `fizz_buzz_transform` split=sft_prompts subset=Taco

- prompt_chars: 2066
- solution_chars: 858
- tests: public=2 hidden=8
- flags: ['looks_easy']

```text
Problem:
Implement a function that takes a list of positive integers and returns a list where each integer transformation is done according to the following rules:

1. If the integer is divisible by 3, replace it with the string "Fizz".
2. If the integer is divisible by 5, replace it with the string "Buzz".
3. If the integer is divisible by both 3 and 5, replace it with the string "FizzBuzz".
4. Otherwise, the integer remains unchanged.

The function signature is defined as:

```python
def fizz_buzz_transform(numbers: List[int]) -> List[Union[int, str]]:
    pass
```

**Example:**
```python
input_list = [1, 3, 5, 15, 22, 30]
fizz_buzz_transform(input_list)
```

**Output:**
```
[1, 'Fizz', 'Buzz', 'FizzBuzz', 22, 'FizzBuzz']
```

**Explanation:**

- 1 is not divisible by 3 or 5, so it remains unchanged.
- 3 is divisible by 3, so it is replaced by "Fizz".
- 5 is divisible by 5, so it is replaced by "Buzz".
- 15 is divisible by both 3 and 5, so it is replaced by "FizzBuzz".
- 22 is not divisible by 3 or 5, so it remains unchanged.
- 30 is divisible by both 3 and 5, so it is replaced by "FizzBuzz".

Implement callable `fizz_buzz_transform`.
Function declaration: `def fizz_buzz_transform(numbers):`

Docstring:
Transforms a list of positive integers according to the FizzBuzz rules.

Args:
- numbers: List[int] : A list of positive integers.

Returns:
- List[Union[int, str]] : A list where each integer is replaced by:
  - 'Fizz' if divisible by 3
  - 'Buzz' if divisible by 5
  - 'FizzBuzz' if divisible by both 3 and 5
  - The integer itself if none of the above conditions are met
```

## 03. Filter_54856_I `average` split=sft_prompts subset=Filter

- prompt_chars: 724
- solution_chars: 202
- tests: public=2 hidden=6
- flags: ['looks_easy']

```text
Problem:
Create a function in Python that takes a list of integers and returns the average of the numbers in the list. The function should handle an empty list by returning 0.0.

Implement callable `average`.
Function declaration: `def average(numbers):`

Docstring:
Returns the average of a list of numbers. 
If the list is empty, returns 0.0.
```

## 04. Algorithm_1690_I `is_perfect_square` split=grpo subset=Algorithm

- prompt_chars: 1693
- solution_chars: 477
- tests: public=2 hidden=13
- flags: ['looks_easy']

```text
Problem:
### Problem Statement
A perfect square is an integer that is the square of some integer. For example, 1, 4, 9, and 16 are perfect squares because:
- 1 = 1 * 1
- 4 = 2 * 2
- 9 = 3 * 3
- 16 = 4 * 4

Write a function `is_perfect_square` that takes an integer `x` as input and returns `True` if the number is a perfect square, otherwise returns `False`. The function should handle edge cases, such as when `x` is zero or negative gracefully.

#### Input Format
- An integer `x` which needs to be checked if it is a perfect square.

#### Output Format
- A boolean value: `True` if `x` is a perfect square, otherwise `False`.

#### Constraints
- The function should be efficient and handle up to large values of `x` within practical limits.
- You are not allowed to use the `sqrt` function from Python's math module.

#### Example
```python
assert is_perfect_square(16) == True
assert is_perfect_square(14) == False
assert is_perfect_square(1) == True
assert is_perfect_square(0) == True
assert is_perfect_square(-4) == False
assert is_perfect_square(25) == True
assert is_perfect_square(26) == False
```

Implement callable `is_perfect_square`.
Function declaration: `def is_perfect_square(x):`

Docstring:
Returns True if x is a perfect square, otherwise False.
Handles edge cases for zero and negative numbers.
```

## 05. Filter_83677_I `reverse_string` split=sft_prompts subset=Filter

- prompt_chars: 765
- solution_chars: 164
- tests: public=2 hidden=4
- flags: ['looks_easy']

```text
Problem:
This code defines a function to reverse a string:

```python
def reverse_string(s):
"""Reverses a string.

Args:
  s: The string to reverse.

Returns:
  The reversed string.
"""
  return s[::-1]

Implement callable `reverse_string`.
Function declaration: `def reverse_string(s):`

Docstring:
Reverses a string.

Args:
  s: The string to reverse.

Returns:
  The reversed string.
```

## 06. Apps_10100_I `rotate_list` split=sft_prompts subset=Apps

- prompt_chars: 1297
- solution_chars: 458
- tests: public=2 hidden=7
- flags: ['looks_easy']

```text
Problem:
You have a list of integers and an integer `k`. Your task is to rotate the list to the right by `k` steps, where `k` is non-negative. The rotation means that the final elements of the array become the first elements of the array. 

Write a function to perform this operation and return the new list.

## Function Signature
```python
def rotate_list(nums: List[int], k: int) -> List[int]:
    # Your code here
```

## Example
```
rotate_list([1, 2, 3, 4, 5], 2)  -->  [4, 5, 1, 2, 3]
rotate_list([0, 1, 2], 4)  -->  [2, 0, 1]
rotate_list([-1, -100, 3, 99], 2)  -->  [3, 99, -1, -100]
```

Implement callable `rotate_list`.
Function declaration: `def rotate_list(nums, k):`

Docstring:
Rotates the list to the right by k steps.

Parameters:
  nums (List[int]): List of integers to be rotated.
  k (int): Number of steps to rotate the list.
  
Returns:
  List[int]: The rotated list.
```

## 07. Data_Structure_15500_I `enhanced_rabin_karp` split=sft_prompts subset=Data_Structure

- prompt_chars: 2252
- solution_chars: 1556
- tests: public=2 hidden=10
- flags: ['looks_easy']

```text
Problem:
### Rabin-Karp Algorithm Enhancement

**Context**:
You are tasked with improving a plagiarism detection system that relies on the Rabin-Karp algorithm for string matching. The current implementation is encountering an unexpected number of hash collisions, leading to inefficient performance. Your goal is to re-implement the algorithm to reduce hash collisions and optimize performance.

#### Problem Statement
Write a modified version of the Rabin-Karp algorithm that:
1. Utilizes a large prime number as the modulus operator in the hash calculations.
2. Ensures efficient handling of edge cases such as empty strings or non-matching words.
3. Minimizes hash collisions by adjusting the base of the hash function.

#### Input and Output
- **Input**: Two strings, `word` (the string to search for) and `text` (the string to search within).
- **Output**: The starting index of the first occurrence of `word` in `text`, or `None` if the `word` is not found.

#### Constraints
- Assume all strings consist of lowercase English letters.
- Length of both `word` and `text` \( \leq 10^5 \).

#### Example
```python
def enhanced_rabin_karp(word: str, text: str) -> int:
    # Your code here

# Example input
print(enhanced_rabin_karp("abc", "abxabcabcaby"))  # Output should be 3
print(enhanced_rabin_karp("abc", "defghijklmnopqrst"))  # Output should be None
```

#### Requirements
1. Implement the Rabin-Karp algorithm using a large prime number (e.g., 101).
2. Ensure you handle all edge cases correctly.
3. The solution must be efficient and minimize hash collisions.

Implement callable `enhan
...(truncated 230 chars)
```

## 08. Filter_17958_I `find_first_duplicate` split=grpo subset=Filter

- prompt_chars: 1115
- solution_chars: 136
- tests: public=2 hidden=3
- flags: ['looks_easy']

```text
Problem:
I have one-dimensional array of integers. I need to find the first duplicate in the array. 
The array is not empty, contains only positive integers and can contain duplicates.
Array length can be up to 10^6 elements.  
Example: for arr = [2,1,3,5,3,2] first duplicate is 3.

My current solution is:

```python
def find_first_duplicate(arr):
    seen = set()
    for num in arr:
        if num in seen:
            return num
        seen.add(num)
    return None  # this will never happen according to the problem description
```

What are the problems with the solution and how can it improve it?

Implement callable `find_first_duplicate`.
Function declaration: `def find_first_duplicate(arr):`
```

## 09. Apps_3549_I `fibonacci` split=eval subset=Apps

- prompt_chars: 1097
- solution_chars: 489
- tests: public=2 hidden=2
- flags: ['few_hidden_tests']

```text
Problem:
Write a function that accepts an integer `n` as input and returns a list containing the fibonacci sequence up to the `n`th term.

# Requirements
- Your function should handle values of `n` >= 1.
- The fibonacci sequence is defined as:
  - The first two numbers are 0 and 1.
  - Each subsequent number is the sum of the previous two.
  
# Notes
- Implement an efficient solution that avoids unnecessary computations.

Implement callable `fibonacci`.
Function declaration: `def fibonacci(n):`

Docstring:
Returns a list containing the Fibonacci sequence up to the nth term.

Parameters:
n (int): the number of terms in the Fibonacci sequence to generate

Returns:
list: a list containing the Fibonacci sequence up to the nth term
```

## 10. Leetcode_12451_I `max_diff_increasing_subsequence` split=grpo subset=Leetcode

- prompt_chars: 1211
- solution_chars: 449
- tests: public=2 hidden=8
- flags: ['keyword_complexity']

```text
Problem:
Given an integer array `nums`, return the maximum difference between any increasing subsequence of length 2. If no such subsequence exists, return `0`. For example, given `nums = [4, 5, 1, 3, 2, 10]`, the output should be `9` because the maximum difference is between the numbers `1` and `10`. If given `nums = [5, 4, 3, 2]`, the output should be `0` as there is no increasing subsequence of length 2. 

**Note:** An increasing subsequence of length 2 is a pair `(nums[i], nums[j])` where `i < j` and `nums[i] < nums[j]`.

Implement callable `max_diff_increasing_subsequence`.
Function declaration: `def max_diff_increasing_subsequence(nums):`

Docstring:
Returns the maximum difference between any increasing subsequence of length 2.
If no such subsequence exists, return 0.
```

## 11. Prefill_10344_I `factorial` split=grpo subset=Prefill

- prompt_chars: 689
- solution_chars: 240
- tests: public=2 hidden=2
- flags: ['few_hidden_tests']

```text
Problem:
Write a function to calculate the factorial of a given number. The function should be efficient and handle large numbers. Use Python's `math` library to achieve this.

Implement callable `factorial`.
Function declaration: `def factorial(n):`

Docstring:
Returns the factorial of the given number n using Python's math library.
```

## 12. Filter_16343_I `group_indices` split=sft_prompts subset=Filter

- prompt_chars: 1616
- solution_chars: 549
- tests: public=2 hidden=4
- flags: ['looks_easy']

```text
Problem:
I have a vector of integers and I wish to create a variable, let's call it "groups", which would contain a number of vectors, each of which contains the indices of the original vector which have a certain property. 

For example, given the vector [1, 2, 2, 4, 4, 4] of integers, I wish the variable "groups" to be [[0], [1, 2], [3, 4, 5]] if the property is that the integer values are the same. 

Here is my attempt so far:

```python
def group_indices(vector):
    seen = []
    groups = []
    for i, x in enumerate(vector):
        if x not in seen:
            groups.append([i])
            seen.append(x)
        else:
            for j, group in enumerate(groups):
                if x in [vector[k] for k in group]:
                    groups[j].append(i)
                    break
    return groups
```

Is this approach correct and time-efficient?

Implement callable `group_indices`.
Function declaration: `def group_indices(vector):`

Docstring:
Groups indices of the elements in the vector based on their value.

Parameters:
vector (list of int): List of integers.

Returns:
list of list of int: List where each sublist contains the indices of the elements with the same value.
```

## 13. Taco_97040_I `allowed_riders` split=sft_prompts subset=Taco

- prompt_chars: 1956
- solution_chars: 548
- tests: public=2 hidden=5
- flags: ['looks_easy']

```text
Problem:
# Roller Coaster Queue Management

A popular amusement park has implemented a new rule for managing the queue system for its top roller coaster ride. Each visitor's height (in cm) is recorded upon entry, and only those within a specified height range are allowed to board the ride.

Implement the function `allowed_riders`, which takes:
- An array of integers `heights` representing the heights of the visitors in the queue,
- Two integers `min_height` and `max_height` representing the inclusive height range.

The function should return a list of the visitors' heights who are allowed to board the ride, maintaining their original order.

## Example

```python
allowed_riders([160, 150, 170, 145, 180, 175], 150, 180)
```

Expected output:
```
[160, 150, 170, 180, 175]
```

## Notes:
1. The function should include both `min_height` and `max_height` in the allowed height range.
2. The order of heights in the input list should be preserved in the result.

---
*Good luck.*

Implement callable `allowed_riders`.
Function declaration: `def allowed_riders(heights, min_height, max_height):`

Docstring:
Returns the list of heights of visitors who are allowed to board the ride.

Parameters:
heights (list of int): A list of heights of visitors.
min_height (int): The minimum height allowed to board the ride.
max_height (int): The maximum height allowed to board the ride.

Returns:
list of int: A list of heights of visitors who are within the allowed height range.
```

## 14. Taco_90401_I `product_of_all_except_self` split=sft_prompts subset=Taco

- prompt_chars: 1109
- solution_chars: 698
- tests: public=2 hidden=7
- flags: ['looks_easy']

```text
Problem:
Write a function that takes a list of integers and returns a list of the same length where each element at index `i` is the product of all elements in the original list except the one at `i`.

For example:
```python
product_of_all_except_self([1, 2, 3, 4])    == [24, 12, 8, 6]
product_of_all_except_self([5, 3, 2, 6, 4]) == [144, 240, 360, 120, 180]
```

Implement callable `product_of_all_except_self`.
Function declaration: `def product_of_all_except_self(nums):`

Docstring:
Returns a list where each element at index i is the product of all elements
in the input list except the one at i.

:param nums: List of integers
:return: List of integers
```

## 15. Taco_19353_I `formatWithCommas` split=grpo subset=Taco

- prompt_chars: 1388
- solution_chars: 564
- tests: public=2 hidden=13
- flags: ['looks_easy']

```text
Problem:
Given a string representing a large integer, the task is to format it with commas to separate every three digits from the right.

Write a function `formatWithCommas(s: str) -> str` that takes a string `s` representing a non-negative integer and returns the formatted string with commas.

**Examples:**

- Input: `"123"`
  Output: `"123"`
  
- Input: `"1234"`
  Output: `"1,234"`
  
- Input: `"123456789"`
  Output: `"123,456,789"`
  
- Input: `"0"`
  Output: `"0"`

**Notes:**

1. The length of the input string `s` will be between 1 and 20.
2. The input string will not contain any leading zeros except when the input is `"0"`.
3. The function should handle large integers seamlessly by treating them as strings.

Implement callable `formatWithCommas`.
Function declaration: `def formatWithCommas(s):`

Docstring:
Formats a string representing a non-negative integer with commas.

Args:
s (str): The input string representing a non-negative integer.

Returns:
str: The formatted string with commas.
```

## 16. Taco_41359_I `reverse_words` split=grpo subset=Taco

- prompt_chars: 1518
- solution_chars: 405
- tests: public=2 hidden=5
- flags: ['looks_easy']

```text
Problem:
Write a function that takes an English sentence as input and returns the sentence with each word's letters reversed but with the words in their original order.

The input will consist of a single string containing alphabetic characters and spaces. The sentence will neither start nor end with a space, and there will be exactly one space between any two words. The sentences will have at most 100 characters.

SAMPLE INPUT:
Hello World
Programming is fun
Code every day

SAMPLE OUTPUT:
olleH dlroW
gnimmargorP si nuf
edoC yreve yad

Explanation

EXAMPLE 1: 
The word 'Hello' becomes 'olleH' and 'World' becomes 'dlroW'. The words remain in the same order.

EXAMPLE 2:
The word 'Programming' becomes 'gnimmargorP', 'is' becomes 'si', and 'fun' becomes 'nuf'. The words remain in the same order.

Implement callable `reverse_words`.
Function declaration: `def reverse_words(sentence):`

Docstring:
Reverses each word in the sentence but keeps the words in their original order.

Parameters:
sentence (str): The input English sentence to be processed.

Returns:
str: The sentence with each word's letters reversed.
```

## 17. Filter_49586_I `convert_temperature` split=sft_prompts subset=Filter

- prompt_chars: 1272
- solution_chars: 673
- tests: public=2 hidden=4
- flags: ['looks_easy']

```text
Problem:
I need to write a Python function that can convert a given temperature from Celsius to Fahrenheit and vice versa. The function should take two parameters: the temperature value and a string indicating the conversion type ("CtoF" for Celsius to Fahrenheit and "FtoC" for Fahrenheit to Celsius). The function should return the converted temperature value, rounded to two decimal places. How can I write this function?

Implement callable `convert_temperature`.
Function declaration: `def convert_temperature(value, conversion_type):`

Docstring:
Converts temperature from Celsius to Fahrenheit and vice versa.

Parameters:
value (float): The temperature value to be converted.
conversion_type (str): The conversion type ("CtoF" for Celsius to Fahrenheit or "FtoC" for Fahrenheit to Celsius).

Returns:
float: The converted temperature, rounded to two decimal places.
```

## 18. Algorithm_22453_I `longest_common_prefix` split=sft_prompts subset=Algorithm

- prompt_chars: 2704
- solution_chars: 801
- tests: public=2 hidden=9
- flags: ['long_prompt']

```text
Problem:
### Context
You are developing an algorithm for a recommendation system to find the most common prefixes shared among a list of strings, which will help in auto-completion features. The algorithm should find the longest common prefix (LCP) among a list of strings provided.

### Objective
Implement a function to find the longest common prefix string amongst a list of strings. If there is no common prefix, return an empty string.

### Function Signature
```python
def longest_common_prefix(strings: list[str]) -> str:
"""
Find the longest common prefix string amongst an array of strings

:param strings: List of strings to evaluate
:return: Longest common prefix string shared among all input strings, or empty string if none exists

Example:
>>> longest_common_prefix(["flower","flow","flight"])
"fl"

>>> longest_common_prefix(["dog","racecar","car"])
""
"""
```

### Constraints and Requirements
1. The input parameter `strings` should be a list of strings.
2. If the input list is empty, return an empty string.
3. The function should handle cases where there is no common prefix.
4. The function should consider the case sensitivity of the strings.

### Performance
1. The algorithm should be efficient, ideally handling lists of up to 1000 strings with string lengths up to 1000 characters.
2. Aim for a linear time complexity relative to the total number of characters across all strings.

### Examples
- Input: `["flower", "flow", "flight"]`  
  Output: `"fl"`
  
- Input: `["dog", "racecar", "car"]`  
  Output: `""`
  
- Input: `[]`  
  Output: `""`

- Input: `["interspecies", 
...(truncated 671 chars)
```

## 19. Filter_2892_I `find_min_length_word` split=sft_prompts subset=Filter

- prompt_chars: 2753
- solution_chars: 369
- tests: public=2 hidden=8
- flags: ['long_prompt']

```text
Problem:
You are given a string `s` and a list of strings `words`. Find the length of the shortest word that is not in the dictionary or is a substring of one of the words in the list.

Example 1:

 Input: `s = "barfoothefoobarman", words = ["foo","bar"]`
 Output: `0` (because "foo" and "bar" are substrings of `s`, and the shortest word in the list is "bar" with length 3)

Example 2:

 Input: `s = "barfoothefoobarman", words = ["foo","the","bar"]`
 Output: `0` (because "foo", "the", and "bar" are substrings of `s`, and the shortest word in the list is "the" with length 3)


However, in this problem, we will return the minimum length of the word that is not in the dictionary or is a substring of one of the words in the list.

Example 3:

 Input: `s = "barfoothefoobarman", words = ["barfoo","foo","thebar"]`
 Output: `3` (because the shortest word in the list that is a substring of `s` is "barfoo" with length 6 and "foo" with length 3, so we return 3)


Here is the code:
```python
def find_length(s, words):
    res = float('inf')
    for word in words:
        if word in s:
            res = min(res, len(word))
    return res if res != float('inf') else 0
```
However, I want to improve it. I want to make it more efficient. You can see that in the code, for every word in the words list, we are checking if it's a substring of `s`. This operation is very expensive because it takes O(nm) time complexity where n is the length of the string `s` and m is the length of the word. We can improve it by using the sliding window technique.

Here is the improved code:
```python
def find_len
...(truncated 700 chars)
```

## 20. Filter_84093_I `fibonacci_sequence` split=grpo subset=Filter

- prompt_chars: 1230
- solution_chars: 546
- tests: public=2 hidden=4
- flags: ['looks_easy']

```text
Problem:
The following is the definition of a **Fibonacci sequence**:

"A sequence of numbers where each subsequent number is the sum of the two preceding ones."

**Examples:**
* 1, 1, 2, 3, 5, 8, 13, 21, 34...

Write a program in Python to generate the Fibonacci sequence up to a given number of terms.


```python
def fibonacci_sequence(n):
  """
  This function generates the Fibonacci sequence up to a given number of terms.

  Args:
    n: The number of terms to generate.

  Returns:
    A list containing the Fibonacci sequence up to n terms.
  """

Implement callable `fibonacci_sequence`.
Function declaration: `def fibonacci_sequence(n):`

Docstring:
This function generates the Fibonacci sequence up to a given number of terms.

Args:
    n: The number of terms to generate.

Returns:
    A list containing the Fibonacci sequence up to n terms.
```

## 21. Filter_24967_I `get_index` split=sft_prompts subset=Filter

- prompt_chars: 831
- solution_chars: 268
- tests: public=2 hidden=5
- flags: ['looks_easy']

```text
Problem:
You've been tasked with writing a function `get_index` that takes two parameters: `my_list` and `my_element`. Your function should return the index of the first occurrence of `my_element` in the list `my_list`.

Implement callable `get_index`.
Function declaration: `def get_index(my_list, my_element):`

Docstring:
Returns the index of the first occurrence of my_element in the list my_list.
If the element is not found, returns -1.
```

## 22. Apps_18029_I `merge_intervals` split=grpo subset=Apps

- prompt_chars: 2082
- solution_chars: 712
- tests: public=2 hidden=7
- flags: ['looks_easy']

```text
Problem:
**[Problem Statement]**

# Merge Intervals

## Task
Given a collection of intervals, merge all overlapping intervals.

## Description
You are given an array of intervals, where each interval is represented as a list with its start and end times `[start, end]`. Your task is to write a function that merges all overlapping intervals and returns an array of the merged intervals.

## Input/Output
* **Input:** A list of intervals where each interval is represented as a list `[start, end]`. Both `start` and `end` are integers such that `start ≤ end`.

* **Output:** A list of intervals merged such that no two intervals overlap and all intervals are returned in ascending order based on their start time.

### Example
```python
# Example 1
input_intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]
output_intervals = [[1, 6], [8, 10], [15, 18]]
# Explanation: Since intervals [1, 3] and [2, 6] overlap, we merge them to get [1, 6].

# Example 2
input_intervals = [[1, 4], [4, 5]]
output_intervals = [[1, 5]]
# Explanation: Intervals [1, 4] and [4, 5] are considered overlapping due to the end of one touching the start of the other, so we merge them into [1, 5].
```

## Function Signature
```python
def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
```

## Constraints
- The list of intervals could be empty, return an empty list in such case.
- All integers in the intervals are non-negative.
- Intervals are not necessarily sorted.
- The intervals in the returned list should be sorted by their start time.

Implement callable `merge_intervals`.
Function declaration: `def me
...(truncated 26 chars)
```

## 23. Leetcode_17814_I `length_of_longest_substring` split=sft_prompts subset=Leetcode

- prompt_chars: 1110
- solution_chars: 451
- tests: public=2 hidden=6
- flags: ['keyword_complexity']

```text
Problem:
Given a string `s`, return _the length of the longest substring without repeating characters_. 

For example:
```python
# Example 1
s = "abcabcbb"
Output: 3
Explanation: The answer is "abc", with the length of 3.

# Example 2
s = "bbbbb"
Output: 1
Explanation: The answer is "b", with the length of 1.

# Example 3
s = "pwwkew"
Output: 3
Explanation: The answer is "wke", with the length of 3. Notice that the answer must be a substring, "pwke" is a subsequence and not a substring.

Implement callable `length_of_longest_substring`.
Function declaration: `def length_of_longest_substring(s):`

Docstring:
Given a string s, return the length of the longest substring without repeating characters.
```

## 24. Taco_22218_I `sum_of_squares` split=sft_prompts subset=Taco

- prompt_chars: 1111
- solution_chars: 235
- tests: public=2 hidden=5
- flags: ['looks_easy']

```text
Problem:
Write a function `sum_of_squares(n)` that takes an integer `n` as input and returns the sum of the squares of all integers from 1 to `n`. For example, if `n = 3`, the function should return `1^2 + 2^2 + 3^2 = 14`. If `n = 0` or `n` is negative, the function should return 0.

### Example:
```python
sum_of_squares(3) => 14
sum_of_squares(5) => 55
sum_of_squares(0) => 0
sum_of_squares(-4) => 0
```

**Constraints**:
- The input `n` will be an integer.
- The function should handle edge cases where `n` is 0 or negative gracefully.

Implement callable `sum_of_squares`.
Function declaration: `def sum_of_squares(n):`

Docstring:
Returns the sum of the squares of all integers from 1 to `n`.
If n is 0 or negative, the function returns 0.
```

## 25. Taco_59985_I `canFormPalindrome` split=sft_prompts subset=Taco

- prompt_chars: 1089
- solution_chars: 317
- tests: public=2 hidden=5
- flags: ['keyword_complexity']

```text
Problem:
Write a function `canFormPalindrome(s)` that takes a string `s` as input and returns `true` if any permutation of `s` could form a palindrome, otherwise returns `false`. A string can form a palindrome if at most one character appears an odd number of times. For example, the string "racecar" can form the palindrome "racecar", so `canFormPalindrome("racecar")` should return `true`, whereas the string "hello" cannot form any palindrome, so `canFormPalindrome("hello")` should return `false`.

Implement callable `canFormPalindrome`.
Function declaration: `def canFormPalindrome(s):`

Docstring:
Returns True if any permutation of the string s can form a palindrome, otherwise returns False.
```

## 26. Leetcode_19765_I `min_distance` split=grpo subset=Leetcode

- prompt_chars: 1258
- solution_chars: 1473
- tests: public=2 hidden=8
- flags: ['looks_easy']

```text
Problem:
You are given two strings, `string1` and `string2`, which consist of lowercase letters. You need to transform `string1` into `string2` by performing a sequence of allowed operations. In each operation, you can do one of the following:
- Insert a new character into `string1`.
- Delete an existing character from `string1`.
- Replace an existing character in `string1` with any other character.

You are required to return the minimum number of operations needed to transform `string1` into `string2`.

Implement callable `min_distance`.
Function declaration: `def min_distance(string1, string2):`

Docstring:
Returns the minimum number of operations needed to transform string1 into string2.
Transformation operations include insertions, deletions, and substitutions.

:param string1: Source string
:param string2: Target string
:return: Minimum number of operations
```

## 27. Algorithm_41389_I `merge_and_sort_lists` split=sft_prompts subset=Algorithm

- prompt_chars: 2045
- solution_chars: 464
- tests: public=2 hidden=4
- flags: ['looks_easy']

```text
Problem:
### List Merging and Sorting Function

Write a function in Python called `merge_and_sort_lists` that accepts two parameters:
1. `list1` (List[int]): A list of integers.
2. `list2` (List[int]): Another list of integers.

The function should merge the two lists, sort the resulting list in ascending order, and remove any duplicate values. Finally, it should return the sorted list of unique values.

### Constraints:
* The input lists, `list1` and `list2`, can have lengths in the range of 0 to 10<sup>5</sup>.
* Each list can contain integers from -10<sup>9</sup> to 10<sup>9</sup>.
* Your function should be optimized to handle large inputs efficiently.

### Inputs:
* `list1`: a list containing 0 to 100,000 integers.
* `list2`: a list containing 0 to 100,000 integers.

### Outputs:
* A sorted list of unique integers.

### Example:

```python
print(merge_and_sort_lists([5, 3, 1], [6, 2, 3, 1]))
```

Should return:

```python
[1, 2, 3, 5, 6]
```

### Hints:
* Consider using Python's set data structure to remove duplicates efficiently.
* Utilize the `sorted()` function to sort the list.

### Additional Example:

```python
print(merge_and_sort_lists([], [4, 2, 2, 3, 9]))
```

Should return:

```python
[2, 3, 4, 9]
```

Implement callable `merge_and_sort_lists`.
Function declaration: `def merge_and_sort_lists(list1, list2):`

Docstring:
Merges two lists, sorts the resulting list in ascending order,
and removes duplicates.

Parameters:
    list1 (list of int): The first list of integers.
    list2 (list of int): The second list of integers.
    
Returns:
    list of int: A sort
...(truncated 27 chars)
```

## 28. Data_Structure_15101_I `bit_manipulation` split=sft_prompts subset=Data_Structure

- prompt_chars: 3131
- solution_chars: 995
- tests: public=2 hidden=6
- flags: ['long_prompt']

```text
Problem:
#### Context
You are working on a low-level embedded system project. The project involves manipulating specific bits within integers to set flags or achieve efficient state management. To perform these operations effectively, you need to write functions that handle bit manipulation reliably and efficiently.

#### Task
Write a function `bit_manipulation(num: int, i: int, action: str, bit: int = None) -> int` that performs one of four different bit manipulation operations on a given integer `num`. The function should accept the following parameters:

* `num`: The integer on which the bit operation will be performed.
* `i`: The index of the bit to be manipulated.
* `action`: The type of bit manipulation to be performed. This can be 'get', 'set', 'clear', or 'update'.
* `bit`: The value to set the ith bit to, applicable only for the 'update' action.

#### Specifications
* For the 'get' action, return 1 if the ith bit is 1, and 0 if the ith bit is 0.
* For the 'set' action, set the ith bit to 1.
* For the 'clear' action, set the ith bit to 0.
* For the 'update' action, update the ith bit to the given `bit` value (0 or 1).

#### Input
* `num`: An integer within the standard 32-bit signed integer range.
* `i`: A non-negative integer indicating the bit index.
* `action`: A string, one of 'get', 'set', 'clear', or 'update'.
* `bit`: An integer, either 0 or 1, only when `action` is 'update'.

#### Output
* Return an integer result of the bitwise operation or the bit value in case of 'get' action.

#### Constraints
* `0 <= num < 2**31`
* `0 <= i < 31`
* `bit` is applicable on
...(truncated 1143 chars)
```

## 29. Prefill_21304_I `longest_string` split=sft_prompts subset=Prefill

- prompt_chars: 909
- solution_chars: 425
- tests: public=2 hidden=5
- flags: ['looks_easy']

```text
Problem:
Create a function that takes a variable number of string arguments and returns the longest string among them.

Implement callable `longest_string`.
Function declaration: `def longest_string(*args):`

Docstring:
Returns the longest string from the given arguments.

Parameters:
    *args (str): Variable number of string arguments.
    
Returns:
    str: The longest string among the input strings. If there are multiple strings with the same maximum length,
    returns the first one encountered.
```

## 30. Filter_79383_I `find_first_index` split=sft_prompts subset=Filter

- prompt_chars: 886
- solution_chars: 467
- tests: public=2 hidden=8
- flags: ['looks_easy']

```text
Problem:
How can I find the first index of any of the characters in a string using Python?

Implement callable `find_first_index`.
Function declaration: `def find_first_index(s, chars):`

Docstring:
Returns the first index of any character from chars in the string s.
If no character from chars is found in s, returns -1.

:param s: str, the string to search through.
:param chars: str, the characters to search for in the string s.
:return: int, the first index of any character from chars in s.
```

## 31. Algorithm_45413_I `rotate_list` split=sft_prompts subset=Algorithm

- prompt_chars: 2038
- solution_chars: 481
- tests: public=2 hidden=7
- flags: ['looks_easy']

```text
Problem:
### Question
**Problem Statement**:

You are given a list of integers and an integer `k`. Your task is to rotate the list to the right by `k` steps.

#### Function Signature:
```python
def rotate_list(nums: list[int], k: int) -> list[int]:
    pass
```

#### Input:
- `nums`: A list of integers. `List[int]`.
- `k`: An integer representing the number of steps to rotate the list. `int`.

#### Output:
- Return the modified list after rotating it to the right by `k` steps.

#### Constraints:
- The length of the list does not exceed \(10^5\).
- Rotations beyond the length of the list should wrap around. For example, rotating a list of length 5 by 6 steps is equivalent to rotating it by 1 step.

#### Examples:
- `rotate_list([1, 2, 3, 4, 5], 2)` should return `[4, 5, 1, 2, 3]`.
- `rotate_list([1, 2, 3, 4, 5], 5)` should return `[1, 2, 3, 4, 5]`.
- `rotate_list([1, 2, 3, 4, 5], 7)` should return `[4, 5, 1, 2, 3]`.
- `rotate_list([], 3)` should return `[]`.
- `rotate_list([1], 0)` should return `[1]`.

#### Notes:
- Consider edge cases such as when the list is empty or when `k` is larger than the length of the list.
- Aim for an efficient solution that operates within O(n) time complexity.

**Hint**:
- Use list slicing to achieve the rotation efficiently.

Good luck!

Implement callable `rotate_list`.
Function declaration: `def rotate_list(nums, k):`

Docstring:
Rotates the list to the right by k steps.

Args:
nums (List[int]): the list of integers to be rotated.
k (int): the number of steps to rotate the list.

Returns:
List[int]: the modified list after rotating it to the
...(truncated 18 chars)
```

## 32. Prefill_580_I `add_strings` split=sft_prompts subset=Prefill

- prompt_chars: 815
- solution_chars: 308
- tests: public=2 hidden=5
- flags: ['looks_easy']

```text
Problem:
Write a function to add two numbers in Python, but the numbers are stored as strings. The function should return the result as a string.

Implement callable `add_strings`.
Function declaration: `def add_strings(num1, num2):`

Docstring:
Adds two numbers that are represented as strings.

Parameters:
num1 (str): The first number as string
num2 (str): The second number as string

Returns:
str: The result of the addition as string
```

## 33. Data_Structure_1710_I `pigeonhole_sort` split=sft_prompts subset=Data_Structure

- prompt_chars: 1885
- solution_chars: 649
- tests: public=2 hidden=4
- flags: ['looks_easy']

```text
Problem:
### Pigeonhole Sort Implementation

You have been hired by a software development company that specializes in processing large volumes of integer data. One of the tasks at hand requires sorting lists of integers efficiently. However, the lists they deal with often have a relatively small range of key values compared to the number of elements.

Your task is to implement the Pigeonhole Sort algorithm, which is suitable for this type of problem. Write a function `pigeonhole_sort` in Python that takes a list of integers and returns a sorted list.

#### Function Signature
```python
def pigeonhole_sort(arr: List[int]) -> List[int]:
```

#### Input
* `arr` (List[int]): A list of integers that need to be sorted.
  
#### Output
* Returns a sorted list of integers.

#### Constraints
* Each integer in the list can be in the range from -1000 to 1000.
* The length of the list `n` is such that `1 <= n <= 10^5`.

#### Example
```python
assert pigeonhole_sort([8, 3, 2, 3, 8, 7, 1]) == [1, 2, 3, 3, 7, 8, 8]
assert pigeonhole_sort([-5, 0, -2, 3, 2, -8]) == [-8, -5, -2, 0, 2, 3]
```

#### Requirements
- The function should handle edge cases gracefully, such as an empty list or a list with a single element.
- Ensure that the solution is efficient in terms of both time and space complexity, taking into account the constraints provided.
- Add appropriate error handling and optimization where necessary.

Good luck!

Implement callable `pigeonhole_sort`.
Function declaration: `def pigeonhole_sort(arr):`
```

## 34. Filter_66470_I `count_words` split=grpo subset=Filter

- prompt_chars: 685
- solution_chars: 192
- tests: public=2 hidden=4
- flags: ['looks_easy']

```text
Problem:
Can you generate a Python code to count the number of words in a given string using Python?

Implement callable `count_words`.
Function declaration: `def count_words(s):`

Docstring:
Returns the number of words in a given string. A word is considered to be any 
sequence of characters separated by spaces.
```

## 35. Filter_39043_I `reverse_string` split=grpo subset=Filter

- prompt_chars: 914
- solution_chars: 516
- tests: public=2 hidden=3
- flags: ['looks_easy']

```text
Problem:
Given a string, reverse the order of its characters without using any built-in string manipulation functions or additional data structures. The solution should have a time complexity of O(n), where n is the length of the string. Additionally, you are not allowed to create any new variables or arrays.

Implement callable `reverse_string`.
Function declaration: `def reverse_string(s):`

Docstring:
Reverses the input string s in place.

Args:
- s (str): The string to be reversed.

Returns:
- str: The reversed string.
```

## 36. Prefill_132_I `reverse_string` split=sft_prompts subset=Prefill

- prompt_chars: 684
- solution_chars: 113
- tests: public=2 hidden=3
- flags: ['looks_easy']

```text
Problem:
Write a function to reverse a string in Python. The function should take a string `s` as input and return the reversed string.

Implement callable `reverse_string`.
Function declaration: `def reverse_string(s):`

Docstring:
Returns the reversed version of the input string s.
```

## 37. Prefill_25483_I `sum_of_odd_integers` split=grpo subset=Prefill

- prompt_chars: 728
- solution_chars: 175
- tests: public=2 hidden=5
- flags: ['looks_easy']

```text
Problem:
Create a function that takes in a list of integers and returns the sum of the list. However, skip over any integers that are even.

Implement callable `sum_of_odd_integers`.
Function declaration: `def sum_of_odd_integers(int_list):`

Docstring:
Returns the sum of the list, skipping over any integers that are even.
```

## 38. Prefill_1215_I `find_largest_number` split=sft_prompts subset=Prefill

- prompt_chars: 824
- solution_chars: 394
- tests: public=2 hidden=2
- flags: ['few_hidden_tests']

```text
Problem:
Write a function to find the largest number in an array of integers. The function should be able to handle arrays with both positive and negative numbers.

Implement callable `find_largest_number`.
Function declaration: `def find_largest_number(arr):`

Docstring:
Returns the largest number in an array of integers.

Parameters:
arr (list): A list of integers.

Returns:
int: The largest number in the list.
```

## 39. Filter_51617_I `factorial` split=sft_prompts subset=Filter

- prompt_chars: 693
- solution_chars: 247
- tests: public=2 hidden=3
- flags: ['keyword_complexity']

```text
Problem:
Write a short paragraph explaining the concept of recursion in programming, and provide a simple example in Python.

Implement callable `factorial`.
Function declaration: `def factorial(n):`

Docstring:
Returns the factorial of a non-negative integer n.
For example, factorial(5) returns 120, because 5! = 5 * 4 * 3 * 2 * 1 = 120.
```

## 40. Data_Structure_5404_I `binary_search_name` split=grpo subset=Data_Structure

- prompt_chars: 2515
- solution_chars: 613
- tests: public=2 hidden=7
- flags: ['keyword_complexity', 'long_prompt']

```text
Problem:
Binary Search

#### Scenario
Suppose you are developing a search utility for a contacts application where users have a list of contacts sorted alphabetically by their names. You need to implement a search function that efficiently locates a contact by their name.

#### Task
Write a function `binary_search_name` that searches for a target name in a sorted list of contact names using the binary search technique. If the target name exists in the list, the function should return its index. If the target name does not exist, the function should return -1.

#### Function Signature
```python
def binary_search_name(names: List[str], target: str) -> int:
    pass
```

#### Input
- `names` (List[str]): A list of strings representing contact names sorted in ascending order. The list contains no duplicate names.
- `target` (str): A string representing the name to be searched.

#### Output
- `int`: Index of the target name if found, otherwise -1.

#### Constraints
- The length of the list `names` is between 0 and 10^6.
- The length of each contact name is between 1 and 100 characters.

#### Example
```python
assert binary_search_name(["Alice", "Bob", "Charlie", "David"], "Charlie") == 2
assert binary_search_name(["Alice", "Bob", "Charlie", "David"], "Eve") == -1
assert binary_search_name([], "Alice") == -1
```

#### Performance Requirements
Your implementation should have a time complexity of O(log n) and space complexity of O(1).

#### Hints
- Consider edge cases like an empty list or the target name being the first/last element in the list.
- Ensure you're not causing integer
...(truncated 453 chars)
```

## 41. Docs: Python310_34710_I `prime_factors` split=eval subset=Docs

- prompt_chars: 2230
- solution_chars: 524
- tests: public=2 hidden=16
- flags: ['looks_easy']

```text
Problem:
#### Problem Statement

Write a Python function `prime_factors(n: int) -> list` that takes an integer `n` and returns a list of all prime factors of `n`, sorted in ascending order.

A prime factor is a factor of a number that is a prime number. Your function should:
- Use basic arithmetic operations (+, -, *, /, //, etc.).
- Utilize lists to store and manipulate intermediate results.
- Demonstrate understanding of loops and conditionals to implement the prime factorization algorithm.

#### Input
- `n` (1 <= n <= 10^4): An integer for which you need to find the prime factors.

#### Output
- Return a list of integers representing the prime factors of `n`, sorted in ascending order.

#### Example
```python
>>> prime_factors(28)
[2, 2, 7]

>>> prime_factors(100)
[2, 2, 5, 5]

>>> prime_factors(37)
[37]

>>> prime_factors(1)
[]
```

#### Constraints
- The input `n` will be a positive integer up to 10,000.
- The output list should sort the prime factors in ascending order.
- You should handle edge cases such as `n` being a prime number itself or `n` being the minimum value 1.

#### Notes
- The function must not use any external libraries for finding prime numbers.
- Carefully handle edge cases such as when `n` is 1.

#### Solution Template

```python
def prime_factors(n: int) -> list:
    # Your code here
    pass
```

#### Evaluation Criteria
- Correctness: The function should correctly determine the prime factors for various test cases.
- Efficiency: The function should run efficiently within the given constraints.
- Code Quality: The code should be well-structured and
...(truncated 246 chars)
```

## 42. Filter_30321_I `transpose_matrix` split=grpo subset=Filter

- prompt_chars: 830
- solution_chars: 420
- tests: public=2 hidden=4
- flags: ['keyword_complexity']

```text
Problem:
Write a function that takes a matrix (a list of lists) and returns the transposed matrix.

Implement callable `transpose_matrix`.
Function declaration: `def transpose_matrix(matrix):`

Docstring:
Returns the transpose of the given matrix.

Parameters:
matrix (List[List[int]]): A 2D list representing the matrix to be transposed.

Returns:
List[List[int]]: The transposed matrix.
```

## 43. Filter_47599_I `convert_and_square_list` split=sft_prompts subset=Filter

- prompt_chars: 987
- solution_chars: 398
- tests: public=2 hidden=3
- flags: ['looks_easy']

```text
Problem:
How can I create a Python function that converts a list of integers into a comma-separated string, with each integer squared? For example, if I provide the list `[1, 2, 3]`, the function should return `"1,4,9"`. How can I achieve this?

Implement callable `convert_and_square_list`.
Function declaration: `def convert_and_square_list(int_list):`

Docstring:
Converts a list of integers into a comma-separated string with each integer squared.

Args:
int_list (list of int): The list of integers to be squared and converted.

Returns:
str: A comma-separated string with each integer squared.
```

## 44. Filter_65137_I `find_min_max` split=eval subset=Filter

- prompt_chars: 900
- solution_chars: 329
- tests: public=2 hidden=4
- flags: ['looks_easy']

```text
Problem:
Write a Python function `find_min_max` that takes a list of integers and returns a tuple containing the minimum and maximum values from the list. If the list is empty, the function should return `(None, None)`.

Implement callable `find_min_max`.
Function declaration: `def find_min_max(numbers):`

Docstring:
Returns a tuple containing the minimum and maximum values from the list of integers.
If the list is empty, returns (None, None).
```

## 45. Filter_61901_I `linear_search` split=sft_prompts subset=Filter

- prompt_chars: 1006
- solution_chars: 461
- tests: public=2 hidden=6
- flags: ['looks_easy']

```text
Problem:
Create a Python function that simulates a linear search algorithm to find a target element in a list of integers. The function should return the index of the target element if it is found, or -1 if it is not in the list.

Implement callable `linear_search`.
Function declaration: `def linear_search(arr, target):`

Docstring:
Simulates a linear search algorithm to find a target element in a list of integers.

Parameters:
arr (list of int): The list of integers to search through.
target (int): The target element to find.

Returns:
int: The index of the target element if found, or -1 if not found.
```

## 46. Prefill_13136_I `max_subarray_sum` split=sft_prompts subset=Prefill

- prompt_chars: 859
- solution_chars: 469
- tests: public=2 hidden=5
- flags: ['looks_easy']

```text
Problem:
Write a function to find the maximum sum of a subarray within a given array of integers. Implement your function using Kadane's Algorithm, which is efficient with a time complexity of O(n).

Implement callable `max_subarray_sum`.
Function declaration: `def max_subarray_sum(arr):`

Docstring:
Finds the maximum sum of a subarray within a given array of integers.

:param arr: List[int] - List of integers
:return: int - Maximum sum of the subarray
```

## 47. Filter_80780_I `remove_duplicates` split=grpo subset=Filter

- prompt_chars: 1002
- solution_chars: 418
- tests: public=2 hidden=5
- flags: ['looks_easy']

```text
Problem:
Write a Python function that takes a list of integers and returns a new list with all duplicates removed. The order of the elements in the returned list should be the same as the order in which they first appeared in the original list. Use the `Set` ADT to implement this function efficiently.

Implement callable `remove_duplicates`.
Function declaration: `def remove_duplicates(lst):`

Docstring:
Removes duplicates from a list while preserving the original order of elements.

Args:
lst (list of int): A list of integers

Returns:
list of int: A new list with all duplicates removed
```

## 48. Algorithm_36396_I `generate_screen_sequence` split=eval subset=Algorithm

- prompt_chars: 2570
- solution_chars: 609
- tests: public=2 hidden=2
- flags: ['long_prompt', 'few_hidden_tests']

```text
Problem:
### Coding Assessment Question

#### Context
In a series of computer screens connected together, each screen displays a sequence of alphabets where each screen's sequence must be incrementally longer than the previous one. This problem involves arranging the alphabets in such a way that the sequences satisfy the required conditions.

#### Problem Statement
Given a single integer `n` representing the number of connected computer screens, you need to generate the sequences of alphabets for each screen such that:
- The sequence for the `i-th` screen (where `i` starts from 1) is exactly `i` characters long.
- Each character in any sequence can only be a lowercase English alphabet (`'a'` to `'z'`).
- All characters in the sequences must be sorted in lexicographical order.

Create a function `generate_screen_sequence(n: int) -> List[str]` that generates these sequences for `n` screens and returns them as a list of strings.

##### Input:
- An integer `n` representing the number of screens (1 ≤ n ≤ 26).

##### Output:
- Return a list of `n` strings, where the `i-th` string has exactly `i` characters, sorted in lexicographical order.

##### Example:
```python
generate_screen_sequence(3)
# Expected output: ["a", "ab", "abc"]
```

##### Constraints:
- Ensure that your solution correctly generates the sequences within the given constraints.
- Utilize appropriate programming constructs to achieve the desired output.

#### Notes:
- The function should handle and return the results in an efficient manner for the given constraints.
- Consider edge cases where `n` can be the smalle
...(truncated 572 chars)
```

## 49. Filter_62922_I `sum_of_elements` split=grpo subset=Filter

- prompt_chars: 793
- solution_chars: 219
- tests: public=2 hidden=3
- flags: ['looks_easy']

```text
Problem:
Write a Python function that takes a list of integers as input and returns the sum of all the elements in the list. The function should be designed to handle large lists efficiently.

Implement callable `sum_of_elements`.
Function declaration: `def sum_of_elements(lst):`

Docstring:
Returns the sum of all elements in the list.

Args:
lst (list): List of integers.

Returns:
int: Sum of all integers in the list.
```

## 50. Filter_68860_I `reverse_string` split=eval subset=Filter

- prompt_chars: 681
- solution_chars: 252
- tests: public=2 hidden=3
- flags: ['looks_easy']

```text
Problem:
Can you explain how to implement a function `reverse_string` in Python using a recursive approach?

Implement callable `reverse_string`.
Function declaration: `def reverse_string(s):`

Docstring:
Recursively reverses a given string s.

:param s: The string to be reversed.
:return: The reversed string.
```

