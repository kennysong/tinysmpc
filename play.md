REGEX for "ab"

|             | **INPUT 'a'** | **INPUT 'b'** |
| ----------- | ------------- | ------------- |
| **STATE 0** | STATE 2       | STATE 3       |
| **STATE 1** | STATE 3       | STATE 3       |
| **STATE 2** | STATE 3       | STATE 1       |
| **STATE 3** | STATE 3       | STATE 3       |

starting state = 0
accepting state = 1

using DPF we essentially select a column from the table above. e.g. when the client inputs an 'a' we select the column with the input 'a' and the row with the current state.

|             | **INPUT 'a'** |
| ----------- | ------------- |
| **STATE 0** | STATE 2       |
| **STATE 1** | STATE 3       |
| **STATE 2** | STATE 3       |
| **STATE 3** | STATE 3       |

rewriting the list as a bunch of points we can use bilinear interpolation to construct this table.

in this example let $a = 0$ and $b = 1$

```python
# (STATE, INPUT, NEXT STATE)
(0, 0, 2)
(1, 0, 3)
(2, 0, 3)
(3, 0, 3)
(0, 1, 3)
(1, 1, 3)
(2, 1, 1)
(3, 1, 3)
```

```python
PRIME = 65521
GF = galois.GF(PRIME)
```

trust me this is the bilinear interpolation formula when $p = 65521$

$$f(x, y) = 2 + 1y + 10922x + 54602xy + 65520x^2 + 65518x^2y + 54601x^3 + 10921x^3y$$

<!-- starting state = 0
accepting state = 1

using DPF we essentially select a column from the table above. e.g. when the client inputs an 'a' we select the column with the input 'a' and the row with the current state.

|             | **INPUT 'a'** |
| ----------- | ------------- |
| **STATE 0** | STATE 2       |
| **STATE 1** | STATE 3       |
| **STATE 2** | STATE 3       |
| **STATE 3** | STATE 3       | -->

| **STATE** | **INPUT ('a'=0 and 'b'=1)** | **NEXT STATE ** |
| --------- | --------------------------- | --------------- |
| 0         | 0                           | 2               |
| 1         | 0                           | 3               |
| 2         | 0                           | 3               |
| 3         | 0                           | 3               |
| 0         | 1                           | 3               |
| 1         | 1                           | 3               |
| 2         | 1                           | 1               |
| 3         | 1                           | 3               |
