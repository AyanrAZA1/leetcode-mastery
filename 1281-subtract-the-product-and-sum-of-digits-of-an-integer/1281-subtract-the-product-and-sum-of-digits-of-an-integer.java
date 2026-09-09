class Solution {
    public int subtractProductAndSum(int n) {
        int product = 1;
        int sum = 0;
        
        String s = String.valueOf(n);
        int[] arr = new int[s.length()];
        for (int i = 0; i < s.length(); i++) {
        arr[i] = s.charAt(i) - '0';
}       
        for(int i=0;i<s.length();i++){ 
        product = arr[i] * product;
        }
        for(int j=0;j<s.length();j++){
            sum = arr[j] + sum;
        }
        int result = product - sum;
        
    return result;
    }
}