class Solution(object):
    def twoSum(self, nums, target):
      numMap = {}
      for i, num in enumerate(nums):
          complement = target - num
          if complement in numMap:
            return [numMap[complement], i]
          numMap[num] = i
      return []

print(Solution().twoSum([3, 2, 4], 6))
#print(Solution().countHillValley([2,4,1,1,6,5]))