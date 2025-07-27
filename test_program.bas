dim arr(1 to 3) as Integer
arr(1) = 5
arr(2) = 10
arr(3) = 15

print "Array contents:"
for i = 1 to 3
    print arr(i);
next
print

if arr(1) > 0 then
    print "First element is positive"
else
    print "First element is not positive"
endif

print "Enter a number:"
input num
sum = 0
for i = 1 to num
    sum = sum + i
next
print "Sum of 1 to "; num; " is "; sum

function square(x)
    result = x * x
end function

print "Square of "; num; " is "; square(num)
