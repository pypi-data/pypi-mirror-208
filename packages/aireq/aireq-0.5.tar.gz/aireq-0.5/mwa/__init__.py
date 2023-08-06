def pal():
    s="""<h1>Palindrome Checker</h1>
<p>Enter a word or phrase to check if it's a palindrome:</p>
<form onsubmit="checkPalindrome(event)">
    <input type="text" id="input1" required>
    <button type="submit">Check</button>
</form>
<div id="result"></div>
<script>
    function checkPalindrome(event) {
        event.preventDefault();
        let str = document.getElementById("input1").value.toLowerCase().replace(/\W/g, '');
        let reversedStr = str.split('').reverse().join('');
        if (str === reversedStr) {
            document.getElementById("result").innerHTML = `Yes, the word/phrase "${str}" is a palindrome!`;
        } else {
            document.getElementById("result").innerHTML = `No, the word/phrase "${str}" is not a palindrome.`;
        }
    }
</script>"""
    return s

def fib():
    s="""<form id="fib-form">
    <label for="number">Generate Fibonacci sequence up to:</label>
    <input type="number" id="number" name="number" required>
    <button type="submit">Generate</button>
  </form>

  <!-- JavaScript code to handle the form submission -->
  <script>
    function fibonacci(number) {
      const sequence = [0, 1];
      for (let i = 2; i <= number; i++) {
        const prev1 = sequence[i - 1];
        const prev2 = sequence[i - 2];
        sequence.push(prev1 + prev2);
      }
      return sequence;
    }

    const form = document.getElementById('fib-form');
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const numberInput = document.getElementById('number');
      const number = parseInt(numberInput.value);
      const fibSequence = fibonacci(number);
      alert(`Fibonacci sequence up to ${number}: ${fibSequence.join(', ')}`);
    });
  </script>
"""
    return s
def cal():
    s="""<!-- HTML code with a form input and a button to submit -->
<form id="calc-form">
  <input type="number" id="num1" name="num1" required>
  <select id="operator" name="operator" required>
    <option value="+">+</option>
    <option value="-">-</option>
    <option value="*">*</option>
    <option value="/">/</option>
  </select>
  <input type="number" id="num2" name="num2" required>
  <button type="submit">Calculate</button>
</form>

<!-- JavaScript code to handle the form submission -->
<script>
  const form = document.getElementById('calc-form');
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const num1Input = document.getElementById('num1');
    const num2Input = document.getElementById('num2');
    const operatorInput = document.getElementById('operator');
    const num1 = parseFloat(num1Input.value);
    const num2 = parseFloat(num2Input.value);
    const operator = operatorInput.value;
    let result;
    switch (operator) {
      case '+':
        result = num1 + num2;
        break;
      case '-':
        result = num1 - num2;
        break;
      case '*':
        result = num1 * num2;
        break;
      case '/':
        result = num1 / num2;
        break;
      default:
        result = 'Invalid operator';
    }
    alert(`Result: ${result}`);
  });
</script>
"""
    return s

def val():
  s="""<!DOCTYPE html>
<html>
<head>
  <title>Email and Password Validation</title>
</head>
<body>
  <h1>Email and Password Validation</h1>
  <form id="myForm">
    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required><br><br>
    <label for="password">Password:</label>
    <input type="password" id="password" name="password" required><br><br>
    <input type="submit" value="Submit">
  </form>

  <script>
    const form = document.getElementById("myForm");
    const email = document.getElementById("email");
    const password = document.getElementById("password");

    form.addEventListener("submit", function(event) {
      // Prevent form submission
      event.preventDefault();

      // Validate email
      if (!isValidEmail(email.value)) {
        alert("Please enter a valid email address");
        return;
      }

      // Validate password
      if (!isValidPassword(password.value)) {
        alert("Password must be at least 8 characters long");
        return;
      }

      // If both email and password are valid, submit form
      alert("Form submitted successfully");
      form.submit();
    });

    function isValidEmail(email) {
      // Regular expression for email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    }

    function isValidPassword(password) {
      // Password must be at least 8 characters long
      return password.length >= 8;
    }
  </script>
</body>
</html>
"""
  return s
