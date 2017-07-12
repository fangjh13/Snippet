import string


def convert_lower(s):
	s = s.lower()
	ans = ''
	for i in s:
		if i in string.ascii_lowercase:
			ans = ans + i
	return ans


def isPalindrome(s):
	if len(s) <= 1:
		return True
	else:
		return s[0] == s[-1] and isPalindrome(s[1:-1])


print(isPalindrome(convert_lower('abcba 8 abcbA')))
