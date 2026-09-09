class Solution {
    public double findMedianSortedArrays(int[] nums1, int[] nums2) {

        // Binary search हमेशा छोटे array पर
        if (nums1.length > nums2.length) {
            return findMedianSortedArrays(nums2, nums1);
        }

        int m = nums1.length;
        int n = nums2.length;

        int low = 0;
        int high = m;

        while (low <= high) {

            // nums1 में कितने elements left side में होंगे
            int partition1 = (low + high) / 2;

            // nums2 में बाकी elements left side में
            int partition2 = (m + n + 1) / 2 - partition1;

            // Boundary values
            int left1 = (partition1 == 0)
                    ? Integer.MIN_VALUE
                    : nums1[partition1 - 1];

            int right1 = (partition1 == m)
                    ? Integer.MAX_VALUE
                    : nums1[partition1];

            int left2 = (partition2 == 0)
                    ? Integer.MIN_VALUE
                    : nums2[partition2 - 1];

            int right2 = (partition2 == n)
                    ? Integer.MAX_VALUE
                    : nums2[partition2];

            // Correct partition
            if (left1 <= right2 && left2 <= right1) {

                // Total length even
                if ((m + n) % 2 == 0) {

                    return (Math.max(left1, left2)
                            + Math.min(right1, right2)) / 2.0;

                }

                // Total length odd
                else {
                    return Math.max(left1, left2);
                }
            }

            // nums1 का partition बहुत right चला गया
            else if (left1 > right2) {
                high = partition1 - 1;
            }

            // nums1 का partition बहुत left है
            else {
                low = partition1 + 1;
            }
        }

        return 0.0;
    }
}