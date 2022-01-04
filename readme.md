# ![Icon](static/favicon.ico) Personal Finance Management System    

This project is a simulator to resemble one's bank account transactions and withdrawls.
<br />
The following languages and technologies are used in this project:
<br />
<br />
 **Back end:**
* Python
* SQL

**Front end:**
* HTM
* CSS
* JavaScript

<br />

## How it works
Similar to a bank account page, a user can login to their account on the login page. 
If one does not already have an account, they can create a new account using the register page.
Once a user is logged in, they can access various account functionality, such as viewing their account history, adding transactions, adding money, and more.

### Viewing account history
On the home page of one's account, a summary/history of the user's transactions is displayed.
This includes all transactions added (money going out of the account) and money added to the account (such as income).
Each transaction includes a "Name" field, an "Amount" field, and a "Date Added" field where each transaction is fetched from the database using SQL.

### Adding transactions
On the "Add Item" page, a user can add a transaction (money going out of the account) to their account.
The user is prompted to enter a "Name" and "Amount" for each transaction they add. 
The date field is automatically inserted according to Greenwich Mean Time.
If the fields are incorrectly entered or one is missing, the user is again prompted to enter a correct transaction.

### Adding money to account
On the "Add Money To Account" page, a user can enter any income they have.
This type of transaction is automatically given the name "Income" and the date field is automatically inserted according to Greenwich Mean Time.
If the amount field is incorrectly entered, the user is again prompted to enter a correct transaction.

<hr>
Feel free to try this out! Let me know if you have any suggestions. I am open to feedback and making improvements :)
This is my first project attempt at backend/frontend programming.
