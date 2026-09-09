class Solution {
    public int[] shuffle(int[] nums, int n) {
        int[] arrX = new int[nums.length / 2];

for(int i = 0; i < nums.length / 2; i++) {
    arrX[i] = nums[i];
}

int[] arrY = new int[nums.length / 2];

for(int i = 0; i < nums.length / 2; i++) {
    arrY[i] = nums[i + n];
}

int[] ans = new int[2 * n];

for(int i = 0; i < n; i++) {
    ans[2 * i] = arrX[i];
    ans[2 * i + 1] = arrY[i];
}

return ans;
    }
}