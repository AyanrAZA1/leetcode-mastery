class Solution {
    public String mergeAlternately(String word1, String word2) {
        char[] arr1 = word1.toCharArray();
        char[] arr2 = word2.toCharArray();
        char[] newArr = new char[arr1.length + arr2.length];

        int i = 0, j = 0, k = 0;

        while (i < arr1.length && j < arr2.length) {
            newArr[k++] = arr1[i++];
            newArr[k++] = arr2[j++];
        }

        while (i < arr1.length) {
            newArr[k++] = arr1[i++];
        }

        
        while (j < arr2.length) {
            newArr[k++] = arr2[j++];
        }

        return new String(newArr);
    }
}
