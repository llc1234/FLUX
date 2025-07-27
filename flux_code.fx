string name = ""
int age = 19 + 19
float height = 1.66
bool running = true


function add(int num1, int num2)
    return num1 + num2
end function


function multiplay(int num1, int num2)
    return num1 * num2
end function


function some_math(int how)
    for i = 0 in how
        print << "row: " << i << "\n"

        print << " - add       " << add(i, 5) << "\n"
        print << " - multiplay " << multiplay(i, 5) << "\n\n"
    end for


    int i1 = 354 * 434 + 22
    int i2 = 3533

    float p1 = 43434
    float p2 = 13434
    float p3 = 12234
    float p4 = 65434
    float p5 = 44111

    p1 += p1 + p1 + i1
    p1 += p1 + p2 + i2
    p1 += p2 + p2 + i1
    p2 += p3 + p3 + i2
    p3 += p5 + p5 + i1
    p4 += p4 + p5 + i2

    print << "p1: " << p1 << "\n"
    print << "p2: " << p2 << "\n"
    print << "p3: " << p3 << "\n"
    print << "p4: " << p4 << "\n"
    print << "p5: " << p5 << "\n"
end function


function some_while()
    int i = 0

    while running
        i += 1
        if i == 1000
            print << "out off while loop" << "\n"
            running = false
        end if
    end while
    
    i = 0

    while (i < 10)
        print << "looping: " << i << "\n"
        i += 1
    end while
end function


function edite_strings(string nam)
    string new_string = nam[0:-1]

    new_string += "1"
    new_string += "2"
    new_string += "3"
    new_string += "4"
    new_string += "5"

    print << new_string << "\n"
end function

function test_if_and_else()
    int i = 1

    if i == 5
        print << "i is 5\n"
    elif i > 5
        print << "is higher then 5\n"
    elif i < 5
        print << "is lower then 5\n"
    end if
end function


name = input << "What is ur name> "

print << "hello " << name << "\n"
print << ((5 + 5) * 2) / 2 << "\n"

print << add(100, 100) << "\n"

print << "------ test for loop ------\n"
some_math(10)

print << "------ test while loop ------\n"
some_while()

print << "------ test string ------\n"
edite_strings("1234567890")

print << "------ test if and else ------\n"
test_if_and_else()
