class Solution {
    public int percentageLetter(String s, char letter) {
        int length = s.length();
        int cnt = 0;
        for(int i=0;i<length;i++){
            if(s.charAt(i) == letter){
                cnt++;

            }

        } 
          int percent = (int)(((double) cnt / length) * 100);

        return percent;
    }
}