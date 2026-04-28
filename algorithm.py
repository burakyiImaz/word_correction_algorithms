def wagner_fischer_distance(s1: str, s2: str) -> int:
    len1 , len2 = len(s1), len(s2)

    matrix = [[0]*(len2+1) for _ in range(len1 +1)]

    for i in range(len1 +1):
        matrix[i][0] =i 

    for j in range(len2 +1):
        matrix[0][j] =j

    for i in range(len1 +1):
        for j in range(len2 +1):
            cost= 0 if s1[i-1]==s2[j-1] else 1
            matrix[i][j]= min(
                matrix[i-1][j] + 1,
                matrix[i][j-1]+1,
                matrix[i-1][j-1] +cost
            )
    return matrix[len1][len2]