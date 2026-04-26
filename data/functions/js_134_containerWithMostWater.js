export default function containerWithMostWater(height) {
  let left = 0, right = height.length - 1;
  let maxWater = 0;
  while (left < right) {
    const water = Math.min(height[left], height[right]) * (right - left);
    maxWater = Math.max(maxWater, water);
    if (height[left] <= height[right]) {
      left++;
    } else {
      right--;
    }
  }
  return maxWater;
}
