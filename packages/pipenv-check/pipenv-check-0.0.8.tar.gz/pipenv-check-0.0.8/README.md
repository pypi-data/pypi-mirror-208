# pipenv-check

Moved the color_print and BColors class, which were defined inside the main function, outside the main function to increase the readability of the code.

An error occurred when you tried to directly convert the result of subprocess.check_output(["pip", "list", "--format=json"]) to JSON. Since this output is a byte array, you must first convert this output to a character array. This was accomplished with decode('utf-8') .

At the same time, this operation may result in any errors (for example, if pip is not found or returns an error). Therefore, I enclosed this code in a try-except block and informed the user when the error occurred and terminated the program.

After calling the ThreadPool's close method, we also called the join method. This waits for all threads to complete and provides more predictable program behavior.