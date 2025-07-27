' Comprehensive interpreter stress test

print "=== STARTING TEST ==="

' --- Variables and Math ---
var a = 5
var b = 3
var c = a + b * 2 - (a ^ 2) / 5
var d = a mod b
print "Math results: "; c; " and MOD result: "; d

' --- INPUT ---
print "Enter a number:"
input userNumber

' --- IF / ELSEIF / ELSE ---
if userNumber < 0 then
    print "You entered a negative number."
elseif userNumber = 0 then
    print "You entered zero."
else
    print "You entered a positive number."
endif

' --- ARRAY TEST ---
dim myArray(1 to 5)
for i = 1 to 5
    myArray(i) = i * i
next

print "Array Contents:"
for i = 1 to 5
    print "myArray("; i; ") = "; myArray(i)
next

' --- WHILE LOOP ---
var count = 1
print "While loop counting to 5:"
while count <= 5
    print "Count = "; count
    count = count + 1
wend

' --- FOR LOOP with STEP ---
print "For loop backwards from 10 to 1:"
for i = 10 to 1 step -1
    print i;
next
print

' --- FUNCTION TEST ---
function Fibonacci(n)
    if n <= 1 then
        result = n
    else
        result = Fibonacci(n - 1) + Fibonacci(n - 2)
    endif
end function

print "Fibonacci sequence up to 10:"
for i = 0 to 10
    print "Fib("; i; ") = "; Fibonacci(i)
next

' --- NESTED CONTROL STRUCTURES ---
print "Nested IF inside FOR loop:"
for i = 1 to 10
    if i mod 2 = 0 then
        print i; " is even"
    else
        print i; " is odd"
    endif
next

' --- Combined math and array indexing ---
dim mathTest(1 to 3)
mathTest(1) = 2 ^ 3
mathTest(2) = (10 + 5) * 2
mathTest(3) = 100 mod 7

print "Math test array:"
for i = 1 to 3
    print "mathTest("; i; ") = "; mathTest(i)
next

print "=== END OF TEST ==="
