# Two Sum: return the indices of two distinct values in nums that add to target.
    # Your implementation goes here.
def two_sum(nums: list[int], target: int) -> list[int]:
     for i in range(len(nums)):
         for j in range(i + 1, len(nums)):
             if nums[i] + nums[j] == target:
                 return [i, j]
    