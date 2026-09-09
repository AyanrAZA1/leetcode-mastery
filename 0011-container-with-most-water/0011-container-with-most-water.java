class Solution {
    public int maxArea(int[] height) {
        int maxwater = 0;
        int i = 0;
        int j = height.length-1;
        while(i<j){
            int width = j-i;
            int ht = Math.min(height[i] , height[j]);
            int currentwater = width * ht;
            maxwater = Math.max(maxwater,currentwater);
            if(height[i] < height[j]){
                i++;
            }else{
                j--;
            }
            }
            return maxwater;
        }
    }
