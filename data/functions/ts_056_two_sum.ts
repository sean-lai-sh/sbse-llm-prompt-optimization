/**
 * Given an array of integers and a target, return the indices of the two
 * numbers that add up to the target.  Assumes exactly one solution exists.
 */
export function twoSum(nums: number[], target: number): [number, number] {
  const seen = new Map<number, number>(); // value -> index

  for (let i = 0; i < nums.length; i++) {
    const complement = target - nums[i];

    if (seen.has(complement)) {
      const j = seen.get(complement) as number;
      return [j, i];
    }

    seen.set(nums[i], i);
  }

  throw new Error("No solution found");
}
